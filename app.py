import streamlit as st
import requests
import json
import re
from groq import Groq

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Ventra HVAC Assistant",
    page_icon="🤖",
    layout="centered"
)

st.title("Ventra HVAC Customer Support")

# ==========================================
# 2. GROQ CLIENT INITIALIZATION
# ==========================================
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# ==========================================
# 3. EMAILJS REST API DISPATCH FUNCTION
# ==========================================
def send_emailjs_lead(lead_data):
    url = "https://api.emailjs.com/api/v1.0/email/send"
    
    # Payload exact match with EmailJS Template variables & Web Form
    payload = {
        "service_id": "service_5wnjb08",
        "template_id": "template_qrc9e94",
        "user_id": "LYQZmBd9qgVMA3_-Q",
        "template_params": {
            "title": "AI Chatbot",
            "firstName": lead_data.get("firstName", "Client"),
            "lastName": lead_data.get("lastName", ""),
            "email": lead_data.get("email", "N/A"),
            "phone": lead_data.get("phone", "N/A"),
            "service": lead_data.get("service", "N/A"),
            "street": lead_data.get("street", "Booked via AI Chatbot"),
            "app": lead_data.get("app", ""),
            "city": lead_data.get("city", "N/A"),
            "postalCode": lead_data.get("postalCode", "N/A"),
            "message": lead_data.get("message", "Lead collected via Ventra AI Assistant.")
        }
    }
    headers = {'Content-Type': 'application/json'}
    try:
        res = requests.post(url, data=json.dumps(payload), headers=headers)
        if res.status_code == 200:
            return True, "Success"
        else:
            return False, f"EmailJS Error {res.status_code}: {res.text}"
    except Exception as e:
        return False, str(e)

# ==========================================
# 4. SYSTEM PROMPT & BUSINESS LOGIC
# ==========================================
SYSTEM_PROMPT = """
You are "Ventra Bot", the official AI Customer Support & Booking Representative for Ventra HVAC.
Your primary goal is to provide accurate information about Ventra HVAC services, promotional pricing, service coverage, and to actively collect booking details.

---

### 1. SERVICES & PROMOTIONAL PRICING
1. Air Duct Cleaning: Promo $249.99 (Reg. $349.99)
2. Furnace Cleaning: Promo $99.99 (Reg. $139.99)
3. A.C Coils Cleaning: Promo $129.99 (Reg. $159.99)
4. A.C Condenser Cleaning: Promo $99.99 (Reg. $139.99)
5. Dryer Vent Cleaning: Promo $99.99 (Reg. $149.99)
6. Air Exchanger Cleaning: Promo $129.99 (Reg. $159.99)
7. Exhaust Fan Cleaning: Promo $19.99 (Reg. $24.99)
8. Central Vacuum Cleaning: Promo $149.99 (Reg. $199.99)
9. Bird Nest Removal & Guard Installation: Flat $149.99

---

### 2. SERVICE COVERAGE AREAS
Ajax, Alliston, Aurora, Barrie, Beamsville, Belleville, Bolton, Bowmanville, Bracebridge, Bradford, Brantford, Brockville, Caledonia, Cambridge, Chatham, Cobourg, Collingwood, Cornwall, East Gwillimbury, Fergus, Fort Erie, Georgetown, Goderich, Gravenhurst, GTA, Guelph, Hamilton, and surrounding Ontario areas.

---

### 3. MANDATORY INSTRUCTION FOR FINAL BOOKING STEP
Whenever a client provides booking info (First Name, Phone, Email, Service, and City/Address), summarize details politely AND attach the hidden JSON tag at the VERY END of your message.

MANDATORY TAG FORMAT:
[BOOKING_DATA: {"firstName": "ClientFirstName", "lastName": "", "email": "client@email.com", "phone": "12345678", "service": "Service Name", "city": "City Name"}]
"""

# ==========================================
# 5. INITIALIZE SESSION STATE
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "assistant",
            "content": "👋 **Hello! Welcome to Ventra HVAC Support.**\n\nHow can I help you today? Select a quick option below or type your question:"
        }
    ]

# ==========================================
# 6. DISPLAY CHAT HISTORY (Cleaned JSON Tag)
# ==========================================
for msg in st.session_state.messages:
    if msg["role"] != "system":
        clean_content = re.sub(r'\[BOOKING_DATA:.*?\]', '', msg["content"], flags=re.DOTALL).strip()
        with st.chat_message(msg["role"]):
            st.markdown(clean_content)

# ==========================================
# 7. QUICK ACTION BUTTONS
# ==========================================
prompt = None

if len(st.session_state.messages) <= 2:
    st.markdown("**Quick Options:**")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("💰 View Pricing"):
            prompt = "What are your current promotional prices and packages?"
    with col2:
        if st.button("📅 Book Service"):
            prompt = "I want to book an HVAC cleaning service."
    with col3:
        if st.button("📍 Check Areas"):
            prompt = "Which cities do you service in Ontario?"

# ==========================================
# 8. CHAT INPUT & RESPONSE LOGIC
# ==========================================
chat_input_val = st.chat_input("Type your message here...")
if chat_input_val:
    prompt = chat_input_val

if prompt:
    # Append User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # Generate AI Response
    with st.chat_message("assistant"):
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=st.session_state.messages,
            temperature=0.2
        )
        reply = completion.choices[0].message.content
        
        # Check if response contains JSON lead tag
        booking_match = re.search(r'\[BOOKING_DATA:\s*(\{.*?\})\s*\]', reply, flags=re.DOTALL)
        if booking_match:
            try:
                data_dict = json.loads(booking_match.group(1))
                email_sent, status_msg = send_emailjs_lead(data_dict)
                if email_sent:
                    st.toast("✅ Booking notification sent to service@ventrahvac.ca!")
                else:
                    st.error(f"⚠️ Email Sending Failed: {status_msg}")
            except Exception as err:
                st.error(f"JSON Parsing Error: {err}")

        # Hide JSON tag from Chat Interface
        clean_reply = re.sub(r'\[BOOKING_DATA:.*?\]', '', reply, flags=re.DOTALL).strip()
        st.markdown(clean_reply)
        
        # Store full conversation in state
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()
