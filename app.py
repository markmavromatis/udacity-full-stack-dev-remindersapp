import sys

from flask import abort, Flask, jsonify, render_template, request, redirect, url_for
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
  list_id = db.Column(db.Integer, db.ForeignKey('todolists.id'), nullable = False)

  # Override display value
  def __repr__(self):
    return f'<Todo {self.id} {self.description}>'

class TodoList(db.Model):
  __tablename__ = 'todolists'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(), nullable = False)
  todos = db.relationship('Todo', backref = 'list', lazy = False, cascade ="all, delete-orphan")

  def __repr__(self):
    return f'<Todo List {self.id} {self.description}'

# Adds a new reminder
@app.route('/todos/createToDo', methods=['POST'])
def create_todo():
  error = False
  body = {}
  try:
    description = request.get_json()['description']
    list_id = request.get_json()['list_id']
    todo = Todo(description=description, list_id=list_id)
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

# Adds a new reminders list
@app.route('/todos/createList', methods=['POST'])
def create_list():
  error = False
  body = {}
  try:
    name = request.get_json()['name']
    new_list = TodoList(name=name)
    db.session.add(new_list)
    db.session.commit()
    body['name'] = new_list.name
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

# Update the completed status of a reminder
@app.route('/todos/<todo_id>/set-completed-todo', methods=['POST'])
def set_completed_todo(todo_id):
  try:
    completed = request.get_json()['completed']
    todo = Todo.query.get(todo_id)
    todo.completed = completed
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  return redirect(url_for('index'))

# Update the completed status of a list
@app.route('/todos/<list_id>/set-completed-list', methods=['POST'])
def set_completed_list(list_id):
  try:
    todos = Todo.query.filter_by(list_id = list_id).all()
    # print("Found " + str(todos.count()) + " todos!")
    for each_todo in todos:
      print("HI")
      db.session.add(each_todo)
      print("Checking completed status of todo: " + str(each_todo.id))
      each_todo.completed = True
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  return redirect(url_for('index'))

# Delete a reminder
@app.route('/todos/<todo_id>/delete', methods=['DELETE'])
def deleteTodo(todo_id):
  try:
    todo = Todo.query.get(todo_id)
    db.session.delete(todo)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  return jsonify({"success": True})

# Delete a reminder list
@app.route('/lists/<list_id>/delete', methods=['DELETE'])
def deleteList(list_id):
  try:
    todo_list = TodoList.query.get(list_id);
    db.session.delete(todo_list);
    db.session.commit();
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  return jsonify({"success": True})




# Get list of Todos for a specific Todos List
@app.route('/lists/<list_id>')
def get_list_todos(list_id):
  lists = TodoList.query.order_by('id').all()
  todos = Todo.query.filter_by(list_id = list_id).order_by('id').all()
  active_list = TodoList.query.get(list_id)
  return render_template('index.html', todos = todos, lists = lists, active_list = active_list)

# Front Page
@app.route('/')
def index():
  return redirect(url_for('get_list_todos', list_id=1))
