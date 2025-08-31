from flask import Flask, render_template, request, jsonify
from Api_Request import askAI
import markdown
import os

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

        file_path = None
        if uploaded_file and uploaded_file.filename != '':
            os.makedirs("uploads", exist_ok=True)
            file_path = os.path.join("uploads", uploaded_file.filename)
            uploaded_file.save(file_path)
            print(f"Uploaded File: {file_path}")

        # if nothing is provided, just reload the page
        if not user_input and not file_path and not url_input:
            return render_template('index.html', chats=chats)

        try:
            # Pass only the arguments that exist
            answer = askAI(
                userInput=user_input if user_input else None,
                file=file_path if file_path else None,
                url=url_input if url_input else None
            )

            citations = citation_function(answer[0])
            content = answer[1]
            search_results = search_results_function(answer[2])
            chats.append({
                "question": user_input,
                "answer": content,
                "citations": citations,
                "search_results": search_results
            })
            print(chats)

            return render_template(
                'index.html',
                chats=chats
            )

        except Exception as e:
            return render_template(
                'index.html',
                answer=f"Error: {str(e)}",
                question=user_input,
                chats=chats
            )

    # GET request
    else:
        return render_template('index.html', chats=chats)
    
@app.route('/about', methods=['GET'])
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)