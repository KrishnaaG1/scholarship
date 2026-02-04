import streamlit as st
import pandas as pd
from datetime import datetime
from textblob import TextBlob
import textstat

st.set_page_config(page_title="Smart Scholarship System", layout="centered")

st.title("🎓 Smart Scholarship Eligibility & Essay Evaluation System")

# ---------------- STUDENT DETAILS ----------------

st.header("Student Details")

name = st.text_input("Student Name")

cgpa = st.number_input("CGPA", 0.0, 10.0, step=0.1)

income = st.number_input("Annual Family Income (₹)", min_value=0)

category = st.selectbox("Category", ["General", "OBC", "SC", "ST"])

attendance = st.slider("Attendance (%)", 0, 100, 75)

hosteller = st.selectbox("Hosteller", ["Yes", "No"])

scheme = st.selectbox(
    "Scholarship Scheme",
    ["Merit Based", "Merit + Means", "Need Based"]
)

# ---------------- ESSAY ----------------

st.header("Scholarship Essay")

essay = st.text_area("Paste Essay Here (Minimum 150 words)", height=200)

# ---------------- EVALUATION ----------------

if st.button("Evaluate Scholarship"):

    # ---------- ELIGIBILITY SCORING ----------

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

    st.subheader("📊 Academic & Financial Evaluation")

    st.write(f"Score: {score}/100")

    if score >= threshold:
        st.success("Academically Eligible ✅")
    else:
        st.error("Academically Not Eligible ❌")

    # ---------- ESSAY ANALYSIS ----------

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
    st.write(f"Readability Score: {round(readability,2)}")
    st.write(f"Keyword Relevance: {relevance}")
    st.write(f"Essay Score: {essay_score}/100")

    if essay_score >= 60:
        st.success("Essay Quality: Good ✅")
    else:
        st.warning("Essay Quality: Needs Improvement ⚠")

    # ---------- FINAL DECISION ----------

    final_score = (score + essay_score) / 2

    st.subheader("🎯 Final Scholarship Decision")

    st.write(f"Combined Score: {round(final_score,2)}")

    if final_score >= 65:
        st.success("🎉 SCHOLARSHIP APPROVED")
        final_status = "Approved"
    else:
        st.error("❌ SCHOLARSHIP REJECTED")
        final_status = "Rejected"

    # ---------- DOCUMENT CHECKLIST ----------

    st.subheader("📄 Required Documents")

    st.write("""
    • Income Certificate  
    • CGPA Marksheet  
    • Attendance Proof  
    • Aadhaar  
    • Bank Passbook  
    """)

    if reasons:
        st.subheader("⚠ Issues Found")
        for r in reasons:
            st.write("•", r)

    # ---------- SAVE TO CSV ----------

    record = {
        "Name": name,
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

    st.info("Application saved to applications.csv successfully.")


st.subheader("📥 Download Applications Data")

try:
    df = pd.read_csv("applications.csv")
    st.download_button(
        label="Download applications.csv",
        data=df.to_csv(index=False),
        file_name="applications.csv",
        mime="text/csv"
    )
except:
    st.write("No applications yet.")
