import pytest
from fastapi.testclient import TestClient
from app.main import app
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from app.agent import check_compliance, modify_document
import json

client = TestClient(app)

@pytest.fixture
def create_test_pdf():
    """Create a test PDF file."""
    file_path = "test.pdf"
    c = canvas.Canvas(file_path, pagesize=letter)
    c.drawString(100, 750, "This is a test PDF document.")
    c.save()
    return file_path

def test_upload_file(create_test_pdf):
    """Test the upload file endpoint."""
    file_path = create_test_pdf
    with open(file_path, "rb") as f:
        response = client.post(
            "/api/upload/",
            files={"file": (file_path, f, "application/pdf")},
            data={"modify": "true"}
        )
    assert response.status_code == 200
    assert response.json()["filename"] == file_path

def test_check_compliance():
    """Test the check_compliance function with a dummy text."""
    dummy_text = "The dogs runs fast. John told Mike that he was wrong."
    report_json = check_compliance(dummy_text)
    report = json.loads(report_json)

    assert isinstance(report, list)
    assert len(report) > 0
    for item in report:
        assert "type" in item
        assert "description" in item
        assert "original_text" in item
        assert "suggestion" in item

def test_modify_document():
    """Test the modify_document function with a dummy text and report."""
    original_text = "The dogs runs fast. John told Mike that he was wrong."
    compliance_report = [
        {
            "type": "grammar",
            "description": "Subject-verb agreement error.",
            "original_text": "dogs runs",
            "suggestion": "dogs run"
        },
        {
            "type": "clarity",
            "description": "Ambiguous pronoun reference.",
            "original_text": "he was wrong",
            "suggestion": "Mike was wrong"
        }
    ]
    modified_text = modify_document(original_text, compliance_report)
    assert "dogs run fast" in modified_text
    assert "John told Mike that Mike was wrong." in modified_text
