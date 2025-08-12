from flask import Flask, jsonify, render_template, url_for
import os
from scheduled_call import _actual_handler_logic

# Configure Flask to find templates and static files in parent directories
app = Flask(__name__, 
            template_folder='../templates',
            static_folder='../static')

@app.route('/api/scheduled-call', methods=['GET'])
def scheduled_call():
    response_data = _actual_handler_logic()
    response = jsonify(response_data.get("body"))
    response.status_code = response_data.get("statusCode")
    return response

@app.route('/')
def home():
    return render_template('index.html')

# Add any other routes for your application

if __name__ == '__main__':
    app.run(debug=True)