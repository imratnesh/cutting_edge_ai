"""
# app/main.py
# This module defines the FastAPI application and endpoints for file upload, compliance checking, and document modification.
# It includes endpoints to upload files, check their compliance, and optionally modify them based on the compliance report.
# Created by Ratnesh Kumar on 2024-01-01.
# """

from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from app.config import BASE_URL
from fastapi.responses import JSONResponse
import os
import pypdf
from docx import Document
import csv
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from datetime import datetime
import json
from app.agent import check_compliance, modify_document
from app.utils import setup_logger

api_endpoints_logger = setup_logger()
file_processor_logger = setup_logger()
report_generator_logger = setup_logger()

app = FastAPI(title="AI Document Compliance Checker")

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.post("/api/upload/")
async def upload_file(file: UploadFile = File(...), modify: bool = Form(...)):
    """Upload a PDF or Word document and check for compliance.

    This endpoint accepts PDF (.pdf) and Word (.docx) files.
    If an unsupported file type is uploaded, a 400 Bad Request error is returned.

    Args:
        file (UploadFile): The file to upload.
        modify (bool): Whether to modify the file to be compliant.

    Returns:
        JSONResponse: The response with the filename, compliance report, and csv report path.
    """
    supported_extensions = [".pdf", ".docx"]
    file_extension = os.path.splitext(file.filename)[1].lower()

    if file_extension not in supported_extensions:
        api_endpoints_logger.error(f"Unsupported file type uploaded: {file.filename}")
        return JSONResponse(status_code=400, content={"message": f"Unsupported file type: {file.filename}. Only PDF and Word (.docx) files are supported."})

    api_endpoints_logger.info(f"Received upload request for file: {file.filename}")
    
    if not os.path.exists('uploads'):
        os.makedirs('uploads')

    file_path = os.path.join('uploads', file.filename)
    api_endpoints_logger.info(f"Saving uploaded file: {file.filename}")
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
    api_endpoints_logger.info(f"File saved to: {file.filename}")

    text = ""
    api_endpoints_logger.info("Processing file content...")
    if file.filename.endswith(".pdf"):
        file_processor_logger.info("Processing file with content type: application/pdf")
        with open(file_path, "rb") as f:
            reader = pypdf.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text()
    elif file.filename.endswith(".docx"):
        file_processor_logger.info("Processing file with content type: application/vnd.openxmlformats-officedocument.wordprocessingprocessingml.document")
        document = Document(file_path)
        for paragraph in document.paragraphs:
            text += paragraph.text + "\n"

    api_endpoints_logger.info("Checking compliance...")
    compliance_report_json = check_compliance(text)
    try:
        compliance_report = json.loads(compliance_report_json)
    except json.JSONDecodeError:
        api_endpoints_logger.error(f"Failed to decode JSON from compliance report: {compliance_report_json}")
        compliance_report = []
    api_endpoints_logger.info("Compliance check complete.")

    
    
    # Generate CSV report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_report_filename = f"compliance_report_{timestamp}.csv"
    csv_report_path_relative = os.path.join('uploads', csv_report_filename)
    csv_report_path_absolute = f"{BASE_URL}{csv_report_path_relative}"

    with open(csv_report_path_relative, 'w', newline='') as csvfile:
        fieldnames = ["type", "description", "original_text", "suggestion"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for item in compliance_report:
            writer.writerow(item)
    report_generator_logger.info(f"Compliance report saved to: {csv_report_path_relative}")

    if modify:
        api_endpoints_logger.info(f"Received modify request for file: {file.filename}")
        modified_text = modify_document(text, compliance_report)
        modified_pdf_path_relative = os.path.join('uploads', f"modified_{file.filename}")
        modified_pdf_path_absolute = f"{BASE_URL}{modified_pdf_path_relative}"
        c = canvas.Canvas(modified_pdf_path_relative, pagesize=letter)
        width, height = letter
        text_object = c.beginText(40, height - 40)
        for line in modified_text.split('\n'):
            text_object.textLine(line)
        c.drawText(text_object)
        c.save()
        api_endpoints_logger.info(f"Modified PDF saved to: {modified_pdf_path_relative}")
        return JSONResponse(content={"filename": file.filename, "compliance_report": compliance_report, "modified_pdf_path": modified_pdf_path_absolute, "csv_report_path": csv_report_path_absolute})

    return JSONResponse(content={"filename": file.filename, "compliance_report": compliance_report, "csv_report_path": csv_report_path_absolute})