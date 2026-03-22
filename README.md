# Document Text & Metadata Extractor

A Python-based Streamlit application that extracts text from documents (PDF, DOCX, TXT) and uses the Google Gemini AI to intelligently pull out metadata fields specified by the user.

## Features
- **File Upload:** Supports PDF, DOCX, and TXT files.
- **Text Extraction:** Uses `PyMuPDF` for fast PDF extraction and `python-docx` for Word documents.
- **AI-Powered Metadata Extraction:** Uses the `google-generativeai` SDK along with Gemini 1.5 Flash to rapidly analyze entire documents and extract any requested fields.
- **Customizable Fields:** Extract anything from Author, Date, Summary to specific key clauses or keywords.

## Setup Instructions

### 1. Prerequisites
You need **Python 3.8+** installed on your system.
*(Note: It appears Python is currently not installed, or not added to your system PATH. Please [download Python from python.org](https://www.python.org/downloads/) and ensure you check the box **"Add Python to PATH"** during installation.)*

### 2. Environment Setup
Open your terminal/command prompt in this folder and create a virtual environment:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
Install all required Python packages using pip:

```powershell
pip install -r requirements.txt
```

### 4. Run the Application
Start the Streamlit development server:

```powershell
streamlit run app.py
```
This will automatically open the application in your default web browser (typically at http://localhost:8501).

## Getting a Gemini API Key
To use the AI metadata extraction features, you will need a free Gemini API key:
1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey).
2. Sign in with your Google Account.
3. Click on **"Create API key"**.
4. Paste the generated key into the sidebar of the application.
