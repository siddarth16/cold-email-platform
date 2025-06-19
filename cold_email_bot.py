import streamlit as st
import openai
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

# Set OpenAI key from Streamlit secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

st.set_page_config(page_title="Cold Email Bot", page_icon="📧")
st.title("📧 Cold Email Generator")

# Inputs
product = st.text_area("🧾 Describe your product or service")
audience = st.text_input("🎯 Target audience")
tone = st.selectbox("🗣️ Tone", ["Formal", "Friendly", "Casual", "Persuasive"])
cta = st.text_input("📣 Call to action (e.g., 'Book a call')")

if st.button("Generate Email"):
    with st.spinner("Generating..."):
        prompt = f"""
        Write a cold email for:

        Product/Service: {product}
        Target Audience: {audience}
        Tone: {tone}
        Call to Action: {cta}

        Keep it short, clear, and engaging.
        """
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400
        )
        email_text = response['choices'][0]['message']['content']
        st.session_state.generated_email = email_text

    st.subheader("✉️ Generated Email")
    st.text_area("Edit the email if needed", value=email_text, height=300, key="edited_email")

# Optional Email Sending
with st.expander("📤 Send This Email"):
    sender_email = st.text_input("Your Gmail")
    app_password = st.text_input("App Password (Google)", type="password")
    recipient = st.text_input("Recipient Email")
    subject = st.text_input("Subject")

    if st.button("Send Email"):
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient
        msg['Subject'] = subject
        msg.attach(MIMEText(st.session_state.get("edited_email", ""), "plain"))

        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(sender_email, app_password)
                server.send_message(msg)
            st.success("✅ Email sent successfully!")
        except Exception as e:
            st.error(f"Failed to send: {e}")
