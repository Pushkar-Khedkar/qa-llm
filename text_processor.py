import fitz  # PyMuPDF
import docx 
import io

# Function to extract text from a PDF file
def extract_text_from_pdf(pdf_bytes):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    text = ""
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        text += page.get_text("text")
    doc.close()
    return text

# Function to extract text from a Word file
def extract_text_from_docx(docx_bytes):
    docx_file = io.BytesIO(docx_bytes)
    doc = docx.Document(docx_file)
    text = []
    for paragraph in doc.paragraphs:
        text.append(paragraph.text)
    return "\n".join(text)
