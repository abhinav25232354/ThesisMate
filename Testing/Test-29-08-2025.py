from flask import Flask, request, render_template_string
import fitz   # PyMuPDF
import io

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def upload_pdf():
    extracted_text = ""
    if request.method == 'POST':
        file = request.files.get('file')
        if file:
            file_bytes = file.read()
            # Open PDF directly from bytes, no saving
            pdf_doc = fitz.open(stream=file_bytes, filetype="pdf")
            extracted_text = ""
            for page in pdf_doc:
                extracted_text += page.get_text()
            # extracted_text variable now contains all PDF text

    # Simple upload form for demonstration
    return render_template_string("""
        <form method="post" enctype="multipart/form-data">
            <input type="file" name="file" accept=".pdf">
            <input type="submit" value="Upload PDF">
        </form>
        <pre>{{text}}</pre>
    """, text=extracted_text)

if __name__ == '__main__':
    app.run(debug=True)
