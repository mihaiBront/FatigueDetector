from flask import Flask, render_template, jsonify, request
import src.server_file_sample as srvSample

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/getHelloWorld', methods=['POST'])
def getHelloWorld():
    try:
        data = request.get_json()
        name = data.get('name', '')

        if len(name) == 0:
            raise Exception("No name provided")

        return jsonify(message=srvSample.makeStringForGreeting(name)), 200
    
    except Exception as ex:
        return jsonify(error=f"{ex} :´("), 500

if __name__ == '__main__':
    app.run()
