import sys
import os

# Add backend directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

import streamlit as st
import time
from utils.transfer_utils import parse_transfer_command, normalize_albanian_name, perform_transfer
from utils.leftover_utils import leftover_transfer_handler
from config.smart_summary.smart_summary import get_top_spending_category_last_n_months
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.forecasting_utils import summarize_forecast
from backend.config.budget_forecasting.budget_forecasting import ForecastingModel
import matplotlib.pyplot as plt 

LEFTOVER_AMOUNT = 150.0
LEFTOVER_CURRENCY = "EUR"
USER_NAME = "Arb"
# --- Session Setup ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "transfer_mode" not in st.session_state:
    st.session_state.transfer_mode = False
if "typed_intro" not in st.session_state:
    st.session_state.typed_intro = False

# --- Header ---from config.smart_summary.smart_summary import get_top_spending_category_last_n_months

st.set_page_config(page_title="Banking Assistant", page_icon="💬", layout="centered")

# Dark chat bubble styling
st.markdown("""
    <style>
    .chat-bubble {
        background-color: #2f2f2f;
        padding: 1rem 1.5rem;
        border-radius: 20px;
        width: fit-content;
        max-width: 80%;
        margin: 2rem auto;
        font-size: 18px;
        color: white;
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        line-height: 1.5;
    }
    .st-emotion-cache-ktz07o:active {
            border-color: yellow !important;
            color: yellow !important;
        }
    .st-emotion-cache-ktz07o:hover {
            background-color: yellow !important;
            border-color: yellow !important;
            color: black !important;
        }
    .st-emotion-cache-ktz07o:focus:not(:active) {
    border-color: yellow;
    color: yellow;
}
    .st-emotion-cache-x1bvup:focus-within {
    border-color: yellow !important;
}
    .st-emotion-cache-bm2z3a {
            padding-left:10px;
            padding-right:10px;
            }
    </style>
""", unsafe_allow_html=True)


# Simulate typing inside one bubble
def type_text(text, container, delay=0.035):
    displayed_text = ""
    for char in text:
        displayed_text += char
        container.markdown(f"<div class='chat-bubble'>{displayed_text}</div>", unsafe_allow_html=True)
        time.sleep(delay)

    # if st.button("Show My Transactions", key="btn5"):
    #     st.session_state.transfer_mode = False
    #     st.session_state.chat_history.append(("user", "Show my transactions"))
    #     st.session_state.chat_history.append(("bot", "What transactions would you like to see?"))

# Combine both lines into one string
full_text = f"👋 Hi {USER_NAME}, I'm RAI.\nWhat can I help you with today?"

# Render it only once
chat_area = st.empty()
if not st.session_state.typed_intro:
    type_text(full_text, chat_area)
    st.session_state.typed_intro = True
else:
    # Just display the full text without typing animation
    chat_area.markdown(f"<div class='chat-bubble'>{full_text}</div>", unsafe_allow_html=True)


# Custom button wrapper
st.markdown("""
    <style>
        .custom-button-container {
            display: flex;
            flex-direction: column;
            align-items: flex-start;
            gap: 12px;
            margin-top: 30px;
        }
        .custom-button-container .stButton {
            opacity: 0;
            transform: translateY(10px);
            animation: fadeInUp 0.5s ease forwards;
        }
        .custom-button-container .stButton:nth-child(1) { animation-delay: 0.1s; }
        .custom-button-container .stButton:nth-child(2) { animation-delay: 0.3s; }
        .custom-button-container .stButton:nth-child(3) { animation-delay: 0.5s; }
        .custom-button-container .stButton:nth-child(4) { animation-delay: 0.7s; }

        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .custom-button-container button {
            width: 300px !important;
            text-align: left;
            background-color: #f0f2f6;
            color: #333;
            border: 1px solid #d3d3d3;
            border-radius: 8px;
            padding: 10px 16px;
            font-size: 16px;
            font-weight: 500;
        }
        .custom-button-container button:hover {
            background-color: #e0e4ea;
        }
    </style>
""", unsafe_allow_html=True)

# Container with class
st.markdown("<div class='custom-button-container'>", unsafe_allow_html=True)

# Buttons (appear one after another due to animation delays)
if st.button("Show My Transactions", key="btn1"):
    st.session_state.transfer_mode = False
    st.session_state.chat_history.append(("user", "Show my transactions"))
    st.session_state.chat_history.append(("bot", "What transactions would you like to see?"))

if st.button("Help Me Transfer Money", key="btn2"):
    st.session_state.transfer_mode = True
    st.session_state.chat_history.append(("user", "Help me transfer money"))
    st.session_state.chat_history.append(("bot", "Certainly! How much money do you want to transfer and to whom?"))
    
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
    elif "spend the most on" in user_input:
        if "last 3 months" in user_input:
            return get_top_spending_category_last_n_months(n=3)
        elif "last 6 months" in user_input:
            return get_top_spending_category_last_n_months(n=6)
        else:
            return "Please specify how many months to analyze, like 'last 3 months'."
    else:
        return "I'm here to help with transactions, transfers, and credit scores!"

# --- Handle Message ---
if user_message:
    st.session_state.chat_history.append(("user", user_message))
    bot_reply = get_bot_response(user_message)
    st.session_state.chat_history.append(("bot", bot_reply))

# Display chat history
for sender, message in st.session_state.chat_history:
    if sender == "bot":
        st.chat_message("bot", avatar="assets/raiffeisenlogosq.png").markdown(message)  # Or use a URL to an SVG/PNG
    else:
        st.chat_message(sender).markdown(message)
