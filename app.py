import streamlit as st
from groq import Groq

st.set_page_config(page_title="Ventra HVAC Assistant", page_icon="🤖")
st.title("Ventra HVAC Customer Support")

# Groq API Client Setup
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

SYSTEM_PROMPT = """You are a professional customer support representative for Ventra HVAC operating across Canada. 
Services: Air Duct, Furnace, A.C Coils, Dryer Vent, Air Exchanger, Exhaust Fan, A.C Condenser, Central Vacuum Cleaning, and $499.99 Complete Package.
Be polite, professional, concise, and helpful."""

# Chat history state initialize karen
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

# History screen par dikhayen
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

# User ka input handle karen
if prompt := st.chat_input("Aap ka kya sawal hai?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # Groq API Call
    with st.chat_message("assistant"):
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=st.session_state.messages,
            temperature=0.7
        )
        reply = completion.choices[0].message.content
        st.write(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})