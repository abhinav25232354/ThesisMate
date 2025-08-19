from flask import Flask, render_template, request, jsonify
from Api_Request import askAI

app = Flask(__name__)

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
            print(f"User: {user_input}, Answer: {answer}")
            return render_template('index.html', answer=answer, question=user_input)
        except Exception as e:
            return render_template('index.html', answer=f"Error: {str(e)}", question=user_input)
    else:
        # For GET requests, just show the default page
        return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)