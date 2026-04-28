from .context_router import ContextRouter
from ..tools.db_tool import DatabaseTool
from ..tools.analysis_tool import AnalysisTool
from ..tools.prediction_tool import PredictionTool


class MCPAgent:
    def __init__(self, db):
        self.db_tool = DatabaseTool(db)
        self.context_router = ContextRouter()

    def handle(self, query: str):
        """Handle user query using MCP architecture"""
        category = self.context_router.classify(query)
        tool_outputs = {}

        # Always get basic expense data
        expenses = self.db_tool.get_expenses()
        tool_outputs["expenses"] = [
            {
                "id": exp.id,
                "description": exp.description,
                "category": exp.category,
                "amount": exp.amount,
                "date": exp.date.isoformat(),
            }
            for exp in expenses
        ]

        # Route to appropriate tools based on query classification
        if category == "database":
            # Database operations - show expenses
            tool_outputs["database_summary"] = {
                "total_expenses": len(expenses),
                "total_amount": sum(exp.amount for exp in expenses),
                "categories": list(set(exp.category for exp in expenses))
            }

        elif category == "prediction":
            # Prediction operations
            prediction_tool = PredictionTool(expenses)
            prediction = prediction_tool.predict_next_month()
            tool_outputs["prediction"] = prediction

        elif category == "analysis":
            # Analysis operations
            analysis_tool = AnalysisTool(expenses)
            tool_outputs["category_trends"] = analysis_tool.category_trends()
            tool_outputs["anomalies"] = analysis_tool.anomaly_detection()
            tool_outputs["category_summary"] = self.db_tool.category_summary("monthly")
            tool_outputs["monthly_trend"] = self.db_tool.monthly_trend()

        else:
            # General queries - provide overview but let AI assistant handle conversation
            recent_expenses = expenses[-5:]  # Last 5 expenses
            tool_outputs["recent_expenses"] = [
                {
                    "id": exp.id,
                    "description": exp.description,
                    "category": exp.category,
                    "amount": exp.amount,
                    "date": exp.date.isoformat(),
                }
                for exp in recent_expenses
            ]
            # For general queries, return empty string and let AI assistant handle the conversation
            return "", tool_outputs

        return self._generate_response(query, category, tool_outputs), tool_outputs

    def _generate_response(self, query: str, category: str, tool_outputs: dict) -> str:
        """Generate a natural language response based on tool outputs"""

        if category == "database":
            summary = tool_outputs.get("database_summary", {})
            return (
                f"I found {summary.get('total_expenses', 0)} expenses totaling ${summary.get('total_amount', 0):.2f} "
                f"across categories: {', '.join(summary.get('categories', []))}. "
                "You can view, add, update, or delete expenses using the dashboard."
            )

        elif category == "prediction":
            prediction = tool_outputs.get("prediction", {})
            if prediction:
                return (
                    f"Based on your spending patterns, I predict ${prediction.get('forecast', 0):.2f} "
                    f"in expenses for {prediction.get('next_period', 'next month')}.")
            return "I need more expense data to make accurate predictions. Please add some expenses first."

        elif category == "analysis":
            trends = tool_outputs.get("category_trends", {})
            anomalies = tool_outputs.get("anomalies", [])
            summary = tool_outputs.get("category_summary", {})

            response_parts = []

            if trends:
                top_categories = sorted(
                    trends.items(),
                    key=lambda x: sum(item['total'] for item in x[1]),
                    reverse=True,
                )[:3]
                category_strings = [
                    f"{cat} (${sum(item['total'] for item in data):.2f})"
                    for cat, data in top_categories
                ]
                response_parts.append(f"Your top spending categories are: {', '.join(category_strings)}")

            if anomalies:
                response_parts.append(
                    f"I detected {len(anomalies)} unusual spending patterns that might need attention."
                )

            if summary:
                total_by_category = {
                    cat: sum(item['total'] for item in items)
                    for cat, items in summary.items()
                }
                if total_by_category:
                    response_parts.append(
                        f"Monthly breakdown: {', '.join([f'{cat}: ${amt:.2f}' for cat, amt in total_by_category.items()])}"
                    )

            return (
                " ".join(response_parts)
                if response_parts
                else "I've analyzed your expenses. Check the analytics section for detailed charts and trends."
            )

        else:
            recent = tool_outputs.get("recent_expenses", [])
            if recent:
                total_recent = sum(exp["amount"] for exp in recent)
                return (
                    f"Here are your {len(recent)} most recent expenses totaling ${total_recent:.2f}. "
                    "I can also help with predictions, analysis, or managing your expenses."
                )
            return (
                "Welcome to your expense tracker! I can help you manage expenses, run analytics, "
                "make predictions, and detect anomalies. Try asking about your spending patterns "
                "or add some expenses to get started."
            )