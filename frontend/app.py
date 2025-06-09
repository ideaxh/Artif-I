import streamlit as st
from utils.transfer_utils import parse_transfer_command, normalize_albanian_name, perform_transfer
from utils.leftover_utils import leftover_transfer_handler
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.forecasting_utils import summarize_forecast
from backend.config.budget_forecasting.budget_forecasting import ForecastingModel
import matplotlib.pyplot as plt 

LEFTOVER_AMOUNT = 150.0
LEFTOVER_CURRENCY = "EUR"
# --- Session Setup ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "transfer_mode" not in st.session_state:
    st.session_state.transfer_mode = False

# --- Header ---
st.set_page_config(page_title="Banking Assistant", page_icon="💬", layout="centered")
st.markdown("<h2 style='text-align: center;'>👋 Hi, I'm RAI</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>What can I help you with today?</p>", unsafe_allow_html=True)

# --- Action Buttons ---
with st.container():
    st.markdown("<div style='max-width: 300px; margin: auto;'>", unsafe_allow_html=True)  # center container & set max width

    if st.button("Show My Transactions", key="btn1"):
        st.session_state.transfer_mode = False
        st.session_state.chat_history.append(("user", "Show my transactions"))
        st.session_state.chat_history.append(("bot", "Here are your last 5 transactions..."))

    if st.button("Help Me Transfer Money", key="btn2"):
        st.session_state.transfer_mode = True
        st.session_state.chat_history.append(("user", "Help me transfer money"))
        st.session_state.chat_history.append(("bot", "Certainly! How much money do you want to transfer and to whom?"))

    if st.button("View Credit Score", key="btn3"):
        st.session_state.transfer_mode = False
        st.session_state.chat_history.append(("user", "View credit score"))
        st.session_state.chat_history.append(("bot", "Your current credit score is 768."))

    if st.button("Leftover Money Transfer", key="btn4"):
        st.session_state.transfer_mode = "leftover"
        st.session_state.chat_history.append(("user", "Leftover Money Transfer"))
        st.session_state.chat_history.append(("bot", f"You have {LEFTOVER_AMOUNT} {LEFTOVER_CURRENCY} left. Do you want to transfer to your savings account?"))

    if st.button("Forecast Future Spendings", key="btn5"):
        st.session_state.transfer_mode = "forecast"
        st.session_state.chat_history.append(("user", "Forecast Future Spendings"))
        try:
            csv_path = 'C:\\Users\\arbru\\OneDrive\\Desktop\\RAI\\Artif-I\\backend\\datasets\\final\\final_expenses_dataset.csv'

            model = ForecastingModel()
            df = model.load_data(csv_path)
            monthly = model.resample_monthly(df)
            forecast = model.train_and_forecast(monthly)

            summary = summarize_forecast(forecast)
            fig_forecast_only, ax = plt.subplots(figsize=(10, 4))
            forecast.plot(ax=ax, marker='o', color='darkorange', label='Forecast')
            ax.set_title("6-Month Expense Forecast")
            ax.set_xlabel("Months")
            ax.set_ylabel("Amount (EUR)")
            ax.legend()
            ax.grid(True)

            summary = summarize_forecast(forecast)

            # Show summary and plot
            st.subheader("Forecast Summary")
            st.markdown(summary)

            st.subheader("Forecast (Next 6 Months Only)")
            st.pyplot(fig_forecast_only)

        except Exception as e:
            st.session_state.chat_history.append(("bot", f"Something went wrong during forecasting: {e}"))


    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

# --- Chat Input ---
st.markdown("### Chat with Me")
user_message = st.chat_input("Type or say something...")

# --- Response Logic ---
def get_bot_response(user_input):
    if st.session_state.transfer_mode == "leftover":
        result = leftover_transfer_handler(user_input, LEFTOVER_AMOUNT, LEFTOVER_CURRENCY)
        if result.startswith("How much exactly would"):
            return result  # Ask again for specific input
        st.session_state.transfer_mode = False
        return result

    elif st.session_state.transfer_mode:  # Only handles general transfers
        details = parse_transfer_command(user_input)
        print(f"Details {details}")
        if details:
            details['recipient'] = normalize_albanian_name(details['recipient'])
            st.session_state.transfer_mode = False
            return perform_transfer(details['amount'], details['currency'], details['recipient'])
        else:
            return "I don't uderstand your transfer request. Could you please ask again?"

    # Other general cases
    user_input = user_input.lower()
    if "balance" in user_input:
        return "Your balance is $1,234.56."
    elif "credit score" in user_input:
        return "Your credit score is currently 768."
    elif "qoja" in user_input or "dërgo" in user_input:
        return "Please click the *Help Me Transfer Money* button to begin a trsnafer."
    else:
        return "I'm here to help with transactions, transfers, and credit scores!"

# --- Handle Message ---
if user_message:
    st.session_state.chat_history.append(("user", user_message))
    bot_reply = get_bot_response(user_message)
    st.session_state.chat_history.append(("bot", bot_reply))

# --- Display Chat ---
for sender, message in st.session_state.chat_history:
    st.chat_message(sender).markdown(message)
