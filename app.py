import sys

from flask import abort, Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://markmavromatis@localhost:5432/todoapp'

# Disable warning message
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False;

db = SQLAlchemy(app)

migrate = Migrate(app, db)

# Setup Todo Reminder class and backing table in Database
class Todo(db.Model):
  __tablename__ = 'todos'
  id = db.Column(db.Integer, primary_key=True)
  description = db.Column(db.String(), nullable=False)
  completed = db.Column(db.Boolean, nullable=False, default=False)

  # Override display value
  def __repr__(self):
    return f'<Todo {self.id} {self.description}>'

# Adds a new reminder
@app.route('/todos/create', methods=['POST'])
def create_todo():
  error = False
  body = {}
  try:
    description = request.get_json()['description']
    todo = Todo(description=description)
    db.session.add(todo)
    db.session.commit()
    body['description'] = todo.description
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    abort (400)
  else:
    return jsonify(body)

# Main Page
@app.route('/')
def index():
  return render_template('index.html', data=Todo.query.all())