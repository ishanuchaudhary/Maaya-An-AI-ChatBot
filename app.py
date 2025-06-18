from flask import Flask, render_template, request, jsonify
from chatbot import query_agent
import time

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/query', methods=['POST'])
def query():
    try:
        user_input = request.json.get('message', '')
        if not user_input:
            return jsonify({'error': 'No message provided'}), 400
        
        # Add a small delay to prevent rapid-fire requests
        time.sleep(0.5)
        
        response = query_agent(user_input)
        
        # Check if the response indicates a rate limit error
        if "high demand" in response.lower():
            return jsonify({
                'response': response,
                'status': 'rate_limited',
                'retry_after': 60  # Suggest retrying after 60 seconds
            })
        
        return jsonify({
            'response': response,
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({
            'error': f'An unexpected error occurred: {str(e)}',
            'status': 'error'
        }), 500

if __name__ == '__main__':
    app.run(debug=True) 