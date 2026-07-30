def send_emailjs_lead(lead_data):
    url = "https://api.emailjs.com/api/v1.0/email/send"
    
    # Matching exact template variables shown in your EmailJS template
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
