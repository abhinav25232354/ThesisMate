# ResearcherBuddy

ResearcherBuddy is a Flask-based web application designed to help students, professionals, and researchers explore, analyze, and summarize academic content more effectively. It integrates with AI models to process queries, research papers, and URLs, providing structured answers, citations, and research gap detection.  

The project is developed and maintained under the **DexterityCoder** brand.

---

## Features

- **Question Answering**  
  Enter a research question or query and receive a detailed AI-generated response with citations.

- **PDF Upload & Analysis**  
  Upload a research paper in PDF format to extract text, metadata, summaries, and insights.

- **Research Gap Detection**  
  Identify unexplored areas within a research topic to assist in generating original ideas.

- **URL-Based Research**  
  Provide a valid URL to analyze and summarize its content.

- **Citations and Sources**  
  Automatically formats citations and lists related sources with details such as title, publication date, and URL.

- **Chat History**  
  Stores past queries and responses for quick retrieval and reference.

- **Regeneration of Responses**  
  Re-run AI analysis on any previous question to generate a fresh, alternative answer.

- **Export Options**  
  Generate branded summaries and export them for offline use.

- **Smart Caching**  
  Stores previously processed queries for faster performance.

---

## Project Structure

```
.
├── app.py               # Main Flask application
├── Api_Request.py       # Handles API requests and content formatting
├── requirements.txt     # Python dependencies
├── templates/
│   ├── index.html       # Main UI
│   ├── about.html       # About page
├── static/
│   ├── style.css        # Stylesheet
│   ├── script.js        # Frontend logic
│   ├── logo.png         # Branding logo
│   └── Mobile.css       # Responsive styling for smaller screens
├── uploads/             # Uploaded PDFs and files
└── chat_history.txt     # Stores past queries and answers
```

---

## Installation

### Prerequisites
- Python 3.8 or later  
- A Perplexity AI API key (or other supported model API key)

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/researcherbuddy.git
   cd researcherbuddy
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate     # On Linux/Mac
   venv\Scripts\activate        # On Windows
   ```

3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Add your API key inside **`Api_Request.py`**:
   ```python
   API_KEY = "your-api-key-here"
   ```

5. Run the Flask application:
   ```bash
   python app.py
   ```

6. Open your browser at:
   ```
   http://127.0.0.1:5000
   ```

---

## Usage

1. **Ask a Question**  
   Type a question in the input box and press the submit button. The AI will generate a detailed response with citations.

2. **Upload a PDF**  
   Use the PDF upload button to analyze and summarize academic papers.

3. **Research Gaps**  
   Choose the “Analyze Gaps” option to let the system highlight areas lacking sufficient research.

4. **History and Regeneration**  
   - View past conversations via the **History** button.  
   - Regenerate answers for past queries using the **Regenerate** button.  

5. **Export Summaries**  
   Export AI responses and research summaries in a formatted PDF.

---

## Technology Stack

- **Backend**: Python, Flask  
- **Frontend**: HTML, CSS, JavaScript (with HTMX for dynamic updates)  
- **AI Models**: Perplexity API (Sonar model by default)  
- **Utilities**: PyPDF2 for PDF parsing, BeautifulSoup for web scraping, ReportLab for PDF exports  

---

## Contributing

Contributions are welcome. If you wish to improve functionality, fix bugs, or enhance the interface:

1. Fork the repository  
2. Create a new branch (`git checkout -b feature/new-feature`)  
3. Commit changes (`git commit -m "Added new feature"`)  
4. Push to your branch (`git push origin feature/new-feature`)  
5. Open a Pull Request  

---

## License

This project is licensed under the MIT License. You are free to use, modify, and distribute it with attribution.

---

## Contact

For questions, suggestions, or support, reach out at:  
**Email**: [support@dexteritycoder.com](mailto:support@dexteritycoder.com)  
