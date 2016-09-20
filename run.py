from flask import Flask, Response, render_template, json, request, make_response, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from datetime import datetime
from marshmallow import Schema, fields, pprint
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, \
    RoleMixin, login_required


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'super-secret'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)

roles_users = db.Table('roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))


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

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)


@app.route('/')
@login_required
def index():
    return render_template('index.html')


@app.route('/comments', methods=['GET', 'POST'])
@login_required
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


@manager.command
def create_user(email, password):
    user_datastore.create_user(email=email, password=password)
    db.session.commit()


if __name__ == '__main__':
    manager.run()
