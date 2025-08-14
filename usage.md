# Project Usage

This document provides instructions on how to set up and use this project.

## 1. Setup

### Prerequisites

- Python 3.7+
- pip

### Environment Variables

Create a `.env` file in the root directory of the project and add the following:

```
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-3.5-turbo
BASE_URL=http://127.0.0.1:8000/
```

Replace `your_openai_api_key` with your actual OpenAI API key. The `BASE_URL` should be the base URL where your FastAPI application is running.

## 2. Installation

Clone the repository and install the required dependencies:

```bash
git clone <repository_url>
cd <repository_name>
pip install -r requirements.txt
```

## 3. Running the Application

To run the application, use the following command:

```bash
uvicorn app.main:app --reload
```

The application will be available at `http://127.0.0.1:8000`.

## 4. API Usage

### Upload File

- **URL:** `/api/upload/`
- **Method:** `POST`
- **Headers:**
  - `accept: application/json`
  - `Content-Type: multipart/form-data`
- **Form Data:**
  - `file`: The PDF or Word (`.docx`) file to upload.
  - `modify`: A boolean value (`true` or `false`) to indicate whether to modify the file.

#### Sample cURL Request

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/api/upload/' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@/path/to/your/file.pdf;type=application/pdf' \
  -F 'modify=true'
```

#### Sample Response

```json
{
  "filename": "file.pdf",
  "compliance_report": [
    {
      "type": "grammar",
      "description": "Subject-verb agreement error.",
      "original_text": "The dogs runs.",
      "suggestion": "The dogs run."
    }
  ],
  "csv_report_path": "http://127.0.0.1:8000/uploads/compliance_report_20250814_114454.csv",
  "modified_pdf_path": "http://127.0.0.1:8000/uploads/modified_file.pdf" (only if modify=true)
}
```