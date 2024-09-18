from flask import Flask, request, jsonify, render_template, redirect, url_for
import openai
import requests
import base64
from bs4 import BeautifulSoup
import os

app = Flask(__name__)

# Set your OpenAI API key
OPENAI_API_KEY= os.getenv('api_key')
openai.api_key = OPENAI_API_KEY
# In-memory storage for chatbot data (for demonstration purposes)
chatbot_data = {}


# Agent 1: Logo Generator
@app.route('/logo_generator')
def logo_generator():
    return render_template('logo_generator.html')

@app.route('/generate_logo', methods=['POST'])
def generate_logo():
    data = request.get_json()
    description = data['description']
    response = openai.Image.create(
        prompt=description,
        n=1,
        size="512x512"
    )
    image_url = response['data'][0]['url']
    # Fetch the image and encode it in base64
    image_response = requests.get(image_url)
    image_data = base64.b64encode(image_response.content).decode('utf-8')
    return jsonify({'image': image_data})

# Agent 2: Business Research Data Provider
@app.route('/business_research')
def business_research():
    return render_template('business_research.html')

@app.route('/get_research_data', methods=['POST'])
def get_research_data():
    data = request.get_json()
    website = data['website']
    # Fetch website content
    try:
        response = requests.get(website)
        soup = BeautifulSoup(response.text, 'html.parser')
        texts = soup.stripped_strings
        content = ' '.join(texts)
        # Limit content to maximum token length
        max_length = 2000
        content = content[:max_length]
        prompt = f"Provide a detailed business analysis for the following company based on their website content:\n\n{content}"
        completion = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=[{'role': 'user', 'content': prompt}]
        )
        summary = completion['choices'][0]['message']['content']
        return jsonify({'summary': summary})
    except Exception as e:
        return jsonify({'summary': f"An error occurred: {str(e)}"})

# Agent 3: Marketing Strategies Provider
@app.route('/marketing_strategies')
def marketing_strategies():
    return render_template('marketing_strategies.html')

@app.route('/get_strategies', methods=['POST'])
def get_strategies():
    data = request.get_json()
    domain = data['domain']
    prompt = f"Provide effective and innovative marketing strategies for a business in the following domain: {domain}"
    completion = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=[{'role': 'user', 'content': prompt}]
    )
    strategies = completion['choices'][0]['message']['content']
    return jsonify({'strategies': strategies})

# Agent 4: Custom Chatbot Generator
@app.route('/chatbot_generator')
def chatbot_generator():
    return render_template('chatbot_generator.html')

@app.route('/generate_chatbot', methods=['POST'])
def generate_chatbot():
    data = request.get_json()
    company_name = data['company_name']
    description = data['description']
    chatbot_id = company_name.replace(' ', '_').lower()
    # For demonstration, we'll store chatbot data in a simple dictionary
    # In production, use a database
    chatbot_data[chatbot_id] = {
        'company_name': company_name,
        'description': description
    }
    # Generate embed code with properly escaped braces and triple double quotes
    embed_code = f"""<div id="custom-chatbot"></div>
<script>
(function() {{{{ 
    var chatbot_id = '{chatbot_id}';
    var script = document.createElement('script');
    script.src = '/static/chatbot.js?chatbot_id=' + chatbot_id;
    document.head.appendChild(script);
}}}})();
</script>"""
    return jsonify({'embed_code': embed_code})

@app.route('/static/chatbot.js')
def chatbot_js():
    chatbot_id = request.args.get('chatbot_id')
    # JavaScript code that initializes the chatbot, using triple double quotes
    js_code = """
(function() {{{{
    var chatbotDiv = document.getElementById('custom-chatbot');
    chatbotDiv.style.position = 'fixed';
    chatbotDiv.style.bottom = '0';
    chatbotDiv.style.right = '0';
    chatbotDiv.style.width = '300px';
    chatbotDiv.style.height = '400px';
    chatbotDiv.style.border = '1px solid #ccc';
    chatbotDiv.style.backgroundColor = '#fff';
    var iframe = document.createElement('iframe');
    iframe.src = '/chatbot_window?chatbot_id=' + encodeURIComponent('{chatbot_id}');
    iframe.style.width = '100%';
    iframe.style.height = '100%';
    iframe.style.border = 'none';
    chatbotDiv.appendChild(iframe);
}})();
""".format(chatbot_id=chatbot_id)
    response = app.response_class(
        response=js_code,
        status=200,
        mimetype='application/javascript'
    )
    return response

@app.route('/chatbot_window')
def chatbot_window():
    chatbot_id = request.args.get('chatbot_id')
    chatbot_info = chatbot_data.get(chatbot_id, {})
    company_name = chatbot_info.get('company_name', 'Our Company')
    description = chatbot_info.get('description', '')
    return render_template('chatbot_window.html', company_name=company_name, chatbot_id=chatbot_id)

@app.route('/chat_response', methods=['POST'])
def chat_response():
    data = request.get_json()
    message = data['message']
    chatbot_id = data['chatbot_id']
    chatbot_info = chatbot_data.get(chatbot_id, {})
    company_name = chatbot_info.get('company_name', 'Our Company')
    description = chatbot_info.get('description', '')
    prompt = f"You are a chatbot for {company_name}. {description} Answer the following question:\n\n{message}"
    completion = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=[{'role': 'user', 'content': prompt}]
    )
    response_text = completion['choices'][0]['message']['content']
    return jsonify({'response': response_text})

# Home Route
@app.route('/')
def home():
    return render_template('home.html')


if __name__ == '__main__':
    app.run(debug=True)
