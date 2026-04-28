import os
import logging

logger = logging.getLogger("expense_assistant")

try:
    from llama_cpp import Llama
except ImportError:
    Llama = None

try:
    import openai
except ImportError:
    openai = None


class AIResponder:
    def __init__(self):
        self.local_model_path = os.environ.get("LOCAL_LLM_MODEL_PATH")
        self.openai_api_key = os.environ.get("OPENAI_API_KEY")

    def generate(self, user_question: str, tool_outputs: dict) -> str:
        """Generate AI response using tool outputs and context"""
        system_prompt = (
            "You are a helpful expense tracking assistant. Use the provided tool outputs to give "
            "accurate, concise answers. If tool outputs contain relevant data, incorporate it naturally. "
            "If no relevant tool outputs exist, provide helpful guidance about using the expense tracker."
        )

        # Build context from tool outputs
        context_parts = []
        if tool_outputs.get("expenses"):
            expenses = tool_outputs["expenses"]
            total_amount = sum(exp["amount"] for exp in expenses)
            context_parts.append(f"User has {len(expenses)} total expenses worth ${total_amount:.2f}")

        if tool_outputs.get("prediction"):
            pred = tool_outputs["prediction"]
            context_parts.append(f"Predicted spending for {pred.get('next_period', 'next period')}: ${pred.get('forecast', 0):.2f}")

        if tool_outputs.get("category_trends"):
            trends = tool_outputs["category_trends"]
            top_trends = sorted(trends.items(), key=lambda x: len(x[1]), reverse=True)[:2]
            trend_summary = ", ".join([f"{cat}: {len(data)} entries" for cat, data in top_trends])
            context_parts.append(f"Spending trends: {trend_summary}")

        if tool_outputs.get("anomalies"):
            anomalies = tool_outputs["anomalies"]
            context_parts.append(f"Detected {len(anomalies)} spending anomalies")

        if tool_outputs.get("recent_expenses"):
            recent = tool_outputs["recent_expenses"]
            recent_total = sum(exp["amount"] for exp in recent)
            context_parts.append(f"Recent expenses: {len(recent)} items totaling ${recent_total:.2f}")

        context_text = " | ".join(context_parts) if context_parts else "No specific tool data available"

        full_prompt = f"{system_prompt}\n\nUser Question: {user_question}\nTool Context: {context_text}\n\nProvide a helpful response:"

        # Try local LLM first
        if self.local_model_path and Llama is not None:
            try:
                model = Llama(model_path=self.local_model_path)
                response = model(
                    full_prompt,
                    max_tokens=200,
                    temperature=0.3,
                    stop=["\n\n", "User:", "Assistant:"]
                )
                return response["choices"][0]["text"].strip()
            except Exception as exc:
                logger.warning("Local LLM failed: %s", exc)

        # Try OpenAI as fallback
        if self.openai_api_key and openai is not None:
            try:
                client = openai.OpenAI(api_key=self.openai_api_key)
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Question: {user_question}\nContext: {context_text}"}
                    ],
                    max_tokens=200,
                    temperature=0.3,
                )
                return response.choices[0].message.content.strip()
            except Exception as exc:
                logger.warning("OpenAI fallback failed: %s", exc)

        # Use fallback response generation
        return self._generate_fallback_response(user_question, tool_outputs)

    def _generate_fallback_response(self, user_question: str, tool_outputs: dict) -> str:
        """Generate fallback response when AI models are not available"""

        # Handle conversational queries
        question_lower = user_question.lower().strip()

        # Greeting responses
        if any(word in question_lower for word in ["hello", "hi", "hey", "greetings"]):
            return "Hello! I'm your expense tracking assistant. I can help you manage your expenses, analyze spending patterns, make predictions, and answer questions about your financial data. What would you like to know?"

        # How are you responses
        if "how are you" in question_lower or "how do you do" in question_lower:
            return "I'm doing well, thank you! I'm here to help you with your expense tracking. I can show you spending trends, make predictions, or help you manage your expenses. What can I help you with today?"

        # Thank you responses
        if any(word in question_lower for word in ["thank", "thanks"]):
            return "You're welcome! I'm here whenever you need help with your expenses. Feel free to ask me about trends, predictions, or any expense-related questions."

        # Help responses
        if any(word in question_lower for word in ["help", "what can you do", "what do you do"]):
            return "I can help you with:\n• Managing expenses (add, edit, delete)\n• Analyzing spending trends and patterns\n• Predicting future expenses\n• Detecting unusual spending\n• Answering questions about your financial data\n\nTry asking: 'What are my spending trends?' or 'Predict next month expenses'"

        # Check for prediction data
        if tool_outputs.get("prediction"):
            prediction = tool_outputs["prediction"]
            return (
                f"Based on your spending history, I predict you'll spend "
                f"${prediction.get('forecast', 0):.2f} {prediction.get('next_period', 'next month')}."
            )

        # Check for analysis data
        if tool_outputs.get("category_trends") or tool_outputs.get("anomalies"):
            trends = tool_outputs.get("category_trends", {})
            anomalies = tool_outputs.get("anomalies", [])

            response = "Here's what I found in your expenses:\n"
            if trends:
                top_categories = sorted(trends.items(),
                                      key=lambda x: sum(item.get('total', 0) for item in x[1]),
                                      reverse=True)[:3]
                response += f"• Top spending categories: {', '.join([cat for cat, _ in top_categories])}\n"

            if anomalies:
                response += f"• Detected {len(anomalies)} unusual spending patterns\n"

            response += "Check the analytics section for detailed charts."
            return response

        # Check for expense data
        if tool_outputs.get("expenses"):
            expenses = tool_outputs["expenses"]
            total_amount = sum(exp["amount"] for exp in expenses)
            categories = set(exp["category"] for exp in expenses)

            return (
                f"You have {len(expenses)} expenses totaling ${total_amount:.2f} "
                f"across {len(categories)} categories. "
                f"You can view details, add new expenses, or run analytics using the dashboard."
            )

        # Check for recent expenses
        if tool_outputs.get("recent_expenses"):
            recent = tool_outputs["recent_expenses"]
            total_recent = sum(exp["amount"] for exp in recent)

            return (
                f"Your {len(recent)} most recent expenses total ${total_recent:.2f}. "
                f"I can help you analyze trends, predict future spending, or manage your expenses."
            )

        # Default helpful response
        return (
            "I'm your expense tracking assistant! I can help you:\n"
            "• View and manage your expenses\n"
            "• Analyze spending patterns and trends\n"
            "• Predict future expenses\n"
            "• Detect unusual spending\n\n"
            "Try asking questions like 'How much did I spend this month?' or "
            "'What are my spending trends?' or add some expenses to get started!"
        )
