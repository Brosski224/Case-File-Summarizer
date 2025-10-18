import streamlit as st
import requests
import io
import json

# Backend URL
BACKEND_URL = "http://127.0.0.1:5000/summarize"

st.set_page_config(
    page_title="Case File Summarizer (LLM-Powered)",
    page_icon="⚖️",
    layout="wide"
)

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Summarizer", "Case Comparison"])

if page == "Summarizer":
    st.title("Case File Summarizer (LLM-Powered)")
    st.markdown("""
    Upload a **legal case PDF** and click **Summarize Now** to get:
    - A clean **one-line summary**
    - A **structured quick summary**
    - Option to **download JSON**
    - Maintain a **history of past summaries**
    """)

    # Initialize session state
    if "history" not in st.session_state:
        st.session_state.history = []

    col_left, col_right = st.columns([2, 1])

    with col_left:
        uploaded_file = st.file_uploader("Upload your case file (PDF)", type=["pdf"])

        if uploaded_file:
            st.success("✅ File uploaded successfully!")

            colA, colB = st.columns([3, 1])
            with colA:
                model_choice = st.selectbox("Select Model", ["Gemini", "Groq"], index=0)
            with colB:
                summarize_clicked = st.button("Summarize Now")

            if summarize_clicked:
                with st.spinner("Analyzing and summarizing case file... Please wait ⏳"):
                    try:
                        file_bytes = uploaded_file.read()
                        files = {
                            'file': (uploaded_file.name, io.BytesIO(file_bytes), 'application/pdf')
                        }
                        data = {'mode': 'quick', 'model_choice': model_choice.lower()}

                        response = requests.post(BACKEND_URL, files=files, data=data, timeout=150)

                        if response.status_code == 200:
                            summary_data = response.json()

                            if "error" in summary_data:
                                st.error(summary_data["error"])
                            else:
                                summary_text = summary_data.get("summary", "")
                                model_used = summary_data.get("model_used", "Unknown")

                                try:
                                    parsed = json.loads(summary_text)
                                except json.JSONDecodeError:
                                    summary_text = summary_text.strip().replace("```json", "").replace("```", "")
                                    try:
                                        parsed = json.loads(summary_text)
                                    except Exception:
                                        parsed = {"summary_text": summary_text}

                                one_line = f"{parsed.get('case_title', '')} — {parsed.get('final_verdict_or_order', '')}"
                                one_line = one_line.strip().rstrip('.')
                                if one_line:
                                    one_line += '.'

                                # Save to history
                                st.session_state.history.append({
                                    "title": parsed.get("case_title", uploaded_file.name),
                                    "model": model_used,
                                    "summary": one_line,
                                    "parsed": parsed
                                })

                                st.subheader("🧩 One-line Summary")
                                st.markdown(one_line)

                                st.subheader(f"📄 Quick Summary Result ({model_used})")
                                for key, value in parsed.items():
                                    pretty_key = key.replace("_", " ").title()
                                    st.markdown(f"**{pretty_key}:** {value}")

                                parsed_output = {"one_line_summary": one_line, **parsed}
                                json_str = json.dumps(parsed_output, indent=2, ensure_ascii=False)
                                st.download_button(
                                    label="📥 Download JSON",
                                    data=json_str,
                                    file_name="case_summary.json",
                                    mime="application/json"
                                )

                        else:
                            st.error(f"❌ Server error: {response.status_code}")
                            st.text(response.text)

                    except requests.exceptions.RequestException as e:
                        st.error(f"⚠️ Connection failed: {e}")
                    except Exception as e:
                        st.error(f"Unexpected error: {e}")

        else:
            st.info("👆 Please upload a PDF file to get started.")

    with col_right:
        st.subheader("🕓 Summary History")

        if st.session_state.history:
            for i, entry in enumerate(reversed(st.session_state.history), 1):
                with st.expander(f"{i}. {entry['title']} ({entry['model']})"):
                    st.markdown(f"**One-line Summary:** {entry['summary']}")
                    for key, value in entry["parsed"].items():
                        pretty_key = key.replace("_", " ").title()
                        st.markdown(f"**{pretty_key}:** {value}")
        else:
            st.markdown("_No summaries yet. Upload a file to begin._")

elif page == "Case Comparison":
    st.title("Case Comparison Tool")
    st.markdown("""
    Upload **two PDFs** to compare them.
    The app will summarize each, then show **how they are similar and how they differ**.
    """)

    uploaded_files = st.file_uploader("Upload case files", type=["pdf"], accept_multiple_files=True)
    model_choice = st.selectbox("Select Model", ["Gemini", "Groq"], index=0)

    if uploaded_files and len(uploaded_files) >= 2:
        if st.button("Compare Cases"):
            with st.spinner("Summarizing and comparing... Please wait."):
                summaries = []
                for file in uploaded_files:
                    file_bytes = file.read()
                    files = {'file': (file.name, io.BytesIO(file_bytes), 'application/pdf')}
                    data = {'mode': 'quick', 'model_choice': model_choice.lower()}

                    res = requests.post(f"http://127.0.0.1:5000/summarize", files=files, data=data)
                    if res.status_code == 200:
                        result = res.json()
                        summaries.append(result.get("summary", ""))
                    else:
                        st.error(f"Error summarizing {file.name}: {res.text}")

                # Now compare them
                compare_res = requests.post(
                    "http://127.0.0.1:5000/compare-cases",
                    json={"summaries": summaries, "model_choice": model_choice.lower()},
                    timeout=300
                )

                if compare_res.status_code == 200:
                    comparisons = compare_res.json().get("comparisons", [])
                    for comp in comparisons:
                        st.markdown(f"### ⚖️ {comp.get('pair', 'Case Pair')}")
                        st.markdown("**🔹 Similarities:**")
                        for sim in comp.get("similarities", []):
                            st.markdown(f"- {sim}")
                        st.markdown("**🔸 Differences:**")
                        for diff in comp.get("differences", []):
                            st.markdown(f"- {diff}")
                        st.markdown("---")
                else:
                    st.error(f"Comparison failed: {compare_res.text}")
    else:
        st.info("Please upload two PDFs to compare.")

