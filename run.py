from flask import Flask, Response, render_template, json, request, make_response, jsonify
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand
from datetime import datetime
from marshmallow import Schema, fields, pprint
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
	posted = db.Column(db.DateTime, default=datetime.utcnow)

	def to_json(self):
		return {
			"id": self.id,
			"author": self.author,
			"text": self.text,
			"posted": str(self.posted)
		}

class CommentSchema(Schema):
	id = fields.Integer()
	author = fields.String()
	text = fields.String()
	posted = fields.DateTime()

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/comments', methods=['GET', 'POST'])
def comments():
	if request.method == 'POST':
		comment = Comment()
		comment.author = request.form['author']
		comment.text = request.form['text']
		db.session.add(comment)
		db.session.commit()

	comments = Comment.query.order_by(Comment.posted.desc())
	serializer = CommentSchema(many=True)
	result = serializer.dump(comments)
	response = jsonify({"comments": result.data})
	return response

if __name__ == '__main__':
	manager.run()