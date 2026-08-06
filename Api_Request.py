import html
import json
import os
import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader

try:
    from docx import Document
except ImportError:
    Document = None


def polished_markdown_to_html(text):
    if not text or not text.strip():
        return ""

    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = html.escape(text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^\*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*([^\*]+)\*", r"<em>\1</em>", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
    text = re.sub(r"(\[\d+(?:\]\[\d+)*\])", r"<sup>\1</sup>", text)

    lines = text.split("\n")
    html_lines = []
    index = 0
    while index < len(lines):
        line = lines[index].strip()
        if not line:
            index += 1
            continue

        header_match = re.match(r"^(#{1,6})\s+(.*)", line)
        if header_match:
            level = len(header_match.group(1))
            content = header_match.group(2)
            sizes = {1: "2em", 2: "1.75em", 3: "1.5em", 4: "1.25em", 5: "1.1em", 6: "1em"}
            html_lines.append(
                f"<h{level} style='font-size:{sizes[level]}; margin-bottom:1em;'>{content}</h{level}>"
            )
            index += 1
            continue

        if line.startswith(">"):
            quote_lines = []
            while index < len(lines) and lines[index].strip().startswith(">"):
                quote_lines.append(lines[index].strip()[1:].strip())
                index += 1
            html_lines.append(
                "<blockquote style='margin:1em 0; padding-left:1em; border-left:3px solid #ccc; "
                f"font-style:italic;'>{' '.join(quote_lines)}</blockquote>"
            )
            continue

        if re.match(r"^[-*]\s+", line):
            items = []
            while index < len(lines) and re.match(r"^[-*]\s+", lines[index].strip()):
                item = re.sub(r"^[-*]\s+", "", lines[index].strip())
                items.append(f"<li style='margin-bottom:0.5em;'>{item}</li>")
                index += 1
            html_lines.append(f"<ul style='margin-bottom:1em;'>{''.join(items)}</ul>")
            continue

        if re.match(r"^\d+\.\s+", line):
            items = []
            while index < len(lines) and re.match(r"^\d+\.\s+", lines[index].strip()):
                item = re.sub(r"^\d+\.\s+", "", lines[index].strip())
                items.append(f"<li style='margin-bottom:0.5em;'>{item}</li>")
                index += 1
            html_lines.append(f"<ol style='margin-bottom:1em;'>{''.join(items)}</ol>")
            continue

        paragraph = []
        while index < len(lines) and lines[index].strip():
            paragraph.append(lines[index].strip())
            index += 1
        html_lines.append(
            f"<p style='margin-bottom:1.5em; line-height:1.6;'>{' '.join(paragraph)}</p>"
        )

    return "\n".join(html_lines)


def extract_text_from_file(file_path):
    suffix = file_path.suffix.lower()
    if suffix == ".txt":
        return file_path.read_text(encoding="utf-8")
    if suffix == ".pdf":
        reader = PdfReader(str(file_path))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    if suffix in {".docx", ".doc"}:
        if Document is None:
            raise RuntimeError("python-docx is required to process Word documents.")
        document = Document(str(file_path))
        return "\n".join(paragraph.text for paragraph in document.paragraphs)
    raise RuntimeError(f"Unsupported file format: {suffix}")


def extract_text_from_url(url):
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")
    for script in soup(["script", "style"]):
        script.extract()
    return "\n".join(
        line.strip()
        for line in soup.get_text(separator="\n").splitlines()
        if line.strip()
    )


def read_history_context(history_path):
    if not history_path:
        return ""

    history_path = Path(history_path)
    if not history_path.exists():
        return ""

    context_items = []
    with history_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue
            context_items.append(item)
    return json.dumps(context_items[-3:], ensure_ascii=False)


def ask_ai(user_input=None, file_path=None, url=None, history_path=None):
    api_key = os.getenv("PERPLEXITY_API_KEY")
    api_url = os.getenv("PERPLEXITY_API_URL", "https://api.perplexity.ai/chat/completions")
    model_name = os.getenv("THESISMATE_MODEL", "sonar")

    if file_path:
        user_input = extract_text_from_file(Path(file_path))
    elif url:
        user_input = extract_text_from_url(url)

    if not user_input:
        return [], "<p>No input provided.</p>", []

    if not api_key:
        raise RuntimeError(
            "Missing PERPLEXITY_API_KEY. Add it to your environment before starting the app."
        )

    context = read_history_context(history_path)
    prompt = f"""
You are ThesisMate, an academic research assistant.
Answer the user's request with clear headings and practical academic structure.
When appropriate, cover:
1. Topic overview
2. Key concepts or theories
3. Methodology or evidence
4. Limitations or challenges
5. Research gaps
6. Future directions
7. Practical applications
8. Concise summary

Question:
{user_input}

Recent context:
{context[:3000]}
""".strip()

    payload = {
        "model": model_name,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a helpful academic assistant. "
                    "Use a professional tone, answer clearly, and cite sources when the model provides them."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": float(os.getenv("THESISMATE_TEMPERATURE", "0.7")),
        "max_tokens": int(os.getenv("THESISMATE_MAX_TOKENS", "3000")),
        "top_p": 1.0,
        "search_mode": os.getenv("THESISMATE_SEARCH_MODE", "academic"),
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise RuntimeError("The upstream AI request failed. Check your API key and network access.") from exc

    data = response.json()
    answer_text = data.get("choices", [{}])[0].get("message", {}).get("content", "")
    content = polished_markdown_to_html(answer_text)
    citations = data.get("citations", [])
    search_results = data.get("search_results", [])
    return citations, content, search_results


if __name__ == "__main__":
    prompt = input("Enter your question: ")
    print(ask_ai(user_input=prompt))
