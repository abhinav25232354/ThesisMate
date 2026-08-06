import json
import os
import re
from html import unescape
from pathlib import Path
from difflib import SequenceMatcher

from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

from Api_Request import ask_ai

ROOT_DIR = Path(__file__).resolve().parent
DATA_DIR = ROOT_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
CHAT_HISTORY_FILE = DATA_DIR / "chat_history.jsonl"
EVALUATION_FILE = DATA_DIR / "evaluation.txt"

DATA_DIR.mkdir(exist_ok=True)
UPLOAD_DIR.mkdir(exist_ok=True)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = int(
    os.getenv("THESISMATE_MAX_UPLOAD_BYTES", 16 * 1024 * 1024)
)


def evaluate_response(question, answer):
    if not question or not answer:
        return {
            key: 0
            for key in (
                "confidence",
                "relevance",
                "completeness",
                "depth",
                "citations",
                "gap_accuracy",
                "impact",
            )
        }

    normalized_question = re.sub(r"[^a-zA-Z0-9 ]", "", question.lower())
    normalized_answer = re.sub(r"[^a-zA-Z0-9 ]", "", answer.lower())

    confidence = min(100, len(normalized_answer) / 20)
    relevance = SequenceMatcher(None, normalized_question, normalized_answer).ratio() * 100
    relevance = round(min(relevance + 30, 100), 2)
    completeness = round(min(100, len(normalized_answer.split()) / 30 * 100), 2)

    depth_keywords = [
        "architecture",
        "training",
        "model",
        "data",
        "parameters",
        "applications",
        "challenges",
    ]
    depth = min(100, sum(keyword in normalized_answer for keyword in depth_keywords) / len(depth_keywords) * 100)

    citation_patterns = [
        r"\[\d+\]",
        r"\(.*?et al\.,\s*\d{4}\)",
        r"\(.*?\d{4}\)",
        r"according to",
        r"source",
        r"reference",
    ]
    citation_hits = sum(bool(re.search(pattern, answer.lower())) for pattern in citation_patterns)
    if citation_hits == 0:
        citations = 0
    elif citation_hits == 1:
        citations = 50
    else:
        citations = min(100, 60 + (citation_hits * 20))

    gap_accuracy = round(
        max(20, min(100, relevance * 0.5 + completeness * 0.3 + depth * 0.2)), 2
    )
    impact = min(100, round((depth * 0.4 + completeness * 0.3 + confidence * 0.3), 2))

    return {
        "confidence": round(confidence, 2),
        "relevance": round(relevance, 2),
        "completeness": round(completeness, 2),
        "depth": round(depth, 2),
        "citations": round(citations, 2),
        "gap_accuracy": gap_accuracy,
        "impact": round(impact, 2),
    }


def strip_html_tags(value):
    value = re.sub(r"<[^>]*>", "", value)
    value = unescape(value)
    value = re.sub(r"\[\d+(?:\]\[\d+)*\]", "", value)
    return re.sub(r"\s+", " ", value).strip()


def citation_function(citations):
    if not citations:
        return ""
    links = [f'<li><a href="{url}" target="_blank" rel="noopener noreferrer">{url}</a></li>' for url in citations]
    return "<ul>" + "".join(links) + "</ul>"


def search_results_function(search_results):
    return [
        {
            "title": result.get("title"),
            "url": result.get("url"),
            "date": result.get("date"),
            "last_updated": result.get("last_updated"),
        }
        for result in search_results
    ]


def normalize_question(question):
    return re.sub(r"[.?!]+$", "", str(question).strip().lower())


def load_chat_history():
    if not CHAT_HISTORY_FILE.exists():
        return []

    chats = []
    with CHAT_HISTORY_FILE.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                chat = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(chat, dict):
                chats.append(chat)
    return chats


def append_chat_entry(chat_entry):
    with CHAT_HISTORY_FILE.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(chat_entry, ensure_ascii=False) + "\n")


def find_existing_entry(question):
    normalized = normalize_question(question)
    if not normalized:
        return None

    for chat in load_chat_history():
        if normalize_question(chat.get("question", "")) == normalized:
            return chat
    return None


def persist_evaluation(question, answer):
    clean_answer = strip_html_tags(answer)
    EVALUATION_FILE.write_text(
        f"Q: {question}\nAnswer: {clean_answer}\n",
        encoding="utf-8",
    )
    return evaluate_response(question, clean_answer)


def save_uploaded_file(uploaded_file):
    filename = secure_filename(uploaded_file.filename or "")
    if not filename:
        return None

    destination = UPLOAD_DIR / filename
    uploaded_file.save(destination)
    return destination


def render_index(chats=None, evaluation=None, answer=None, question=None):
    return render_template(
        "index.html",
        chats=chats or [],
        evaluation=evaluation,
        answer=answer,
        question=question,
    )


@app.route("/")
def index():
    return render_index()


@app.route("/ask", methods=["GET", "POST"])
def ask():
    if request.method == "GET":
        return render_index(chats=load_chat_history(), evaluation=None)

    user_input = request.form.get("question", "").strip()
    url_input = request.form.get("url", "").strip()
    uploaded_file = request.files.get("fileInput")
    file_path = save_uploaded_file(uploaded_file) if uploaded_file and uploaded_file.filename else None
    if not url_input and user_input.lower().startswith(("http://", "https://")):
        url_input = user_input
        user_input = ""

    if not user_input and not url_input and not file_path:
        return render_index(chats=load_chat_history(), evaluation=None)

    cache_key = user_input or url_input or str(file_path)
    found_chat = find_existing_entry(cache_key)
    if found_chat:
        evaluation = persist_evaluation(user_input or cache_key, found_chat["answer"])
        return render_index(chats=[found_chat], evaluation=evaluation)

    try:
        citations, content, search_results = ask_ai(
            user_input=user_input,
            file_path=file_path,
            url=url_input,
            history_path=CHAT_HISTORY_FILE,
        )
        chat_entry = {
            "question": user_input or url_input or file_path.name,
            "answer": content,
            "citations": citation_function(citations),
            "search_results": search_results_function(search_results),
        }
        append_chat_entry(chat_entry)
        evaluation = persist_evaluation(chat_entry["question"], content)
        return render_index(chats=[chat_entry], evaluation=evaluation)
    except Exception as exc:
        return render_index(
            chats=load_chat_history(),
            evaluation=None,
            answer=f"Error: {exc}",
            question=user_input,
        )


@app.route("/regenerate", methods=["POST"])
def regenerate():
    question = request.form.get("question", "").strip()
    history = load_chat_history()
    if not history:
        return render_index(answer="No previous chat history is available to regenerate from.")

    context = history[-1]
    prompt = (
        "Regenerate a detailed answer for the following question using this context "
        f"as prior chat history: {json.dumps(context, ensure_ascii=False)}\n"
        f"Question: {question}"
    )
    citations, content, search_results = ask_ai(
        user_input=prompt,
        history_path=CHAT_HISTORY_FILE,
    )
    chat_entry = {
        "question": f"{question} (Regenerated)",
        "answer": content,
        "citations": citation_function(citations),
        "search_results": search_results_function(search_results),
    }
    append_chat_entry(chat_entry)
    return render_index(chats=[chat_entry], evaluation=persist_evaluation(chat_entry["question"], content))


@app.route("/about", methods=["GET"])
def about():
    return render_template("about.html")


@app.route("/history", methods=["GET"])
def history():
    return render_index(chats=load_chat_history())


@app.route("/analyzeGap", methods=["POST"])
def analyze_gap():
    question = request.form.get("question", "").strip()
    history = load_chat_history()
    if not history:
        return render_index(answer="No previous chat history is available for gap analysis.")

    context = history[-1]
    prompt = f"""
You are an expert academic research assistant.
Based on the following context and question, identify meaningful and researchable gaps that future researchers could explore.

Context (previous discussion or summary): {json.dumps(context, ensure_ascii=False)}

Question: {question}

Your goal:
1. Analyze what has already been studied or known.
2. Identify missing elements, underexplored dimensions, or inconsistent findings.
3. Suggest how future researchers can address these gaps.
4. Structure the response under these headings:
   - Observed Trends
   - Existing Limitations
   - Potential Research Gaps
   - Future Research Directions
"""

    citations, content, search_results = ask_ai(
        user_input=prompt,
        history_path=CHAT_HISTORY_FILE,
    )
    chat_entry = {
        "question": f"{question} (Gap Analysis)",
        "answer": content,
        "citations": citation_function(citations),
        "search_results": search_results_function(search_results),
    }
    append_chat_entry(chat_entry)
    return render_index(chats=[chat_entry], evaluation=persist_evaluation(chat_entry["question"], content))


if __name__ == "__main__":
    app.run(
        debug=os.getenv("FLASK_DEBUG", "").lower() in {"1", "true", "yes"},
        host=os.getenv("FLASK_HOST", "127.0.0.1"),
        port=int(os.getenv("FLASK_PORT", "5000")),
    )
