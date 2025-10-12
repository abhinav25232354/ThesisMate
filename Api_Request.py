from openai import OpenAI
import requests
import requests
import os
from bs4 import BeautifulSoup
import html
import re
from PyPDF2 import PdfReader



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
    # text = html_lines.append(f"<p>{html.escape(' '.join(paragraph_lines))}</p>")

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
    HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    MODEL_NAME = "sonar"

    try:
        # Handle file input
        if file:
            ext = os.path.splitext(file)[1].lower()
            if ext == ".txt":
                with open(file, "r", encoding="utf-8") as f:
                    userInput = f.read()
            elif ext == ".pdf":
                reader = PdfReader(file)
                userInput = "\n".join([page.extract_text() or "" for page in reader.pages])
            elif ext in [".docx", ".doc"]:
                doc = docx.Document(file)
                userInput = "\n".join([p.text for p in doc.paragraphs])
            else:
                return [], f"<p>Unsupported file format: {ext}</p>", []

        # Handle URL input
        if url:
            page = requests.get(url, timeout=15)
            soup = BeautifulSoup(page.content, "html.parser")
            for script in soup(["script", "style"]):
                script.extract()
            userInput = "\n".join([line.strip() for line in soup.get_text(separator="\n").splitlines() if line.strip()])

        if not userInput:
            return [], "<p>No input provided.</p>", []

        # Load chat history safely
        context = ""
        if os.path.exists("chat_history.txt"):
            try:
                with open("chat_history.txt", "r", encoding="utf-8") as f:
                    context = f.read()
            except Exception as e:
                print("Error reading chat_history.txt:", e)

        print(f"DEBUG: Sending to API -> userInput length: {len(userInput)}")

        payload = {
            "model": MODEL_NAME,
            "messages": [
            {
            "role": "system",
            "content": (
                "You are an intelligent assistant. "
                "If the user asks casual greetings or small talk, reply naturally and concisely. "
                "If the user asks a knowledge or research-related question, provide detailed and insightful answers. "
                "If a file is attached with the question, use its content to inform your response."
                "If the attached file is a research paper, thesis, or article, summarize its key points and findings in your answer."
                "If the user input contains multiple questions, answer each one thoroughly."
                "If the attached file is research then classify the research type (e.g., empirical study, literature review, theoretical paper) and summarize its main contributions accordingly. "
                "Support your response with **10–20 citations**, ensuring diversity of sources "
                "(academic papers, books, reputable articles). "
                "Do not summarize too briefly—expand fully."
                f"{context}"
            )
            },
            {
            "role": "user",
            "content": userInput
            }
        ],
        "temperature": 0.7,
        "max_tokens": 3000,                # OpenAI-compatible parameter (maps from your max_output_tokens)
        "top_p": 1.0,                     # Optional: nucleus sampling (default if not specified)
        "frequency_penalty": 0.0,         # Optional
        "presence_penalty": 0.0,          # Optional
        "stream": False,                  # Optional: set to true for streaming responses
        # Perplexity-specific parameters:
        "search_mode": "academic",             # or "academic" for scholarly mode :contentReference[oaicite:0]{index=0}
        "search_domain_filter": [],       # e.g., ["wikipedia.org"] or ["-reddit.com"] :contentReference[oaicite:1]{index=1}
        "search_recency_filter": None,    # e.g., "day", "week", "month", "year" :contentReference[oaicite:2]{index=2}
        "search_after_date_filter": None, # e.g., "3/1/2025" (MM/DD/YYYY format) :contentReference[oaicite:3]{index=3}
        "search_before_date_filter": None,# same format :contentReference[oaicite:4]{index=4}
        "last_updated_after_filter": None,
        "last_updated_before_filter": None,# if you want “last modified” filtering :contentReference[oaicite:5]{index=5}
        "return_images": False,           # Include image URLs if true :contentReference[oaicite:6]{index=6}
        "image_domain_filter": [],        # Requires return_images = true; e.g. ["-gettyimages.com"] :contentReference[oaicite:7]{index=7}
        "image_format_filter": [],        # e.g. ["png", "gif"] :contentReference[oaicite:8]{index=8}
        "return_related_questions": False,# Optional: include related questions :contentReference[oaicite:9]{index=9}
        "web_search_options": {           # Optional per advanced control (especially academic mode)
        "search_context_size": "high"    # or "high" :contentReference[oaicite:10]{index=10}
        },
        "response_format": None           # Structured output specifier (JSON Schema or Regex) :contentReference[oaicite:11]{index=11}
        }



        try:
            response = requests.post(API_URL, headers=HEADERS, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            print("API request failed:", e)
            return [], f"<p>API request error: {e}</p>", []

        answer_text = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        content = polished_markdown_to_html(answer_text)
        citations = data.get("citations", [])
        search_results = data.get("search_results", [])

        print("DEBUG: API call successful")
        return citations, content, search_results

    except Exception as e:
        print("askAI internal error:", e)
        return [], f"<p>Internal error: {e}</p>", []



if __name__ == "__main__":
    question = input("Enter your question: ")
    # file = "C:/Users/Infort/Downloads/Synopsis of Project.pdf"
    # print(askAI(question, file))
    print(askAI(question))