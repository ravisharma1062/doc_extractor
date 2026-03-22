import streamlit as st
import fitz  # PyMuPDF
import docx
import io
import google.generativeai as genai

st.set_page_config(page_title="Document Extractor", layout="wide", page_icon="📄")

st.title("📄 Document Text & Metadata Extractor")
st.markdown("Upload a document, extract its content, and use AI to automatically pull out key fields.")

with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input("Gemini API Key", type="password", help="Enter your Gemini API Key. It forms the core of the extraction engine.")
    st.markdown("[Get an API key here](https://aistudio.google.com/app/apikey)")
    
    available_models = ["gemini-1.5-flash", "gemini-pro"]
    if api_key:
        try:
            genai.configure(api_key=api_key)
            fetched_models = [m.name for m in genai.list_models() if "generateContent" in m.supported_generation_methods]
            if fetched_models:
                available_models = fetched_models
        except Exception:
            pass

    st.divider()
    st.header("📋 Fields to Extract")
    st.markdown("Specify the metadata fields you want to extract from the document.")
    metadata_fields = st.text_input("Fields (comma separated)", "Title, Author, Date, Summary, Main Keywords")
    
    st.divider()
    model_name = st.selectbox("LLM Model", available_models, index=0, help="Select the model to run the extraction.")
    
    st.divider()
    st.markdown("Supported Formats: PDF, DOCX, TXT")

uploaded_file = st.file_uploader("Upload a document", type=["pdf", "docx", "txt"])

def extract_text(file):
    text = ""
    try:
        filename = file.name.lower()
        if filename.endswith(".pdf"):
            doc = fitz.open(stream=file.read(), filetype="pdf")
            for page in doc:
                text += page.get_text()
        elif filename.endswith(".docx"):
            doc = docx.Document(io.BytesIO(file.read()))
            for para in doc.paragraphs:
                if para.text.strip():
                    text += para.text + "\n"
        elif filename.endswith(".txt"):
            text = str(file.read(), "utf-8")
    except Exception as e:
        st.error(f"Error reading file {filename}: {e}")
    return text

if uploaded_file and st.button("Extract Document Details", type="primary"):
    with st.spinner("Decoding document text..."):
        text = extract_text(uploaded_file)
        
    if not text.strip():
        st.warning("No text could be extracted from the uploaded document. It might be an image-only PDF.")
    else:
        st.success("Text extracted successfully!")
        
        col1, col2 = st.columns([1, 1], gap="large")
        
        with col1:
            st.subheader("📝 Extracted Content")
            st.text_area(f"Full Text ({len(text)} characters)", text, height=500)
        
        with col2:
            st.subheader("🧠 Extracted Metadata")
            if not api_key:
                st.info("ℹ️ Please enter your Gemini API Key in the sidebar to extract custom metadata.")
            elif not metadata_fields.strip():
                st.warning("⚠️ Please specify at least one metadata field to extract.")
            else:
                with st.spinner("Analyzing document with AI..."):
                    try:
                        genai.configure(api_key=api_key)
                        model = genai.GenerativeModel(model_name)
                        
                        prompt = f"""
                        You are an expert data extractor. Review the document text provided below and extract the following data fields:
                        [{metadata_fields}]
                        
                        Give the output as a clear key-value structure or a Markdown table. Be concise and accurate.
                        If a field is not explicitly found in the text, you can state "Not found".
                        
                        --- DOCUMENT TEXT ---
                        {text[:500000]}
                        """
                        
                        response = model.generate_content(prompt)
                        st.markdown(response.text)
                    except Exception as e:
                        st.error(f"Failed to generate metadata using Gemini: {str(e)}")
