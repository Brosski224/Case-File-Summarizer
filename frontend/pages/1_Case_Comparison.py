import streamlit as st
import requests
import io
import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

# Backend URL
BACKEND_URL = "http://127.0.0.1:5000/summarize"

st.title("📚 Case Comparison Tool")
st.markdown("""
Upload **two or more case PDFs** below.  
The app will summarize each case and compute **how similar they are** using semantic embeddings.
""")

uploaded_files = st.file_uploader("Upload multiple PDFs", type=["pdf"], accept_multiple_files=True)

if uploaded_files and len(uploaded_files) >= 2:
    st.info(f"📁 {len(uploaded_files)} files uploaded.")
    if st.button("Compare Cases"):
        with st.spinner("Processing and comparing cases... ⏳"):
            summaries = []
            names = []

            for file in uploaded_files:
                try:
                    file_bytes = file.read()
                    files = {'file': (file.name, io.BytesIO(file_bytes), 'application/pdf')}
                    data = {'mode': 'quick', 'model_choice': 'gemini'}
                    response = requests.post(BACKEND_URL, files=files, data=data, timeout=150)
                    if response.status_code == 200:
                        rjson = response.json()
                        summary_text = rjson.get("summary", "")
                        try:
                            parsed = json.loads(summary_text)
                            summaries.append(parsed.get("case_summary", summary_text))
                        except Exception:
                            summaries.append(summary_text)
                        names.append(file.name)
                    else:
                        st.error(f"Failed to summarize {file.name}: {response.text}")
                except Exception as e:
                    st.error(f"Error with {file.name}: {e}")

            if len(summaries) >= 2:
                model = SentenceTransformer("all-MiniLM-L6-v2")
                embeddings = model.encode(summaries)
                sim_matrix = cosine_similarity(embeddings)

                st.subheader("📊 Case Similarity Matrix")
                st.dataframe(
                    data=np.round(sim_matrix * 100, 2),
                    use_container_width=True
                )

                st.markdown("_(Values are percentage similarity between cases.)_")

                for i in range(len(names)):
                    for j in range(i + 1, len(names)):
                        st.markdown(
                            f"**{names[i]} ↔ {names[j]}:** {sim_matrix[i][j]*100:.2f}% similar"
                        )
else:
    st.warning("Please upload **at least two case files** to compare.")
