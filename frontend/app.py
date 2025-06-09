import sys
import os

# Add backend directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

import streamlit as st
from config.smart_summary.smart_summary import get_top_spending_category_last_n_months

st.set_page_config(page_title="Banking Assistant", page_icon="💬", layout="centered")

st.markdown("<h2 style='text-align: center;'>👋 Hi, I'm RAI</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>What can I help you with today?</p>", unsafe_allow_html=True)

# --- ACTION CARDS ---
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📄 Show My Transactions"):
        st.session_state.chat_history = st.session_state.get("chat_history", [])
        st.session_state.chat_history.append(("user", "Show my transactions"))
        st.session_state.chat_history.append(("bot", "What transactions would you like to see?"))

with col2:
    if st.button("💸 Help Me Transfer Money"):
        st.session_state.chat_history = st.session_state.get("chat_history", [])
        st.session_state.chat_history.append(("user", "Help me transfer money"))
        st.session_state.chat_history.append(("bot", "Sure! Who would you like to send money to?"))

with col3:
    if st.button("📊 View Credit Score"):
        st.session_state.chat_history = st.session_state.get("chat_history", [])
        st.session_state.chat_history.append(("user", "View credit score"))
        st.session_state.chat_history.append(("bot", "Your current credit score is 768."))

st.markdown("---")

# --- CHAT SECTION ---
st.markdown("### 💬 Chat with Me")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

user_message = st.chat_input("Type or say something...")

def get_bot_response(user_input):
    user_input = user_input.lower()
    if "balance" in user_input:
        return "Your balance is $1,234.56."
    elif "transfer" in user_input:
        return "Sure! To whom would you like to transfer funds?"
    elif "credit score" in user_input:
        return "Your credit score is currently 768."
    elif "spend the most on" in user_input:
        if "last 3 months" in user_input:
            return get_top_spending_category_last_n_months(n=3)
        elif "last 6 months" in user_input:
            return get_top_spending_category_last_n_months(n=6)
        else:
            return "Please specify how many months to analyze, like 'last 3 months'."
    else:
        return "I'm here to help with transactions, transfers, and credit scores!"

if user_message:
    st.session_state.chat_history.append(("user", user_message))
    st.session_state.chat_history.append(("bot", get_bot_response(user_message)))

# --- Display chat history ---
for sender, message in st.session_state.chat_history:
    if sender == "user":
        st.chat_message("user").markdown(message)
    else:
        st.chat_message("assistant").markdown(message)
