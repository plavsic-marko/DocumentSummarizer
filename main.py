from flask import Flask, request, render_template
import fitz  # PyMuPDF for PDF handling
from transformers import pipeline

# Initialize Flask app
app = Flask(__name__)

# Initialize summarizer using a PyTorch model
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# Function to split text into smaller chunks
def split_text(text, max_length=1000):
    return [text[i:i + max_length] for i in range(0, len(text), max_length)]

# Home page
@app.route('/')
def home():
    return render_template('index.html')

# Route for summarizing PDF
@app.route('/summarize', methods=['POST'])
def summarize():
    try:
        if 'file' not in request.files:
            return render_template('index.html', summary="No PDF file uploaded.")

        file = request.files['file']
        pdf_document = fitz.open(stream=file.read(), filetype="pdf")
        original_text = ""
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            original_text += page.get_text()

        # Split text into chunks
        chunks = split_text(original_text)

        # Summarize each chunk
        summary = ""
        for chunk in chunks:
            chunk_summary = summarizer(chunk, max_length=150, min_length=30, do_sample=False)[0]['summary_text']
            summary += chunk_summary + " "

        return render_template('index.html', original_text=original_text, summary=summary)

    except Exception as e:
        return render_template('index.html', summary=f"Error: {e}")

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
