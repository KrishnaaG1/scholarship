import streamlit as st
import pandas as pd
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
import textstat

st.set_page_config(page_title="Smart Scholarship System", layout="centered")

st.title("🎓 Smart Scholarship Eligibility + Essay + Email Automation")

# ================= USER INPUT =================

st.header("Student Details")

name = st.text_input("Student Name")
email = st.text_input("Student Email")

cgpa = st.number_input("CGPA", 0.0, 10.0, step=0.1)
income = st.number_input("Annual Family Income (₹)", min_value=0)
category = st.selectbox("Category", ["General", "OBC", "SC", "ST"])
attendance = st.slider("Attendance (%)", 0, 100, 75)
hosteller = st.selectbox("Hosteller", ["Yes", "No"])

scheme = st.selectbox(
    "Scholarship Scheme",
    ["Merit Based", "Merit + Means", "Need Based"]
)

st.header("Scholarship Essay")
essay = st.text_area("Paste Essay Here (minimum 150 words)", height=200)

# ================= BUTTON =================

if st.button("Evaluate Scholarship"):

    # ================= ACADEMIC SCORING =================

    score = 0
    reasons = []

    # CGPA
    if cgpa >= 9:
        score += 40
    elif cgpa >= 8:
        score += 30
    elif cgpa >= 7:
        score += 20
    else:
        reasons.append("Low CGPA")

    # Income
    if income <= 150000:
        score += 30
    elif income <= 200000:
        score += 20
    else:
        reasons.append("High Income")

    # Attendance
    if attendance >= 85:
        score += 20
    elif attendance >= 75:
        score += 10
    else:
        reasons.append("Low Attendance")

    # Category bonus
    if category in ["SC", "ST"]:
        score += 10

    # Hosteller bonus
    if hosteller == "Yes":
        score += 5

    # Scheme threshold
    if scheme == "Merit Based":
        threshold = 70
    elif scheme == "Merit + Means":
        threshold = 60
    else:
        threshold = 50

    st.subheader("📊 Academic Evaluation")
    st.write(f"Academic Score: {score}/100")

    # ================= ESSAY ANALYSIS =================

    st.subheader("📝 Essay Evaluation")

    word_count = len(essay.split())
    readability = textstat.flesch_reading_ease(essay)

    keywords = ["education", "career", "financial", "future", "support"]
    relevance = sum([1 for k in keywords if k in essay.lower()]) * 10

    essay_score = 0

    if word_count >= 150:
        essay_score += 30
    if readability > 40:
        essay_score += 20

    essay_score += min(relevance, 30)
    essay_score = min(essay_score, 100)

    st.write(f"Word Count: {word_count}")
    st.write(f"Readability: {round(readability,2)}")
    st.write(f"Keyword Score: {relevance}")
    st.write(f"Essay Score: {essay_score}/100")

    # ================= FINAL DECISION =================

    final_score = (score + essay_score) / 2

    st.subheader("🎯 Final Result")
    st.write(f"Combined Score: {round(final_score,2)}")

    if final_score >= 65:
        st.success("🎉 SCHOLARSHIP APPROVED")
        final_status = "Approved"
    else:
        st.error("❌ SCHOLARSHIP REJECTED")
        final_status = "Rejected"

    # ================= DOCUMENT LIST =================

    st.subheader("📄 Required Documents")
    st.write("""
    • Income Certificate  
    • CGPA Marksheet  
    • Attendance Proof  
    • Aadhaar  
    • Bank Passbook  
    """)

    if reasons:
        st.subheader("⚠ Issues")
        for r in reasons:
            st.write("•", r)

    # ================= SAVE TO CSV =================

    record = {
        "Name": name,
        "Email": email,
        "CGPA": cgpa,
        "Income": income,
        "Category": category,
        "Attendance": attendance,
        "Hosteller": hosteller,
        "Scheme": scheme,
        "Academic Score": score,
        "Essay Score": essay_score,
        "Final Score": final_score,
        "Status": final_status,
        "Time": datetime.now()
    }

    df = pd.DataFrame([record])

    try:
        old = pd.read_csv("applications.csv")
        df = pd.concat([old, df])
    except:
        pass

    df.to_csv("applications.csv", index=False)

    st.info("Application saved.")

    # ================= EMAIL AUTOMATION =================

    sender_email = "ikrishnaa12@gmail.com"
    sender_password = "wgvu yppq zfnl safy"

    if final_status == "Approved":
        message = f"""
Dear {name},

Congratulations! 🎉

You have been APPROVED for the scholarship.

Final Score: {round(final_score,2)}

Please prepare the following documents:
Income Certificate
Marksheet
Attendance Proof
Aadhaar
Bank Passbook

Regards,
Scholarship Committee
"""
    else:
        message = f"""
Dear {name},

Thank you for applying.

Unfortunately, you were NOT selected this time.

Final Score: {round(final_score,2)}

You may apply again next year.

Regards,
Scholarship Committee
"""

    try:
        msg = MIMEText(message)
        msg["Subject"] = "Scholarship Application Result"
        msg["From"] = sender_email
        msg["To"] = email

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, email, msg.as_string())
        server.quit()

        st.success("📧 Result email sent successfully!")

    except:
        st.warning("Email could not be sent.")

# ================= CSV DOWNLOAD =================

st.subheader("📥 Download Applications")

try:
    df = pd.read_csv("applications.csv")
    st.download_button(
        "Download applications.csv",
        df.to_csv(index=False),
        "applications.csv",
        "text/csv"
    )
except:
    st.write("No applications yet.")
