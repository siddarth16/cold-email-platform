import streamlit as st
import openai
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pandas as pd
import os

# Load secret key
openai.api_key = st.secrets["OPENAI_API_KEY"]

st.set_page_config(page_title="Cold Email Platform", page_icon="📧")
st.title("📧 Cold Email Generator & Sender")

st.sidebar.title("📂 Bulk Personalization")
bulk_mode = st.sidebar.checkbox("Enable CSV Upload")

if not bulk_mode:
    st.subheader("✏️ Describe your campaign")
    product = st.text_area("🧾 Product/Service Description")
    audience = st.text_input("🎯 Target audience")
    tone = st.selectbox("🗣️ Tone", ["Formal", "Friendly", "Casual", "Persuasive"])
    cta = st.text_input("📣 Call to Action (e.g., Book a call)")

    if st.button("Generate Email"):
        with st.spinner("Generating..."):
            prompt = f"""Write a cold email for:
Product: {product}
Target Audience: {audience}
Tone: {tone}
CTA: {cta}
Keep it short and engaging."""
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400
            )
            email_text = response['choices'][0]['message']['content']
            st.session_state.generated_email = email_text

        st.subheader("📩 Generated Email")
        st.text_area("Edit before sending", value=email_text, height=250, key="edited_email")

else:
    uploaded = st.sidebar.file_uploader("Upload CSV (Name, Email, Company)", type=["csv"])
    if uploaded:
        df = pd.read_csv(uploaded)
        st.dataframe(df.head())

        subject_template = st.text_input("✍️ Subject Line (use {Name}, {Company})", value="Let's work together, {Name}")
        body_template = st.text_area("📨 Email Body Template (use {Name}, {Company})", height=250,
            value="Hi {Name},\n\nI came across {Company} and wanted to reach out...")

        if st.button("Generate Emails"):
            st.subheader("📧 Personalized Drafts")
            for i, row in df.iterrows():
                subject = subject_template.format(**row)
                body = body_template.format(**row)
                st.markdown(f"**To:** {row['Email']}  
**Subject:** {subject}  
```
{body}
```")

# Sending section
with st.expander("📤 Send Email"):
    sender_email = st.text_input("Your Gmail")
    app_password = st.text_input("App Password (Gmail App)", type="password")
    recipient = st.text_input("Recipient Email")
    subject = st.text_input("Subject Line")
    content = st.text_area("Email Content", value=st.session_state.get("edited_email", ""), height=200)

    if st.button("Send Now"):
        try:
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = recipient
            msg['Subject'] = subject
            msg.attach(MIMEText(content, "plain"))

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(sender_email, app_password)
                server.send_message(msg)
            st.success("✅ Email sent!")
        except Exception as e:
            st.error(f"Failed: {e}")
