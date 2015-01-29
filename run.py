from flask import Flask, Response, render_template, json
import os

app = Flask(__name__)

def root_dir():
	return os.path.abspath(os.path.dirname(__file__))

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/comments', methods=['GET'])
def comments():
	print 'Hit comments url'
	file = open('_comments.json', 'r+')
	comments = json.loads(file.read())
	print comments
	file.close()

	return json.dumps(comments)

if __name__ == '__main__':
	app.run(debug=True)