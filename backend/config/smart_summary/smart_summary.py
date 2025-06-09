import os
import pandas as pd
from pathlib import Path
from datetime import datetime

def get_top_spending_category_last_n_months(n=6):
    # Load your CSV
    cwd = Path(__file__).parent.resolve()
    relative_path = "../../datasets/final/cleaned_expense_data.csv"
    full_path = (cwd / relative_path).resolve()
    # path_with_forward_slashes = full_path.as_posix()

    print(f"Full path: {full_path}")
    df = pd.read_csv(full_path, parse_dates=["date"])
    # Filter data for last `n` months
    today = pd.Timestamp.today()
    cutoff_date = today - pd.DateOffset(months=n)
    df_nmonths = df[df['date'] >= cutoff_date]

    # Group by category and sum amount
    category_sums = df_nmonths.groupby('category')['amount'].sum()

    # Find the category with max spending
    top_category = category_sums.idxmax()
    top_category_amount = category_sums.max()

    # Filter data for only top category
    df_top_cat = df_nmonths[df_nmonths['category'] == top_category]

    # Group by location and sum amount within top category
    location_sums = df_top_cat.groupby('location')['amount'].sum()

    # Get top 3 locations
    top_locations = location_sums.sort_values(ascending=False).head(3).index.tolist()

    # Format output with newline
    output = (
        f"In the last {n} months, you spent the most on {top_category}, "
        f"totaling €{top_category_amount:.2f}.\n"
        f"Your top locations were:\n" + "\n".join(f"- {loc}" for loc in top_locations)
    )

    return output
