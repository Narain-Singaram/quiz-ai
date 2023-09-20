from flask import Flask, render_template, request, redirect, url_for, flash, send_file
import google.generativeai as palm
import os
import io
from tempfile import NamedTemporaryFile

palm.configure(api_key="AIzaSyD2XypgJgP-RQPBQLgXhnyZ0kSOLUTM-OM")  # Replace with your actual API key

app = Flask(__name__)
app.secret_key = "your_secret_key"

defaults = {
    'model': 'models/text-bison-001',
    'temperature': 0.7,
    'candidate_count': 1,
    'top_k': 40,
    'top_p': 0.95,
    'max_output_tokens': 3000,
    'stop_sequences': [],
    'safety_settings': [
        {"category": "HARM_CATEGORY_DEROGATORY", "threshold": 4},
        {"category": "HARM_CATEGORY_TOXICITY", "threshold": 4},
        {"category": "HARM_CATEGORY_VIOLENCE", "threshold": 4},
        {"category": "HARM_CATEGORY_SEXUAL", "threshold": 4},
        {"category": "HARM_CATEGORY_MEDICAL", "threshold": 4},
        {"category": "HARM_CATEGORY_DANGEROUS", "threshold": 4},
    ],
}

conversation_history = []

@app.route('/export_questions', methods=['GET'])
def export_questions():
    # Generate questions using the chat history
    prompt = "\n".join(conversation_history)
    response = palm.generate_text(**defaults, prompt=prompt)
    generated_text = response.result

    if generated_text is not None:  # Ensure generated_text is not None
        # Create an in-memory file
        in_memory_file = io.BytesIO()
        in_memory_file.write(generated_text.encode('utf-8'))
        in_memory_file.seek(0)

        # Provide the in-memory file for download
        return send_file(
            in_memory_file,
            as_attachment=True,
            download_name="generated_questions.txt",
            mimetype='text/plain'
        )
    else:
        flash("Error generating questions.")
        return redirect(url_for('index'))

def format_chat_message(message):
    if message:
        formatted_message = message.replace('\n', '<br>')
        return formatted_message
    else:
        return ""

@app.route('/', methods=['GET', 'POST'])
def index():
    generated_text = None

    if request.method == 'POST':
        input_passage = request.form.get('input_passage')
        input_instructions = request.form.get('input_instructions')

        conversation_history.clear()

        conversation_history.append(input_passage)
        conversation_history.append(f"User: {format_chat_message(input_instructions)}")

        # Generate the response from the chatbot
        prompt = "\n".join(conversation_history)
        response = palm.generate_text(**defaults, prompt=prompt)
        generated_text = response.result

        chatbot_message = f"Chatbot: {format_chat_message(generated_text)}"
        conversation_history.append(chatbot_message)

        return redirect(url_for('index'))

    return render_template('index.html', generated_text=generated_text, conversation=conversation_history)

if __name__ == '__main__':
    app.run(debug=True, port=8080)
