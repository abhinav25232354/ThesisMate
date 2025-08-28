from flask import Flask, render_template, request, jsonify
from Api_Request import askAI
import markdown

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

@app.route('/ask', methods=['GET', 'POST'])
def ask():
    if request.method == 'POST':
        user_input = request.form.get('question', '')
        if user_input.strip() == '':
            return render_template('index.html')
        try:
            answer = askAI(user_input)
            citations = citation_function(answer[0])
            content = answer[1]
            search_results = search_results_function(answer[2])
            print(f"User: {user_input}, Answer: {answer}")
            return render_template('index.html', answer=content, question=user_input, citations=citations, search_results=search_results)
        except Exception as e:
            return render_template('index.html', answer=f"Error: {str(e)}", question=user_input)
            # return render_template('index.html', answer=f"Error Occured - Please Try After Stable Version Release", question=user_input)
    else:
        # For GET requests, just show the default page
        return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)