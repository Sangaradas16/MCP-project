from collections import defaultdict
from datetime import datetime, timedelta


class PredictionTool:
    def __init__(self, expenses):
        self.expenses = expenses

    def _monthly_series(self):
        monthly_totals = defaultdict(float)
        for exp in self.expenses:
            month_key = exp.date.strftime("%Y-%m")
            monthly_totals[month_key] += exp.amount
        return dict(sorted(monthly_totals.items()))

    def _linear_forecast(self, series: dict):
        if len(series) < 2:
            return sum(series.values()) / len(series) if series else 0.0

        # Simple linear regression
        months = list(range(len(series)))
        values = list(series.values())

        n = len(months)
        sum_x = sum(months)
        sum_y = sum(values)
        sum_xy = sum(x * y for x, y in zip(months, values))
        sum_xx = sum(x * x for x in months)

        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_xx - sum_x * sum_x)
        intercept = (sum_y - slope * sum_x) / n

        next_x = n
        forecast = slope * next_x + intercept
        return max(0.0, forecast)

    def predict_next_month(self):
        series = self._monthly_series()
        history = [{"period": period, "total": round(total, 2)} for period, total in series.items()]

        if not series:
            return {"next_period": "n/a", "forecast": 0.0, "history": history}

        if len(series) < 4:
            forecast_value = sum(series.values()) / len(series)
            next_period = list(series.keys())[-1]
            # Calculate next month
            year, month = map(int, next_period.split('-'))
            if month == 12:
                next_period = f"{year + 1:04d}-01"
            else:
                next_period = f"{year:04d}-{month + 1:02d}"
            return {"next_period": next_period, "forecast": round(forecast_value, 2), "history": history}

        try:
            forecast_value = self._linear_forecast(series)
            next_period = list(series.keys())[-1]
            # Calculate next month
            year, month = map(int, next_period.split('-'))
            if month == 12:
                next_period = f"{year + 1:04d}-01"
            else:
                next_period = f"{year:04d}-{month + 1:02d}"
            return {"next_period": next_period, "forecast": round(forecast_value, 2), "history": history}
        except Exception:
            forecast_value = sum(list(series.values())[-3:]) / 3
            next_period = list(series.keys())[-1]
            year, month = map(int, next_period.split('-'))
            if month == 12:
                next_period = f"{year + 1:04d}-01"
            else:
                next_period = f"{year:04d}-{month + 1:02d}"
            return {"next_period": next_period, "forecast": round(forecast_value, 2), "history": history}
