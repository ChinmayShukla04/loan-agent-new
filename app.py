import streamlit as st
from openai import OpenAI
from kyc import verify_kyc
from credit import get_credit_score
from eligibility import check_eligibility
import re
from dotenv import load_dotenv
import os
load_dotenv()

# 🔐 Secure API Key
client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

st.title("🤖 AI Loan Agent")

# =========================
# 🔍 DATA EXTRACTION FUNCTIONS
# =========================

def extract_pan(text):
    match = re.search(r"[A-Z]{5}[0-9]{4}[A-Z]", text)
    return match.group() if match else None

def extract_aadhaar(text):
    match = re.search(r"\b\d{12}\b", text)
    return match.group() if match else None

def extract_income(text):
    match = re.search(r"(income\s*is\s*|salary\s*is\s*)(\d+)", text.lower())
    return int(match.group(2)) if match else None

def extract_name(text):
    if len(text.split()) <= 3 and all(word.isalpha() for word in text.split()):
        return text
    return None

# =========================
# 🧠 SESSION MEMORY
# =========================

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hello! I am your AI Loan Assistant.\n\nHow can I help you today?"
        }
    ]

if "user_data" not in st.session_state:
    st.session_state.user_data = {}

# =========================
# 🔄 RESET BUTTON
# =========================

if st.button("🔄 Start New Application"):
    st.session_state.messages = []
    st.session_state.user_data = {}
    st.rerun()

# =========================
# 💬 SHOW CHAT HISTORY
# =========================

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# =========================
# 🧾 USER INPUT
# =========================

user_input = st.chat_input("Type your message...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.chat_message("user").write(user_input)

    # =========================
    # 🧠 EXTRACT DATA
    # =========================

    data = st.session_state.user_data

    pan = extract_pan(user_input.upper())
    aadhaar = extract_aadhaar(user_input)
    income = extract_income(user_input)
    name = extract_name(user_input)

    if pan:
        data["pan"] = pan

    if aadhaar:
        data["aadhaar"] = aadhaar

    if income:
        data["income"] = income

    if "name" not in data and name:
        data["name"] = name

    # =========================
    # 🤖 AI SYSTEM PROMPT
    # =========================

    system_prompt = f"""
    You are a professional banking loan agent.

    Collected Data:
    {data}

    Instructions:
    - If name is missing → ask name
    - If PAN is missing → ask PAN
    - If Aadhaar is missing → ask Aadhaar
    - If income is missing → ask income
    - If all data is collected → stop asking and wait

    Rules:
    - Ask only one question at a time
    - Be polite and human-like
    - Do not repeat questions
    """

    # =========================
    # 🤖 AI RESPONSE
    # =========================

    with st.chat_message("assistant"):
        with st.spinner("Processing your loan request..."):
            response = client.chat.completions.create(
                model="meta-llama/llama-3-8b-instruct",
                messages=[
                    {"role": "system", "content": system_prompt},
                    *st.session_state.messages
                ]
            )

            bot_reply = response.choices[0].message.content
            st.write(bot_reply)

    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
    # st.chat_message("assistant").write(bot_reply)

    # =========================
    # ⚙️ LOAN PROCESSING LOGIC
    # =========================

    if all(k in data for k in ["name", "pan", "aadhaar", "income"]) and not data.get("done"):

        st.chat_message("assistant").write("⚙️ Processing your application...")

        if not verify_kyc(data["pan"], data["aadhaar"]):
            st.chat_message("assistant").write("❌ KYC Verification Failed")
        else:
            st.chat_message("assistant").write("✅ KYC Verified")

            credit_score = get_credit_score()
            st.chat_message("assistant").write(f"💳 Credit Score: {credit_score}")

            result = check_eligibility(credit_score, data["income"])

            if result == "Approved":
                st.chat_message("assistant").write("🎉 Loan Approved & Sanctioned (Demo)")
            elif result == "Review":
                st.chat_message("assistant").write("⏳ Your application is under review")
            else:
                st.chat_message("assistant").write("❌ Loan Rejected")

        # Mark as processed
        data["done"] = True
