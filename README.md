# ThesisMate

ThesisMate is a Flask web app for exploring research questions, summarizing papers, analyzing article URLs, and generating structured AI-assisted responses with citations.

This repository is prepared for self-hosting and public reuse. It does not include personal credentials, user uploads, or private chat history.

## Features

- Ask research questions and receive structured responses
- Upload `.pdf`, `.txt`, and `.docx` files for analysis
- Analyze article URLs by pasting a link into the prompt field
- Review suggested citations and related sources
- Regenerate answers and run research gap analysis
- Cache prior responses locally in app-owned runtime storage

## Project Structure

```text
.
|-- app.py
|-- Api_Request.py
|-- requirements.txt
|-- templates/
|   |-- index.html
|   `-- about.html
|-- static/
|   |-- style.css
|   |-- Mobile.css
|   |-- script.js
|   `-- assets...
|-- data/                # created at runtime, ignored by git
|   |-- uploads/
|   |-- chat_history.jsonl
|   `-- evaluation.txt
|-- .env.example
|-- .gitignore
|-- LICENSE
`-- RELEASE_NOTES.md
```

## Requirements

- Python 3.10+
- A Perplexity API key

## Quick Start

1. Clone the repository.
2. Create a virtual environment.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Copy `.env.example` to `.env` or export the variables in your shell.
5. Set `PERPLEXITY_API_KEY`.
6. Run the app:

```bash
python app.py
```

7. Open `http://127.0.0.1:5000`.

## Configuration

Environment variables:

- `PERPLEXITY_API_KEY`: required API key
- `PERPLEXITY_API_URL`: optional override for the API endpoint
- `THESISMATE_MODEL`: model name, default `sonar`
- `THESISMATE_SEARCH_MODE`: search mode, default `academic`
- `THESISMATE_TEMPERATURE`: generation temperature, default `0.7`
- `THESISMATE_MAX_TOKENS`: max response tokens, default `3000`
- `THESISMATE_MAX_UPLOAD_BYTES`: upload size limit in bytes, default `16777216`
- `FLASK_HOST`: server host, default `127.0.0.1`
- `FLASK_PORT`: server port, default `5000`
- `FLASK_DEBUG`: enable debug mode with `true` or `1`

## Privacy and Local Data

ThesisMate stores runtime data in the local `data/` directory:

- uploaded files
- cached chat history
- latest evaluation output

Those files are ignored by git so they do not get committed by default.

## Development Notes

- The app expects outbound network access to reach the configured AI provider.
- The current UI is optimized for desktop layouts.
- If you want production deployment, use a WSGI server such as `gunicorn`.

## License

This project is released under the MIT License. See [LICENSE](LICENSE).
