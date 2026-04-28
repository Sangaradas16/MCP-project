import re


class ContextRouter:
    """Routes user queries to appropriate MCP tools using keyword and pattern matching"""

    # Enhanced keyword categories with more comprehensive terms
    categories = {
        "database": [
            "add", "update", "delete", "show", "list", "expense", "expenses", "transaction",
            "record", "spending", "cost", "payment", "purchase", "item", "entry",
            "how many", "what expenses", "view", "see", "display", "total"
        ],
        "prediction": [
            "predict", "forecast", "estimate", "future", "next month", "projection",
            "will spend", "expect", "plan", "budget", "coming", "upcoming",
            "how much will", "what will", "forecasting"
        ],
        "analysis": [
            "analysis", "analytics", "trend", "trends", "anomaly", "report", "summary",
            "average", "pattern", "statistics", "chart", "graph", "breakdown",
            "compare", "comparison", "insights", "unusual", "outlier", "anomalies",
            "category", "monthly", "weekly", "yearly", "spending pattern"
        ],
    }

    # Question patterns that indicate specific categories (compiled regex)
    question_patterns = {
        "database": [
            re.compile(r"how many.*expenses?", re.IGNORECASE),
            re.compile(r"what.*expenses?", re.IGNORECASE),
            re.compile(r"show me.*expenses?", re.IGNORECASE),
            re.compile(r"list.*expenses?", re.IGNORECASE),
            re.compile(r"what did i spend", re.IGNORECASE),
            re.compile(r"total.*spend", re.IGNORECASE),
            re.compile(r"how much.*spent", re.IGNORECASE)
        ],
        "prediction": [
            re.compile(r"how much.*next", re.IGNORECASE),
            re.compile(r"what.*next.*month", re.IGNORECASE),
            re.compile(r"predict.*spend", re.IGNORECASE),
            re.compile(r"forecast.*month", re.IGNORECASE),
            re.compile(r"will.*spend", re.IGNORECASE),
            re.compile(r"expect.*spend", re.IGNORECASE)
        ],
        "analysis": [
            re.compile(r"analyze.*spend", re.IGNORECASE),
            re.compile(r"trend.*spend", re.IGNORECASE),
            re.compile(r"anomaly.*spend", re.IGNORECASE),
            re.compile(r"unusual.*spend", re.IGNORECASE),
            re.compile(r"pattern.*spend", re.IGNORECASE),
            re.compile(r"breakdown.*spend", re.IGNORECASE),
            re.compile(r"category.*spend", re.IGNORECASE)
        ]
    }

    @classmethod
    def classify(cls, text: str) -> str:
        """Classify user query into database, prediction, analysis, or general"""
        normalized = text.lower().strip()

        # Priority order: check most specific patterns first
        # 1. Prediction queries
        if any(pattern.search(normalized) for pattern in cls.question_patterns["prediction"]):
            return "prediction"
        if any(keyword in normalized for keyword in ["predict", "forecast", "estimate", "future", "next month", "projection", "will spend", "expect"]):
            return "prediction"

        # 2. Analysis queries
        if any(pattern.search(normalized) for pattern in cls.question_patterns["analysis"]):
            return "analysis"
        if any(keyword in normalized for keyword in ["analysis", "analytics", "trend", "trends", "anomaly", "report", "summary", "average", "pattern", "statistics", "breakdown", "unusual", "outlier", "anomalies", "category"]):
            return "analysis"

        # 3. Database queries (most general, checked last)
        if any(pattern.search(normalized) for pattern in cls.question_patterns["database"]):
            return "database"
        if any(keyword in normalized for keyword in ["show", "list", "expense", "expenses", "transaction", "record", "how many", "what expenses", "view", "see", "display", "total"]):
            return "database"

        # Default to general for conversational queries
        return "general"
