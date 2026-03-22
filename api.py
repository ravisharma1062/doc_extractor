from fastapi import FastAPI, File, UploadFile, Form, HTTPException
import fitz  # PyMuPDF
import docx
import io
import google.generativeai as genai

app = FastAPI(
    title="Document Extractor API",
    description="API for extracting text and specific fields from documents (PDF, DOCX, TXT) using Gemini AI.",
    version="1.0.0"
)

async def extract_document_text(file: UploadFile) -> str:
    text = ""
    filename = file.filename.lower()
    content = await file.read()
    
    try:
        if filename.endswith(".pdf"):
            doc = fitz.open(stream=content, filetype="pdf")
            for page in doc:
                text += page.get_text()
        elif filename.endswith(".docx"):
            doc = docx.Document(io.BytesIO(content))
            for para in doc.paragraphs:
                if para.text.strip():
                    text += para.text + "\n"
        elif filename.endswith(".txt"):
            text = content.decode("utf-8")
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format. Please upload PDF, DOCX, or TXT.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file {file.filename}: {str(e)}")
        
    return text

@app.post("/api/extract/text", summary="Full Text Extraction")
async def extract_text(file: UploadFile = File(..., description="The document file (PDF, DOCX, TXT)")):
    """
    Extracts the full raw text from the uploaded document.
    """
    text = await extract_document_text(file)
    if not text.strip():
        raise HTTPException(status_code=400, detail="No text could be extracted. It might be an image-only document.")
        
    return {"filename": file.filename, "text": text}

@app.post("/api/extract/fields", summary="Field Extraction using AI")
async def extract_fields(
    file: UploadFile = File(..., description="The document file (PDF, DOCX, TXT)"),
    fields: str = Form(..., description="Comma separated fields to extract (e.g. Title, Author, Date)"),
    api_key: str = Form(..., description="Your Gemini API Key"),
    model_name: str = Form("gemini-1.5-flash", description="Gemini model to use")
):
    """
    Extracts specified metadata fields from the document using Google's Gemini AI.
    """
    text = await extract_document_text(file)
    if not text.strip():
        raise HTTPException(status_code=400, detail="No text could be extracted to analyze.")
        
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)
        
        prompt = f"""
        You are an expert data extractor. Review the document text provided below and extract the following data fields:
        [{fields}]
        
        Give the output strictly as a JSON object where the keys are the field names requested.
        If a field is not explicitly found in the text, set its value to "Not found".
        Provide only the valid JSON object without any markup or markdown tags around it.
        
        --- DOCUMENT TEXT ---
        {text[:500000]}
        """
        
        response = model.generate_content(prompt)
        result_text = response.text.strip()
        
        # Clean up markdown block if the model included it
        if result_text.startswith("```json"):
            result_text = result_text[7:]
        if result_text.startswith("```"):
            result_text = result_text[3:]
        if result_text.endswith("```"):
            result_text = result_text[:-3]
            
        import json
        try:
            parsed_data = json.loads(result_text.strip())
        except json.JSONDecodeError:
            # Fallback if the AI fails to generate strict JSON
            parsed_data = {"raw_response": response.text.strip()}
            
        return {"filename": file.filename, "extracted_fields": parsed_data}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate metadata using Gemini: {str(e)}")
