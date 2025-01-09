from flask import Flask, request, render_template
import fitz  # PyMuPDF for PDF handling
import docx  # For Word file handling
from transformers import pipeline

# Initialize Flask app
app = Flask(__name__)

# Initialize summarizer using a PyTorch model
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# Function to extract text from PDF
def extract_text_from_pdf(file):
    pdf_document = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        text += page.get_text()
    return text

# Function to extract text from Word
def extract_text_from_word(file):
    doc = docx.Document(file)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text

# Function to split text into smaller chunks
def split_text(text, max_length=1000):
    return [text[i:i + max_length] for i in range(0, len(text), max_length)]

# Home page
@app.route('/')
def home():
    return render_template('index.html')

# Route for summarizing documents
@app.route('/summarize', methods=['POST'])
def summarize():
    try:
        if 'file' not in request.files:
            return render_template('index.html', summary="No file uploaded.")

        file = request.files['file']
        filename = file.filename.lower()

        if filename.endswith('.pdf'):
            text = extract_text_from_pdf(file)
        elif filename.endswith('.docx'):
            text = extract_text_from_word(file)
        elif filename.endswith('.txt'):
            text = file.read().decode('utf-8')
        else:
            return render_template('index.html', summary="Unsupported file format. Please upload a PDF, DOCX, or TXT file.")

        # Split text into chunks
        chunks = split_text(text)

        # Summarize each chunk
        summary = ""
        for chunk in chunks:
            chunk_summary = summarizer(chunk, max_length=150, min_length=30, do_sample=False)[0]['summary_text']
            summary += chunk_summary + " "

        return render_template('index.html', summary=summary)

    except Exception as e:
        return render_template('index.html', summary=f"Error: {e}")

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
