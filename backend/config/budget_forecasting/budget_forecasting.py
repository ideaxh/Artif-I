import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA

class ForecastingModel:

    def __init__(self, arima_order=(1, 1, 1)):
        self.arima_order = arima_order

    @staticmethod
    def load_data(csv_path):
        if not csv_path.endswith(".csv"):
            raise ValueError(f"File is not csv : {csv_path}")
        return pd.read_csv(csv_path)

    @staticmethod
    def resample_monthly(df):
        df['date'] = pd.to_datetime(df['date'])
        return df.resample('M', on='date')['amount'].sum()

    def train_and_forecast(self, monthly_expenses):
        model = ARIMA(monthly_expenses, order=self.arima_order)
        results = model.fit()
        return results.forecast(steps=6)

    @staticmethod
    def plot_forecast(history, forecast):
        plt.figure(figsize=(10, 5))
        history.plot(label='Historical', marker='o')
        forecast.plot(label='Forecast', marker='o', linestyle='--', color='orange')
        plt.title('Monthly Expenses Forecast')
        plt.xlabel('Date')
        plt.ylabel('Amount (EUR)')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()


if __name__ == "__main__":
    csv_path = 'C:\\Users\\arbru\\OneDrive\\Desktop\\RAI\\Artif-I\\backend\\datasets\\final\\final_expenses_dataset.csv'
    model = ForecastingModel()

    df = model.load_data(csv_path)
    monthly = model.resample_monthly(df)
    forecast = model.train_and_forecast(monthly)

    print("Next 6 months forecast:")
    for date, value in forecast.items():
        print(f"{date.date()}   {value:.2f} EUR")

    model.plot_forecast(monthly, forecast)
