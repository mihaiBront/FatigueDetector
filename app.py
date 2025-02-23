from flask import Flask, render_template, send_from_directory

app = Flask(__name__, 
    static_folder='static',  # explicitly set static folder
    template_folder='templates'  # explicitly set template folder
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == '__main__':
    app.run()  # added debug mode for development