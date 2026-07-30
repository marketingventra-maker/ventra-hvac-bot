import streamlit as st
import requests
import json
import re
from groq import Groq

# Page Configuration
st.set_page_config(page_title="Ventra HVAC Assistant", page_icon="🤖")
st.title("Ventra HVAC Customer Support")

# Groq API Client Setup
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# EmailJS REST API Dispatch Function
def send_emailjs_lead(lead_data):
    url = "https://api.emailjs.com/api/v1.0/email/send"
    payload = {
        "service_id": "service_5wnjb08",
        "template_id": "template_qrc9e94",
        "user_id": "LYQZmBd9qgVMA3_-Q",
        "template_params": {
            "firstName": lead_data.get("firstName", ""),
            "lastName": lead_data.get("lastName", ""),
            "email": lead_data.get("email", ""),
            "phone": lead_data.get("phone", ""),
            "service": lead_data.get("service", ""),
            "city": lead_data.get("city", ""),
            "street": lead_data.get("street", "Booked via AI Chatbot"),
            "app": lead_data.get("app", ""),
            "postalCode": lead_data.get("postalCode", "N/A"),
            "message": lead_data.get("message", "Lead collected automatically by Ventra AI Chatbot.")
        }
    }
    headers = {'Content-Type': 'application/json'}
    try:
        res = requests.post(url, data=json.dumps(payload), headers=headers)
        return res.status_code == 200
    except Exception as e:
        print(f"EmailJS Error: {e}")
        return False

# Detailed System Prompt with Automation Trigger Tag
SYSTEM_PROMPT = """
You are "Ventra Bot", the official, friendly, and highly professional AI Customer Support & Booking Representative for Ventra HVAC.
Your primary goal is to provide accurate information about Ventra HVAC services, current promotional pricing, service coverage, and to actively collect booking details from interested clients.

---

### 1. CORE BRAND & VALUE PROPOSITION
- **Company Name:** Ventra HVAC
- **Core Focus:** Professional HVAC, Duct & Home Air System Cleaning across Canadian homes.
- **Key Benefits:** Clinical cleanliness, commercial-grade equipment, certified elite technicians, transparent pricing with NO hidden fees, comprehensive warranty coverage.

---

### 2. SERVICES & PROMOTIONAL PRICING (Residential Offers)
1. **Air Duct Cleaning (Central Ventilation System):** Regular $349.99 | Promo: **$249.99** (Includes free J-Panel Brushing)
2. **Furnace Cleaning:** Regular $139.99 | Promo: **$99.99**
3. **A.C Coils Cleaning:** Regular $159.99 | Promo: **$129.99**
4. **A.C Condenser Cleaning:** Regular $139.99 | Promo: **$99.99**
5. **Dryer Vent Cleaning:** Regular $149.99 | Promo: **$99.99**
6. **Air Exchanger Cleaning:** Regular $159.99 | Promo: **$129.99**
7. **Exhaust Fan Cleaning:** Regular $24.99 | Promo: **$19.99**
8. **Central Vacuum Cleaning:** Regular $199.99 | Promo: **$149.99**
9. **Bird Nest Removal & Guard Installation:** Flat **$149.99**

---

### 3. SERVICE COVERAGE AREAS
Ajax, Alliston, Aurora, Barrie, Beamsville, Belleville, Bolton, Bowmanville, Bracebridge, Bradford, Brantford, Brockville, Caledonia, Cambridge, Chatham, Cobourg, Collingwood, Cornwall, East Gwillimbury, Fergus, Fort Erie, Georgetown, Goderich, Gravenhurst, GTA, Guelph, Hamilton, and surrounding Ontario areas.

---

### 4. IN-CHAT BOOKING & LEAD COLLECTION FLOW
When a user wants to book or get a quote, step-by-step collect:
1. Full Name (Split into First & Last Name)
2. Phone Number
3. Email Address
4. Service Required
5. City / Location Address

CRITICAL INSTRUCTION FOR FINAL BOOKING STEP:
As soon as you have collected the minimum required info (First Name, Phone, Email, Service, and City), thank the client naturally in your message AND append a JSON trigger block at the very end of your response in this EXACT format:

[BOOKING_DATA: {"firstName": "John", "lastName": "Doe", "email": "john@example.com", "phone": "1234567890", "service": "Air Duct Cleaning", "city": "Toronto", "street": "123 Main St", "postalCode": "M5V 2T6", "message": "Preferred morning slot"}]

Do not forget to append [BOOKING_DATA: ...] when lead info is complete!
"""

# Initializing Chat History
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "assistant",
            "content": "👋 **Hello! Welcome to Ventra HVAC Support.**\n\nHow can I help you today? Select a quick option below or type your question:\n\n1. 💰 **What are your current promotional offers & prices?**\n2. 📅 **How do I book a cleaning appointment?**\n3. 📍 **Which areas in Ontario do you service?**"
        }
    ]

# Display history screen (Filtering out internal JSON tags)
for msg in st.session_state.messages:
    if msg["role"] != "system":
        clean_content = re.sub(r'\[BOOKING_DATA:.*?\]', '', msg["content"]).strip()
        with st.chat_message(msg["role"]):
            st.markdown(clean_content)

# Prompt Trigger Handler
prompt = None

# Show Quick Action Buttons at start
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

# Standard chat input box
chat_input_val = st.chat_input("Aap ka kya sawal hai?")
if chat_input_val:
    prompt = chat_input_val

# Process Response
if prompt:
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
        
        # Check if booking data trigger is present in AI response
        booking_match = re.search(r'\[BOOKING_DATA:\s*(\{.*?\})\s*\]', reply)
        if booking_match:
            try:
                data_dict = json.loads(booking_match.group(1))
                # Send email via EmailJS API
                email_sent = send_emailjs_lead(data_dict)
                if email_sent:
                    st.toast("✅ Booking details dispatched directly to Ventra HVAC team!")
            except Exception as err:
                print("JSON Parsing error:", err)

        # Render display message (clean without JSON tag)
        clean_reply = re.sub(r'\[BOOKING_DATA:.*?\]', '', reply).strip()
        st.markdown(clean_reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()
