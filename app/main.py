from flask import Flask, request

app = Flask(__name__)


@app.route("/")
def home_view():
    return "<h1>Hello World!</h1>"


@app.route("/db", methods=['POST'])
def update_data_set():
    if request.method == 'POST':
        return 'Good request', 200
    else:
        return 'Bad request', 400


