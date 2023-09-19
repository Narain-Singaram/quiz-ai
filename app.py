from flask import Flask, render_template, request, redirect, url_for
import PyPDF2
from docx import Document
import google.generativeai as palm

palm.configure(api_key="AIzaSyD2XypgJgP-RQPBQLgXhnyZ0kSOLUTM-OM")

app = Flask(__name__)

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

def extract_text_from_pdf(pdf_file):
    pdf_text = ""
    try:
        pdf_reader = PyPDF2.PdfFileReader(pdf_file)
        for page_num in range(pdf_reader.numPages):
            page = pdf_reader.getPage(page_num)
            pdf_text += page.extractText()
    except Exception as e:
        print(f"Error extracting text from PDF: {str(e)}")
    return pdf_text

def extract_text_from_docx(docx_file):
    docx_text = ""
    try:
        doc = Document(docx_file)
        for paragraph in doc.paragraphs:
            docx_text += paragraph.text + "\n"
    except Exception as e:
        print(f"Error extracting text from DOCX: {str(e)}")
    return docx_text

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

        uploaded_file = request.files['file_input']

        if uploaded_file:
            if uploaded_file.filename.endswith('.pdf'):
                pdf_text = extract_text_from_pdf(uploaded_file)
                input_passage = f"{input_passage}\n{pdf_text}"
            elif uploaded_file.filename.endswith('.docx'):
                docx_text = extract_text_from_docx(uploaded_file)
                input_passage = f"{input_passage}\n{docx_text}"

        conversation_history.clear()
        conversation_history.append(input_passage)
        conversation_history.append(f"User: {format_chat_message(input_instructions)}")

        prompt = "\n".join(conversation_history)
        response = palm.generate_text(**defaults, prompt=prompt)
        generated_text = response.result

        chatbot_message = f"Chatbot: {format_chat_message(generated_text)}"
        conversation_history.append(chatbot_message)

        return redirect(url_for('index'))

    return render_template('index.html', generated_text=generated_text, conversation=conversation_history)

if __name__ == '__main__':
    app.run(debug=True, port=8080)
