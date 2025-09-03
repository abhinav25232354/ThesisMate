from flask import Flask, render_template, request, jsonify
from Api_Request import askAI
import markdown
import os
import re

app = Flask(__name__)

def citation_function(citations):
    links = [f'<li><a href="{url}" target="_blank">{url}</a></li>' for url in citations]
    return "<ul>" + "".join(links) + "</ul>"

def search_results_function(search_results):
    results = []
    for res in search_results:
        results.append({
            "title": res.get("title"),
            "url": res.get("url"),
            "date": res.get("date"),
            "last_updated": res.get("last_updated")
        })
    return results

def checkExistingEntry(question):
    def normalize_question(q):
        # Lowercase, strip, remove trailing punctuation (., ?, !)
        return re.sub(r'[.?!]+$', '', q.strip().lower())

    if not question:
        return "No entry Matched"

    try:
        if os.path.exists("chat_history.txt"):
            question_norm = normalize_question(question)
            with open("chat_history.txt", "r", encoding="utf-8") as f:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        chat_obj = eval(line.strip())
                    except Exception:
                        continue
                    if isinstance(chat_obj, dict):
                        q = chat_obj.get("question", "")
                        if normalize_question(q) == question_norm:
                            return chat_obj
    except Exception:
        pass

    return "No entry Matched"

@app.route('/')
def index():
    return render_template('index.html')


chats = []
@app.route('/ask', methods=['GET', 'POST'])
def ask():
    if request.method == 'POST':
        user_input = request.form.get('question', '').strip()
        url_input = request.form.get('url', '').strip()   # 👈 for handling URL input
        uploaded_file = request.files.get('fileInput')   # 👈 safe get (no crash if missing)

        all_chats = []  # ✅ Always initialize here

        file_path = None
        if uploaded_file and uploaded_file.filename != '':
            os.makedirs("uploads", exist_ok=True)
            file_path = os.path.join("uploads", uploaded_file.filename)
            uploaded_file.save(file_path)
            print(f"Uploaded File: {file_path}")

        # if nothing is provided, just reload the page
        if not user_input and not file_path and not url_input:
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
                        except Exception:
                            continue
            return render_template('index.html', chats=all_chats)

        # ✅ Use checkExistingEntry instead of inline checking
        found_chat = checkExistingEntry(user_input)

        if found_chat != "No entry Matched":
            # Only show the found chat, do not append or save duplicate
            return render_template('index.html', chats=[found_chat])

        # Not found, do a new API request
        try:
            answer = askAI(
                userInput=user_input if user_input else None,
                file=file_path if file_path else None,
                url=url_input if url_input else None
            )

            citations = citation_function(answer[0])
            content = answer[1]
            search_results = search_results_function(answer[2])
            chat_entry = {
                "question": user_input,
                "answer": content,
                "citations": citations,
                "search_results": search_results
            }
            all_chats.append(chat_entry)
            with open("chat_history.txt", "a", encoding="utf-8") as f:
                f.write(str(chat_entry) + "\n")

            return render_template('index.html', chats=all_chats)

        except Exception as e:
            return render_template(
                'index.html',
                answer=f"Error: {str(e)}",
                question=user_input,
                chats=all_chats
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
                    except Exception:
                        continue
        return render_template('index.html', chats=all_chats)

    

@app.route('/regenerate', methods=['POST'])
def regenerate():
    try:
        question = request.form.get('question', '').strip()
        # Find the chat entry for this question
        chat_context = None
        if os.path.exists("chat_history.txt"):
            with open("chat_history.txt", "r", encoding="utf-8") as f:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        chat_obj = eval(line.strip())
                    except Exception:
                        continue
                    if isinstance(chat_obj, dict) and chat_obj.get("question", "").strip().lower() == question.lower():
                        chat_context = chat_obj
                        break
        # If found, use its context (the answer and possibly previous context)
        if chat_context:
            context_str = chat_context["answer"]
        else:
            context_str = ""
        # Regenerate using askAI with the context
        prompt = f"Regenerate a detailed answer for the following question using this context as prior chat history: {context_str}\nQuestion: {question}"
        answer = askAI(prompt)
        citations = citation_function(answer[0])
        content = answer[1]
        search_results = search_results_function(answer[2])
        chat_entry = {
            "question": question + " (Regenerated)",
            "answer": content,
            "citations": citations,
            "search_results": search_results
        }
        chats.append(chat_entry)
        with open("chat_history.txt", "a", encoding="utf-8") as f:
            f.write(str(chat_entry) + "\n")
        return render_template('index.html', chats=chats[-1:])
    except Exception as e:
        return render_template('index.html', answer=f"Error: {str(e)}")

@app.route('/about', methods=['GET'])
def about():
    return render_template('about.html')

@app.route('/history', methods=['GET'])
def history():
    return render_template('index.html', chats=chats)



@app.route("/analyzeGap", methods=["GET", "POST"])
def analyzeGap():
    try:
        # Get last chat context from history
        with open("chat_history.txt", "r") as f:
            last_line = [line for line in f if line.strip()][-1].strip()
        context = last_line

        # Run gap analysis prompt
        Gaps = askAI("Identify research gaps based on the above context." + context)
        citations = citation_function(Gaps[0])
        content = Gaps[1]
        search_results = search_results_function(Gaps[2])
        chat_entry = {
            "question": "Potential Gaps in research based on the above context.",
            "answer": content,
            "citations": citations,
            "search_results": search_results
        }
        chats.append(chat_entry)
        with open("chat_history.txt", "a") as f:
            f.write(str(chat_entry) + "\n")

        return render_template(
            'index.html',
            chats=chats[-1:]
        )
    except Exception as e:
        return render_template('index.html', answer=f"Error: {str(e)}")


if __name__ == '__main__':
    app.run(debug=True)
    # analyzeGap()