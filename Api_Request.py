from openai import OpenAI
import requests

import requests
import os
from bs4 import BeautifulSoup
import html
import re



def polished_markdown_to_html(text):
    """
    Convert Markdown-like text to polished, article-ready HTML.
    """
    if not text or not text.strip():
        return ""

    # Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Escape HTML first
    text = html.escape(text)

    # Inline formatting
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)  # code
    text = re.sub(r'\*\*([^\*]+)\*\*', r'<strong>\1</strong>', text)  # bold
    text = re.sub(r'\*([^\*]+)\*', r'<em>\1</em>', text)  # italic
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)  # links
    text = re.sub(r'(\[\d+(?:\]\[\d+)*\])', r'<sup>\1</sup>', text)  # citations

    lines = text.split("\n")
    html_lines = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue

        # Headers (#, ##, ...)
        header_match = re.match(r'^(#{1,6})\s+(.*)', line)
        if header_match:
            level = len(header_match.group(1))
            content = header_match.group(2)
            size_style = {1:"2em",2:"1.75em",3:"1.5em",4:"1.25em",5:"1.1em",6:"1em"}
            html_lines.append(f"<h{level} style='font-size:{size_style[level]}; margin-bottom:1em;'>{content}</h{level}>")
            i += 1
            continue

        # Blockquotes
        if line.startswith(">"):
            quote_lines = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                quote_lines.append(lines[i].strip()[1:].strip())
                i += 1
            html_lines.append(f"<blockquote style='margin:1em 0; padding-left:1em; border-left:3px solid #ccc; font-style:italic;'>{' '.join(quote_lines)}</blockquote>")
            continue

        # Unordered lists
        if re.match(r'^[-*]\s+', line):
            list_items = []
            while i < len(lines) and re.match(r'^[-*]\s+', lines[i].strip()):
                item = re.sub(r'^[-*]\s+', '', lines[i].strip())
                list_items.append(f"<li style='margin-bottom:0.5em;'>{item}</li>")
                i += 1
            html_lines.append(f"<ul style='margin-bottom:1em;'>{''.join(list_items)}</ul>")
            continue

        # Ordered lists
        if re.match(r'^\d+\.\s+', line):
            list_items = []
            while i < len(lines) and re.match(r'^\d+\.\s+', lines[i].strip()):
                item = re.sub(r'^\d+\.\s+', '', lines[i].strip())
                list_items.append(f"<li style='margin-bottom:0.5em;'>{item}</li>")
                i += 1
            html_lines.append(f"<ol style='margin-bottom:1em;'>{''.join(list_items)}</ol>")
            continue

        # Normal paragraph
        paragraph_lines = []
        while i < len(lines) and lines[i].strip() != "":
            paragraph_lines.append(lines[i].strip())
            i += 1
        html_lines.append(f"<p style='margin-bottom:1.5em; line-height:1.6;'>{' '.join(paragraph_lines)}</p>")

    return "\n".join(html_lines)

def askAI(userInput=None, file=None, url=None):
    API_KEY = "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"
    API_URL = "https://api.perplexity.ai/chat/completions"
    HEADERS = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    MODEL_NAME = "sonar"
    # MODEL_NAME = "sonar-deep-research"

    # Handle file upload
    if file:
        ext = os.path.splitext(file)[1].lower()
        try:
            if ext == ".txt":
                with open(file, "r", encoding="utf-8") as f:
                    userInput = f.read()
            elif ext == ".pdf":
                from PyPDF2 import PdfReader
                reader = PdfReader(file)
                userInput = "\n".join([page.extract_text() for page in reader.pages])
            elif ext in [".docx", ".doc"]:
                import docx
                doc = docx.Document(file)
                userInput = "\n".join([p.text for p in doc.paragraphs])
            else:
                raise ValueError("Unsupported file format. Use txt, pdf, or docx.")
        except Exception as e:
            return [], f"<p>Error reading file: {str(e)}</p>", []

    # Handle URL analysis
    elif url:
        try:
            page = requests.get(url, timeout=10)
            soup = BeautifulSoup(page.content, "html.parser")
            # Extract main readable text
            for script in soup(["script", "style"]):
                script.extract()
            userInput = soup.get_text(separator="\n")
            userInput = "\n".join([line.strip() for line in userInput.splitlines() if line.strip()])
        except Exception as e:
            return [], f"<p>Error fetching URL: {str(e)}</p>", []

    # Ensure we have something to process
    if not userInput:
        return [], "<p>No input provided.</p>", []

    # payload = {
    #     "model": MODEL_NAME,
    #     "messages": [
    #         {"role": "system", "content": "You are a helpful research assistant. Always respond with very long and detailed answers. Don't add markdown syntax bold, italic, underline, bullets, citations and reference markers etc."},
    #         {"role": "user", "content": userInput}
    #     ],
    #     "max_tokens": 700,
    #     "temperature": 0.7,
    # }
    with open("chat_history.txt", "r") as f:
        context = f.read()

    payload = {
    "model": MODEL_NAME,
    "messages": [
        {
            "role": "system",
            "content": (
                "You are an intelligent assistant. "
                "If the user asks casual greetings or small talk, reply naturally and concisely. "
                "If the user asks a knowledge or research-related question, provide detailed and insightful answers. "
                f"{context}"
    )
        },
        {"role": "user", "content": userInput}
    ],
    "temperature": 0.7,
    "max_output_tokens": 700   # Perplexity uses 'max_output_tokens' instead of 'max_tokens'
}


    response = requests.post(API_URL, headers=HEADERS, json=payload)
    response.raise_for_status()
    data = response.json()

    answer = data["choices"][0]["message"]["content"]
    # Format answer as HTML paragraphs for display
    # content = "<p>" + answer.replace("\n\n", "</p><p>").replace("\n", "<br><br>") + "</p>"
    content = polished_markdown_to_html(answer)
    citations = data.get("citations", [])
    search_results = data.get("search_results", [])

    return citations, content, search_results



if __name__ == "__main__":
    question = "Explain this PDF in detail."
    file = "C:/Users/Infort/Downloads/Synopsis of Project.pdf"
    print(askAI(question, file))