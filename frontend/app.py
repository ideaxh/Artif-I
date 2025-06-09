import streamlit as st
from utils.transfer_utils import parse_transfer_command, normalize_albanian_name, perform_transfer
from utils.leftover_utils import leftover_transfer_handler

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
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("📄 Show My Transactions"):
        st.session_state.transfer_mode = False
        st.session_state.chat_history.append(("user", "Show my transactions"))
        st.session_state.chat_history.append(("bot", "Here are your last 5 transactions..."))

with col2:
    if st.button("💸 Help Me Transfer Money"):
        st.session_state.transfer_mode = True
        st.session_state.chat_history.append(("user", "Help me transfer money"))
        st.session_state.chat_history.append(("bot", "Sigurisht! Sa para dëshironi të transferoni dhe kujt?"))

with col3:
    if st.button("📊 View Credit Score"):
        st.session_state.transfer_mode = False
        st.session_state.chat_history.append(("user", "View credit score"))
        st.session_state.chat_history.append(("bot", "Your current credit score is 768."))

with col4:
    if st.button("📊 Leftover Money Transfer"):
        st.session_state.transfer_mode = "leftover"
        st.session_state.chat_history.append(("user", "Leftover Money Transfer"))
        st.session_state.chat_history.append(("bot", f"Ke {LEFTOVER_AMOUNT} {LEFTOVER_CURRENCY} të mbetura. Sa dëshiron të transferosh?"))

st.markdown("---")

# --- Chat Input ---
st.markdown("### 💬 Chat with Me")
user_message = st.chat_input("Type or say something...")

# --- Response Logic ---
def get_bot_response(user_input):
    if st.session_state.transfer_mode:
        details = parse_transfer_command(user_input)
        if details:
            details['recipient'] = normalize_albanian_name(details['recipient'])
            st.session_state.transfer_mode = False
            return perform_transfer(details['amount'], details['currency'], details['recipient'])
        else:
            return "Nuk mund të kuptoj kërkesën për transfer. Mund të shkruash sërish?"
    elif st.session_state.transfer_mode == "leftover":
        result = leftover_transfer_handler(user_input, LEFTOVER_AMOUNT, LEFTOVER_CURRENCY)
        if result.startswith("Sa saktësisht"):
            return result  # Ask again for specific input
        st.session_state.transfer_mode = False
        return result

    user_input = user_input.lower()
    if "balance" in user_input:
        return "Your balance is $1,234.56."
    elif "credit score" in user_input:
        return "Your credit score is currently 768."
    elif "qoja" in user_input or "dërgo" in user_input:
        return "Ju lutem klikoni butonin 💸 *Help Me Transfer Money* për të nisur një transferim."
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
