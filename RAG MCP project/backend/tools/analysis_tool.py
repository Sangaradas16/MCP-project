from datetime import datetime
from collections import defaultdict
from typing import List, Dict


class AnalysisTool:
    def __init__(self, expenses):
        self.expenses = expenses

    def category_trends(self):
        # Group by category and month
        trends = defaultdict(lambda: defaultdict(float))
        for exp in self.expenses:
            month_key = exp.date.strftime("%Y-%m")
            trends[exp.category][month_key] += exp.amount

        result = {}
        for category, monthly_data in trends.items():
            result[category] = [
                {"period": period, "total": round(total, 2)}
                for period, total in sorted(monthly_data.items())
            ]
        return result

    def anomaly_detection(self):
        # Simple anomaly detection: flag weeks with spending > 2x average
        weekly_totals = defaultdict(float)
        for exp in self.expenses:
            week_key = exp.date.strftime("%Y-%U")
            weekly_totals[week_key] += exp.amount

        if not weekly_totals:
            return []

        all_totals = list(weekly_totals.values())
        avg_spending = sum(all_totals) / len(all_totals)
        std_dev = (sum((x - avg_spending) ** 2 for x in all_totals) / len(all_totals)) ** 0.5

        anomalies = []
        for week, total in weekly_totals.items():
            if std_dev > 0:
                z_score = (total - avg_spending) / std_dev
                if z_score > 2.0:
                    anomalies.append({
                        "period": week,
                        "amount": round(total, 2),
                        "z_score": round(z_score, 2)
                    })
        return anomalies
