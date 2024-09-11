from bot import obj
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/chatbot', methods=['POST'])
def chatbot():
    usermess = request.json.get('message')
    
    if not usermess:
        return jsonify({"error": "No message provided"}), 400  

    try:
        res = obj.message(usermess)
        return jsonify({"response": res})
    except Exception as e:
        print(f"Error processing the message: {e}")
        return jsonify({"error": "Error processing message"}), 500

if __name__ == '__main__':
    app.run(port=5001, debug=True)
