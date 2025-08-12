import sys
import os
from flask import Flask, jsonify

# Add the current directory to the Python path
sys.path.append(os.path.dirname(__file__))

from api.scheduled_call import _actual_handler_logic

app = Flask(__name__)

@app.route('/api/scheduled-call', methods=['GET'])
def scheduled_call():
    response_data = _actual_handler_logic()
    response = jsonify(response_data.get("body"))
    response.status_code = response_data.get("statusCode")
    return response

if __name__ == '__main__':
    app.run(debug=True)
