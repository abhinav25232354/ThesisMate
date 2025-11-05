from flask import Flask, render_template, request, jsonify
from Api_Request import askAI
import markdown
import os
import re
import html
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from html import unescape
import math
from difflib import SequenceMatcher

# Path Configuration
ROOT_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = ROOT_DIR / 'uploads'
CHAT_HISTORY_FILE = ROOT_DIR / 'chat_history.txt'
EVALUATION_FILE = ROOT_DIR / 'Evaluation.txt'

# Ensure required directories exist
UPLOAD_DIR.mkdir(exist_ok=True)

app = Flask(__name__)


def evaluate_response(question, answer):
    """
    Returns a stable, readable evaluation dictionary.
    It ensures all scores (0–100) reflect realistic proportions.
    """
    if not question or not answer:
        return {
            k: 0
            for k in [
                "confidence",
                "relevance",
                "completeness",
                "depth",
                "citations",
                "gap_accuracy",
                "impact",
            ]
        }

    # --- Clean text ---
    q = re.sub(r"[^a-zA-Z0-9 ]", "", question.lower())
    a = re.sub(r"[^a-zA-Z0-9 ]", "", answer.lower())

    # --- Confidence ---
    # If answer length is reasonable, confidence = 100
    confidence = min(100, len(a) / 20)  # scaled to sentence length

    # --- Relevance ---
    relevance = SequenceMatcher(None, q, a).ratio() * 100
    relevance = round(min(relevance + 30, 100), 2)  # boost for strong answers

    # --- Completeness ---
    # Based on length and keyword density
    completeness = min(100, len(a.split()) / 30 * 100)
    completeness = round(completeness, 2)

    # --- Depth ---
    depth_keywords = [
        "architecture",
        "training",
        "model",
        "data",
        "parameters",
        "applications",
        "challenges",
    ]
    depth_hits = sum(k in a for k in depth_keywords)
    depth = min(100, depth_hits / len(depth_keywords) * 100)

    # --- Citations ---
    # --- Citations Quality ---


    # Detects multiple citation patterns: [1], (Author, 2020), "according to", etc.
    citation_patterns = [
        r"\[\d+\]",  # [1]
        r"\(.*?et al\.,\s*\d{4}\)",  # (Smith et al., 2020)
        r"\(.*?\d{4}\)",  # (Smith, 2021)
        r"according to",  # "according to ..."
        r"source",  # "source: ..."
        r"reference",  # "reference"
    ]   

    citation_hits = sum(bool(re.search(p, answer.lower())) for p in citation_patterns)

    if citation_hits == 0:
        citations = 0
    elif citation_hits == 1:
        citations = 50
    else:
        citations = min(100, 60 + (citation_hits * 20))

    # --- Gap Accuracy ---
    gap_accuracy = round(
        max(20, min(100, relevance * 0.5 + completeness * 0.3 + depth * 0.2)), 2
    )

    # --- Research Impact ---
    impact = round((depth * 0.4 + completeness * 0.3 + confidence * 0.3), 2)
    impact = min(100, impact)

    return {
        "confidence": round(confidence, 2),
        "relevance": round(relevance, 2),
        "completeness": round(completeness, 2),
        "depth": round(depth, 2),
        "citations": round(citations, 2),
        "gap_accuracy": round(gap_accuracy, 2),
        "impact": round(impact, 2),
    }


def strip_html_tags(s):
    # 1. Remove all HTML tags
    s = re.sub(r"<[^>]*>", "", s)
    # 2. Decode HTML entities (e.g., &quot; → ")
    s = html.unescape(s)
    # 3. Remove citations like [1], [2][3][4], etc.
    s = re.sub(r"\[\d+(?:\]\[\d+)*\]", "", s)
    # 4. Normalize whitespace
    return re.sub(r"\s+", " ", s).strip()


def citation_function(citations):
    links = [f'<li><a href="{url}" target="_blank">{url}</a></li>' for url in citations]
    return "<ul>" + "".join(links) + "</ul>"


def search_results_function(search_results):
    results = []
    for res in search_results:
        results.append(
            {
                "title": res.get("title"),
                "url": res.get("url"),
                "date": res.get("date"),
                "last_updated": res.get("last_updated"),
            }
        )
    return results


def checkExistingEntry(question):
    def normalize_question(q):
        # Lowercase, strip, remove trailing punctuation (., ?, !)
        return re.sub(r"[.?!]+$", "", q.strip().lower())

    if not question:
        return "No entry Matched"

    try:
        if CHAT_HISTORY_FILE.exists():
            question_norm = normalize_question(question)
            with open(CHAT_HISTORY_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        chat_obj = eval(line.strip())
                    except Exception as e:
                        print(f"checkExistingEntry: failed to eval line: {e}")
                        continue
                    if isinstance(chat_obj, dict):
                        q = chat_obj.get("question", "")
                        if normalize_question(q) == question_norm:
                            return chat_obj
    except Exception as e:
        print(f"checkExistingEntry error: {e}")

    return "No entry Matched"


@app.route("/")
def index():
    return render_template("index.html", evaluation=None)


chats = []


@app.route("/ask", methods=["GET", "POST"])
def ask():
    if request.method == "POST":
        user_input = request.form.get("question", "").strip()
        url_input = request.form.get("url", "").strip()
        uploaded_file = request.files.get("fileInput")

        all_chats = []
        file_path = None
        evaluation = None
        if uploaded_file and uploaded_file.filename != "":
            file_path = UPLOAD_DIR / uploaded_file.filename
            uploaded_file.save(str(file_path))
            print(f"Uploaded File: {file_path}")

        # if nothing is provided, just reload the page
        if not user_input and not file_path and not url_input:
            all_chats = []
            if CHAT_HISTORY_FILE.exists():
                with open(CHAT_HISTORY_FILE, "r", encoding="utf-8") as f:
                    for line in f:
                        if not line.strip():
                            continue
                        try:
                            chat_obj = eval(line.strip())
                            if isinstance(chat_obj, dict):
                                all_chats.append(chat_obj)
                        except Exception as e:
                            print(f"ask POST: failed to eval chat_history line: {e}")
                            continue
            return render_template("index.html", chats=all_chats, evaluation=None)

        # found_chat = checkExistingEntry(user_input)
        found_chat = checkExistingEntry(user_input or file_path or url_input)

        if found_chat != "No entry Matched":
            # Only show the found chat, do not append or save duplicate
            with open(EVALUATION_FILE, "w") as eval_file:
                format_chat = strip_html_tags(found_chat["answer"])
                eval_file.write(f"\nQ: {user_input}\nCached: {format_chat}\n\n")

                evaluation = evaluate_response(user_input, format_chat)
                return render_template(
                    "index.html", chats=[found_chat], evaluation=evaluation
                )
            return render_template("index.html", chats=[found_chat], evaluation=None)

        # Not found, do a new API request
        try:
            print(f"User Input: {user_input}, File: {file_path}, URL: {url_input}")
            answer = askAI(userInput=user_input, file=file_path, url=url_input)
            print(f"API called")

            citations = citation_function(answer[0])
            content = answer[1]
            search_results = search_results_function(answer[2])
            chat_entry = {
                "question": user_input,
                "answer": content,
                "citations": citations,
                "search_results": search_results,
            }
            all_chats.append(chat_entry)
            with open(CHAT_HISTORY_FILE, "a", encoding="utf-8") as f:
                f.write(str(chat_entry) + "\n")

            # Write evaluation using the generated content (not found_chat which would be a string here)
            with open("Evaluation.txt", "w") as eval_file:
                format_chat = strip_html_tags(content)
                eval_file.write(f"\nQ: {user_input}\nCached: {format_chat}\n\n")

            evaluation = evaluate_response(user_input, format_chat)
            return render_template("index.html", chats=all_chats, evaluation=evaluation)

        except Exception as e:
            print(f"ask POST error: {e}")
            # Ensure variables passed to template are defined
            return render_template(
                "index.html",
                answer=f"Error: {str(e)}",
                question=user_input,
                chats=all_chats,
                evaluation=evaluation,
            )

    # GET request
    else:
        all_chats = []
        if os.path.exists("chat_history.txt"):
            with open("chat_history.txt", "r", encoding="utf-8") as f:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        chat_obj = eval(line.strip())
                        if isinstance(chat_obj, dict):
                            all_chats.append(chat_obj)
                    except Exception as e:
                        print(f"ask GET: failed to eval chat_history line: {e}")
                        continue
    return render_template("index.html", chats=all_chats, evaluation=None)


@app.route("/regenerate", methods=["POST", "GET"])
def regenerate():
    try:
        question = request.form.get("question", "").strip()
        with open(CHAT_HISTORY_FILE, "r", encoding="utf-8") as file:
            lines = file.readlines()
            context = lines[-1]

        prompt = f"Regenerate a detailed answer for the following question using this context as prior chat history: {context}\nQuestion: {question}"
        answer = askAI(prompt)
        citations = citation_function(answer[0])
        content = answer[1]
        search_results = search_results_function(answer[2])
        chat_entry = {
            "question": question + " (Regenerated)",
            "answer": content,
            "citations": citations,
            "search_results": search_results,
        }
        chats.append(chat_entry)
        with open("chat_history.txt", "a", encoding="utf-8") as f:
            f.write(str(chat_entry) + "\n")
        return render_template("index.html", chats=chats[-1:])

    except Exception as e:
        return render_template("index.html", answer=f"Error: {str(e)}")


@app.route("/about", methods=["GET"])
def about():
    return render_template("about.html")


@app.route("/history", methods=["GET"])
def history():
    return render_template("index.html", chats=chats)


@app.route("/analyzeGap", methods=["GET", "POST"])
def analyzeGap():
    try:
        question = request.form.get("question", "").strip()
        with open(CHAT_HISTORY_FILE, "r", encoding="utf-8") as file:
            lines = file.readlines()
            context = lines[-1]

        prompt = f"""
            You are an expert academic research assistant. 
            Based on the following context and question, identify meaningful and researchable gaps that future researchers could explore.

            Context (previous discussion or summary): {context}

            Question: {question}

            Your goal:
            1. Analyze what has already been studied or known.
            2. Identify missing elements, underexplored dimensions, or inconsistent findings.
            3. Suggest how future researchers can address these gaps (with methods, perspectives, or data improvements).
            4. Ensure your response is structured under these headings:
            - **Observed Trends**
            - **Existing Limitations**
            - **Potential Research Gaps**
            - **Future Research Directions**

            Be concise, analytical, and academic in tone. Focus only on gap discovery and future scope, not on summarizing the full paper.
            """

        answer = askAI(prompt)
        citations = citation_function(answer[0])
        content = answer[1]
        search_results = search_results_function(answer[2])
        chat_entry = {
            "question": question + " (Gap Analysis)",
            "answer": content,
            "citations": citations,
            "search_results": search_results,
        }
        chats.append(chat_entry)
        with open("chat_history.txt", "a", encoding="utf-8") as f:
            f.write(str(chat_entry) + "\n")
        return render_template("index.html", chats=chats[-1:])

    except Exception as e:
        return render_template("index.html", answer=f"Error: {str(e)}")


if __name__ == "__main__":
    app.run(debug=True)
