from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello, DevOps!, 1/24/25 6:22"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
