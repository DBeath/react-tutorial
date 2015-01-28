from flask import Flask, Response, render_template
import os

app = Flask(__name__)

def root_dir():
	return os.path.abspath(os.path.dirname(__file__))

@app.route('/')
def index():
	return render_template('index.html')

if __name__ == '__main__':
	app.run(debug=True)