from flask import Flask, render_template, request, redirect, url_for
import google.generativeai as palm

palm.configure(api_key="AIzaSyD2XypgJgP-RQPBQLgXhnyZ0kSOLUTM-OM")

app = Flask(__name__)

defaults = {
    'model': 'models/text-bison-001',
    'temperature': 0.7,
    'candidate_count': 1,
    'top_k': 40,
    'top_p': 0.95,
    'max_output_tokens': 1024,
    'stop_sequences': [],
    'safety_settings': [
        {"category": "HARM_CATEGORY_DEROGATORY", "threshold": 1},
        {"category": "HARM_CATEGORY_TOXICITY", "threshold": 1},
        {"category": "HARM_CATEGORY_VIOLENCE", "threshold": 2},
        {"category": "HARM_CATEGORY_SEXUAL", "threshold": 2},
        {"category": "HARM_CATEGORY_MEDICAL", "threshold": 2},
        {"category": "HARM_CATEGORY_DANGEROUS", "threshold": 2},
    ],
}

context = ("You are now tasked with the role of an advanced test creator. Users will provide you with diverse texts or data, and your responsibility is to craft high-level assessment questions that challenge their understanding at an advanced level, akin to questions found on standardized exams such as those administered by College Board or other advanced assessments."
           " The questions you generate should encompass a variety of formats, including true/false,"
           " multiple choice, and multiselect, and they must reflect advanced cognitive skills such as analysis, synthesis, and application."
           "Each question should be meticulously designed to be clear, precise, and nuanced, aiming to evaluate the deepest understanding "
           "of the provided content. Additionally, you are required to provide not only the questions but also the correct answers for each."
           " Your goal is to create a set of advanced-level assessment items that allow users to test their knowledge comprehensively."
           "(Please begin by generating a set of such questions based on the given text:")
conversation_history = [context]


def format_chat_message(message):
    if message:
        # Format the message as needed, e.g., handle line breaks, bullet points, etc.
        formatted_message = message.replace('\n', '<br>')  # Convert newlines to HTML line breaks
        # Add additional formatting logic here if needed
        return formatted_message
    else:
        return ""


@app.route('/', methods=['GET', 'POST'])
def index():
    generated_text = None

    if request.method == 'POST':
        input_passage = request.form.get('input_passage')
        input_instructions = request.form.get('input_instructions')

        # Create a conversation prompt that includes the passage and instructions
        conversation_history.clear()  # Clear the previous conversation
        conversation_history.append(input_passage)
        conversation_history.append(f"User: {format_chat_message(input_instructions)}")

        prompt = "\n".join(conversation_history)
        response = palm.generate_text(**defaults, prompt=prompt)
        generated_text = response.result

        chatbot_message = f"Chatbot: {format_chat_message(generated_text)}"
        conversation_history.append(chatbot_message)

        return redirect(url_for('index'))

        print(generated_text)

    return render_template('index.html', generated_text=generated_text, conversation=conversation_history)


if __name__ == '__main__':
    app.run(debug=True)
