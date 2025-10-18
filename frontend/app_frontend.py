import streamlit as st
import requests
import io
import json

# ==============================
# 🔧 CONFIGURATION
# ==============================
BACKEND_URL = "http://127.0.0.1:5000/summarize"

st.set_page_config(
    page_title="Case File Summarizer (LLM-Powered)",
    page_icon="⚖️",
    layout="wide"
)

# ==============================
# 💡 HEADER
# ==============================
st.title("⚖️ Case File Summarizer (LLM-Powered)")
st.markdown("""
Upload a **legal case PDF** and click **Summarize Now** to generate:
- A concise **one-line summary**
- A detailed **structured quick summary**
- Option to **download the JSON result**
- Automatic **summary history**
""")

# ==============================
# 🧠 INITIALIZE SESSION
# ==============================
if "history" not in st.session_state:
    st.session_state.history = []

# ==============================
# 📂 FILE UPLOAD & MAIN LOGIC
# ==============================
col_left, col_right = st.columns([2, 1])

with col_left:
    uploaded_file = st.file_uploader("Upload your case file (PDF)", type=["pdf"])

    if uploaded_file:
        st.success("✅ File uploaded successfully!")

        colA, colB = st.columns([3, 1])
        with colA:
            model_choice = st.selectbox("Select Model", ["Gemini", "Groq"], index=0)
        with colB:
            summarize_clicked = st.button("⚡ Summarize Now")

        if summarize_clicked:
            with st.spinner("Analyzing and summarizing case file... Please wait ⏳"):
                try:
                    # Prepare request
                    files = {
                        'file': (uploaded_file.name, io.BytesIO(uploaded_file.read()), 'application/pdf')
                    }
                    data = {'mode': 'quick', 'model_choice': model_choice.lower()}

                    # Send request
                    response = requests.post(BACKEND_URL, files=files, data=data, timeout=150)

                    # ==============================
                    # 📬 HANDLE RESPONSE
                    # ==============================
                    if response.status_code == 200:
                        summary_data = response.json()

                        if "error" in summary_data:
                            st.error(summary_data["error"])
                        else:
                            summary_text = summary_data.get("summary", "")
                            model_used = summary_data.get("model_used", model_choice)

                            # Try parsing JSON response
                            parsed = {}
                            try:
                                parsed = json.loads(summary_text)
                            except json.JSONDecodeError:
                                cleaned = summary_text.strip().replace("```json", "").replace("```", "")
                                try:
                                    parsed = json.loads(cleaned)
                                except Exception:
                                    parsed = {"summary_text": cleaned}

                            # Construct one-line summary
                            case_title = parsed.get("case_title", uploaded_file.name)
                            verdict = parsed.get("final_verdict_or_order", "")
                            one_line = f"{case_title} — {verdict}".strip().rstrip('.') + '.'

                            # Save history
                            st.session_state.history.append({
                                "title": case_title,
                                "model": model_used,
                                "summary": one_line,
                                "parsed": parsed
                            })

                            # ==============================
                            # 🧾 DISPLAY RESULTS
                            # ==============================
                            st.subheader("One-line Summary")
                            st.markdown(one_line)

                            st.subheader(f"Detailed Summary ({model_used})")
                            for key, value in parsed.items():
                                pretty_key = key.replace("_", " ").title()
                                st.markdown(f"**{pretty_key}:** {value}")

                            # Download JSON
                            parsed_output = {"one_line_summary": one_line, **parsed}
                            st.download_button(
                                label="Download JSON",
                                data=json.dumps(parsed_output, indent=2, ensure_ascii=False),
                                file_name="case_summary.json",
                                mime="application/json"
                            )
                    else:
                        st.error(f"❌ Server Error: {response.status_code}")
                        st.text(response.text)

                except requests.exceptions.RequestException as e:
                    st.error(f"⚠️ Connection failed: {e}")
                except Exception as e:
                    st.error(f"Unexpected error: {e}")
    else:
        st.info("Please upload a PDF file to get started.")

# ==============================
# 🕘 SUMMARY HISTORY
# ==============================
with col_right:
    st.subheader("Summary History")

    if st.session_state.history:
        for i, entry in enumerate(reversed(st.session_state.history), 1):
            with st.expander(f"{i}. {entry['title']} ({entry['model']})"):
                st.markdown(f"**One-line Summary:** {entry['summary']}")
                for key, value in entry["parsed"].items():
                    pretty_key = key.replace("_", " ").title()
                    st.markdown(f"**{pretty_key}:** {value}")
    else:
        st.markdown("_No summaries yet. Upload a file to begin._")
