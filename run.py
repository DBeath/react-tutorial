from flask import Flask, Response, render_template, json, request, make_response, jsonify
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand
from datetime import datetime

import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['DEBUG'] = True

db = SQLAlchemy(app)
migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)

class Comment(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	author = db.Column(db.String(80))
	text = db.Column(db.String(1024))
	posted = db.Column(db.DateTime, default=datetime.utcnow())

	def to_json(self):
		return {
			"id": self.id,
			"author": self.author,
			"text": self.text,
			"posted": str(self.posted)
		}

def root_dir():
	return os.path.abspath(os.path.dirname(__file__))

def get_comments():
	comments = Comment.query.all()
	values = [comment.to_json() for comment in comments]
	file = open('_comments.json', 'w+')
	file.write(json.dumps(values))
	file.close()
	return values

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/comments', methods=['GET'])
def comments():
	response = make_response()
	response.data = get_comments()
	print response.data
	return response

@app.route('/comments', methods=['POST'])
def post_comments():
	print request.form['author']
	print request.form['text']

	comment = Comment()
	comment.author = request.form['author']
	comment.text = request.form['text']
	db.session.add(comment)
	db.session.commit()

	response = make_response()
	response.data = get_comments()
	return response

if __name__ == '__main__':
	manager.run()