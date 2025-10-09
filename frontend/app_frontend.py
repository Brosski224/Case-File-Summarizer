import streamlit as st
import requests
import io
import json

#  Backend Flask API URL
BACKEND_URL = "http://127.0.0.1:5000/summarize"

#  Page configuration
st.set_page_config(
    page_title=" Case File Summarizer (LLM-Powered)",
    page_icon="⚖️",
    layout="centered"
)

# 🧾 App title and intro
st.title(" Case File Summarizer (LLM-Powered)")
st.markdown("""
Upload a **legal case PDF** and click **Summarize Now ** to get:
- A clean **one-line summary**
- A **structured quick summary**
- Option to **download JSON**
""")

#  File uploader
uploaded_file = st.file_uploader("Upload your case file (PDF)", type=["pdf"])

# If a file is uploaded
if uploaded_file:
    st.success(" File uploaded successfully!")

    #  Summarize button
    if st.button("Summarize Now"):
        with st.spinner("Analyzing and summarizing case file... Please wait "):
            try:
                # Prepare PDF file for backend
                file_bytes = uploaded_file.read()
                files = {
                    'file': (uploaded_file.name, io.BytesIO(file_bytes), 'application/pdf')
                }
                data = {'mode': 'quick'}

                # Send request to backend
                response = requests.post(BACKEND_URL, files=files, data=data, timeout=150)

                #  If backend returns success
                if response.status_code == 200:
                    summary_data = response.json()

                    if "error" in summary_data:
                        st.error(summary_data["error"])
                    else:
                        summary_text = summary_data.get("summary", "")

                        # 🧠 Try to parse JSON
                        try:
                            parsed = json.loads(summary_text)
                        except json.JSONDecodeError:
                            summary_text = summary_text.strip().replace("```json", "").replace("```", "")
                            try:
                                parsed = json.loads(summary_text)
                            except Exception:
                                parsed = {"summary_text": summary_text}

                        #  Generate a one-line summary
                        one_line = f"{parsed.get('case_title', '')} — {parsed.get('final_verdict_or_order', '')}"
                        one_line = one_line.strip().rstrip('.')
                        if one_line:
                            one_line += '.'

                        # 🪄 Display results neatly
                        st.subheader("One-line Summary")
                        st.markdown(one_line)



                        st.subheader("Quick Summary Result")
                        if parsed:
                            for key, value in parsed.items():
                                pretty_key = key.replace("_", " ").title()
                                st.markdown(f"**{pretty_key}:** {value}")
                        else:
                            st.write(summary_text)

                        #  Download JSON button
                        parsed_output = {"one_line_summary": one_line, **parsed}
                        json_str = json.dumps(parsed_output, indent=2, ensure_ascii=False)
                        st.download_button(
                            label=" Download JSON",
                            data=json_str,
                            file_name="case_summary.json",
                            mime="application/json"
                        )

                else:
                    st.error(f"❌ Server error: {response.status_code}")
                    try:
                        st.text(response.text)
                    except Exception:
                        pass

            except requests.exceptions.RequestException as e:
                st.error(f"⚠️ Connection failed: {e}")
            except Exception as e:
                st.error(f"Unexpected error: {e}")

else:
    st.info("👆 Please upload a PDF file to get started.")
