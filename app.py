import os
import streamlit as st

from services.vector_store import VectorStore
from services.ingest import ingest_document
from services.qa_engine import answer_question

st.set_page_config(page_title="DocQuery", page_icon="📄")

st.title("📄 DocQuery")
st.write("Ask questions about your PDF or TXT documents.")

os.makedirs("documents", exist_ok=True)

if "vector_store" not in st.session_state:
    st.session_state.vector_store = VectorStore()

if "processed_files" not in st.session_state:
    st.session_state.processed_files = []

uploaded_file = st.file_uploader(
    "Upload a PDF or TXT file",
    type=["pdf", "txt"]
)

if uploaded_file is not None:
    file_path = os.path.join("documents", uploaded_file.name)

    with open(file_path, "wb") as file:
        file.write(uploaded_file.getbuffer())

    if st.button("Process Document"):
        try:
            ingest_document(file_path, st.session_state.vector_store)
            if file_path not in st.session_state.processed_files:
                st.session_state.processed_files.append(file_path)
            st.success("Document processed successfully!")
        except Exception as error:
            st.error(f"Could not process the document: {error}")

if st.session_state.processed_files:
    st.sidebar.subheader("Processed Documents")
    for file_path in st.session_state.processed_files:
        st.sidebar.write(os.path.basename(file_path))

question = st.chat_input("Ask a question about your document...")

if question:
    st.chat_message("user").write(question)

    try:
        result = answer_question(
            question,
            st.session_state.vector_store
        )

        st.chat_message("assistant").write(result["answer"])

        if result["sources"]:
            with st.expander("Sources"):
                for source in result["sources"]:
                    st.write(f"Score: {source['score']:.3f}")
                    st.write(source["text"])
    except Exception as error:
        st.error(f"Could not answer the question: {error}")
