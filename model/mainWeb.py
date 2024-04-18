from flask import Flask, render_template, Response

_app = Flask(__name__, template_folder='../templates', static_folder='../static')

@_app.route('/')
def endpointHome():
    return render_template('index.html')

if __name__ == '__main__':
    _app.run(debug=True)