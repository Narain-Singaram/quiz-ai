from flask import Flask, render_template, request

# Import the palm module and configure the API key
import google.generativeai as palm

palm.configure(api_key="AIzaSyD2XypgJgP-RQPBQLgXhnyZ0kSOLUTM-OM")

app = Flask(__name__)

# Define the default parameters for text generation
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

# Initialize a conversation history list with the context
context = ("You are Lumi, a compassionate and supportive mental health chatbot. "
           "Your primary goal is to provide empathetic and positive assistance to individuals seeking mental "
           "and emotional support. You are always open to helping people navigate their mental "
           "well-being and offer them a safe space to express their thoughts and feelings. "
           "In your interactions, prioritize active listening, empathy, and offering constructive guidance to "
           "improve the mental health of those who reach out to you. Create a conversation starter that invites "
           "someone to open up about their feelings and concerns.")
conversation_history = [context]


# Define the route to display the form and handle text generation
@app.route('/', methods=['GET', 'POST'])
def index():
    generated_text = None

    if request.method == 'POST':
        input_text = request.form.get('input_text')

        # Append the user's input to the conversation history
        conversation_history.append(f"User: {input_text}")

        # Create a conversation prompt that includes the entire history
        prompt = "\n".join(conversation_history)

        # Generate text based on the conversation history
        response = palm.generate_text(**defaults, prompt=prompt)

        # Extract the generated text from the response
        generated_text = response.result

        # Append the chatbot's response to the conversation history
        conversation_history.append(f"Chatbot: {generated_text}")

    return render_template('index.html', generated_text=generated_text, conversation=conversation_history)


if __name__ == '__main__':
    app.run(debug=True)
