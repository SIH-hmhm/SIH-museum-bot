from bot import obj
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/chatbot', methods=['POST'])
def chatbot():
    usermess = request.json.get('message')
    
    res = f" {obj.message(usermess)}"
    return jsonify({"response": res})

if __name__ == '__main__':
    app.run(port=5001,debug=True) 
    