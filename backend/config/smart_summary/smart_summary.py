import pandas as pd
from datetime import datetime

# Load your original CSV
df = pd.read_csv("/workspace/ai-hackathon-va/backend/datasets/expense_data_1.csv", parse_dates=["Date"])

# Normalize relevant columns (basic cleanup in-memory)
df["Category"] = df["Category"].str.lower().str.strip()
df["Income/Expense"] = df["Income/Expense"].str.lower().str.strip()

def get_amount_spent(category, date_str):
    try:
        query_date = datetime.strptime(date_str, "%B %d, %Y").date()
    except ValueError:
        return "Invalid date format. Use 'Month day, year' like 'March 1, 2022'."

    df["OnlyDate"] = df["Date"].dt.date
    filtered = df[
        (df["Category"].str.lower() == category.lower()) &
        (df["OnlyDate"] == query_date) &
        (df["Income/Expense"].str.lower() == "expense")
    ]

    total = filtered["Amount"].sum()
    return f"You spent {total} on {category} on {query_date}."

if __name__ == "__main__":
    while True:
        query = input("\nAsk your expense question (or type 'exit'): ").strip()
        if query.lower() == "exit":
            break

        # Improved parsing:
        if "how much did i spend on" in query.lower():
            try:
                # Extract category between "spend on" and "on <date>"
                # Example: "How much did I spend on food on March 1, 2022?"
                parts = query.lower().split("how much did i spend on")[1].strip().rsplit(" on ", 1)
                category = parts[0].strip()
                date_str = parts[1].strip().rstrip("?")
                print(get_amount_spent(category, date_str))
            except Exception as e:
                print("Sorry, I couldn't understand that. Try: 'How much did I spend on food on March 1, 2022?'")
        else:
            print("Try something like: 'How much did I spend on food on March 1, 2022?'")


# Sample interaction loop
if __name__ == "__main__":
    while True:
        query = input("\nAsk your expense question (or type 'exit'): ")
        if query.lower() == "exit":
            break

        # Simple pattern: "how much did i spend on CATEGORY on DATE?"
        if "how much did i spend on" in query:
            try:
                parts = query.lower().split(" on ")
                category = parts[1].split(" on ")[0].strip()
                date_str = parts[-1].strip().rstrip("?")
                print(get_amount_spent(category, date_str))
            except:
                print("Sorry, I couldn't understand that. Try: 'How much did I spend on food on March 1, 2022?'")
        else:
            print("Try something like: 'How much did I spend on food on March 1, 2022?'")
