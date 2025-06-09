import sys
import os

# Add backend directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

import streamlit as st
from utils.transfer_utils import parse_transfer_command, normalize_albanian_name, perform_transfer
from utils.leftover_utils import leftover_transfer_handler
from config.smart_summary.smart_summary import get_top_spending_category_last_n_months

LEFTOVER_AMOUNT = 150.0
LEFTOVER_CURRENCY = "EUR"
# --- Session Setup ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "transfer_mode" not in st.session_state:
    st.session_state.transfer_mode = False

# --- Header ---from config.smart_summary.smart_summary import get_top_spending_category_last_n_months

st.set_page_config(page_title="Banking Assistant", page_icon="💬", layout="centered")
st.markdown("<h2 style='text-align: center;'>👋 Hi, I'm RAI</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>What can I help you with today?</p>", unsafe_allow_html=True)

# --- Action Buttons ---
with st.container():
    st.markdown("<div style='max-width: 300px; margin: auto;'>", unsafe_allow_html=True)  # center container & set max width

    if st.button("Show My Transactions", key="btn1"):
        st.session_state.transfer_mode = False
        st.session_state.chat_history.append(("user", "Show my transactions"))
        st.session_state.chat_history.append(("bot", "What transactions would you like to see?"))

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
    st.chat_message(sender).markdown(message)
