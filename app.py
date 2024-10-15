import sys
from flask import Flask, abort, render_template, jsonify , request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://Emmanuel:Manos@localhost:5432/todosapp'
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class TodoList(db.Model):
  __tablename__ = 'todolists'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(), nullable=False)
  todos = db.relationship('Todo', backref='list', lazy=True)

  def __repr__(self):
    return f'<TodoList {self.id} {self.name}>'

class Todo(db.Model):
  __tablename__ = 'todos'
  id = db.Column(db.Integer, primary_key=True)
  description = db.Column(db.String(), nullable=False)
  completed = db.Column(db.Boolean, nullable=False, default=False)
  list_id = db.Column(db.Integer, db.ForeignKey('todolists.id'), nullable=False)

  def __repr__(self):
    return f'<Todo {self.id} {self.description}>'
  
  #many to many relation
order_items = db.Table('order_items',
    db.Column('order_id', db.Integer, db.ForeignKey('order.id'), primary_key=True),
    db.Column('product_id', db.Integer, db.ForeignKey('product.id'), primary_key=True)
)
#parent table
class Order(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  status = db.Column(db.String(), nullable=False)
  products = db.relationship('Product', secondary=order_items,
      backref=db.backref('orders', lazy=True))\
      
#Child table
class Product(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(), nullable=False)
    
with app.app_context():
   #Creates all tables only once
   db.create_all()

# Create Todo items and put them under the same todo list
@app.route('/todos/create', methods=['POST'])
def create_todo():
   error=False
   body={}
   error = False
   try: 
       description =  request.get_json()['description']
       list_id= request.get_json()['list_id']
       todo = Todo(description=description)
       active_list =db.session.get(TodoList,list_id) #TodoList.query.get(list_id) => Legacy code
       todo.list = active_list
       db.session.add(todo)
       db.session.commit()
       body['description'] = todo.description
   except:        
        error = True
        db.session.rollback()
        print(sys.exc_info())
   finally:
        db.session.close()           
        if  error == True:
            abort(400)
        else:            
            return jsonify(body)
        
# Set completed for Todo items        
@app.route('/todos/<todo_id>/set-completed',methods=['POST'])
def set_completed_todo(todo_id):
    try:
        completed = request.get_json()['completed']
        todo =db.session.get(Todo , todo_id)
        todo.completed = completed
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for('index'))

#Delete todo items by todo id
@app.route('/todos/<todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
  try:
    Todo.query.filter_by(id=todo_id).delete()
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return jsonify({ 'success': True })

#Create todo list 
@app.route('/lists/create', methods=['POST'])
def create_todolist():
   error=False
   body={}
   error = False
   try: 
       name =  request.get_json()['name']
       todolist = TodoList(name=name)
       db.session.add(todolist)
       db.session.commit()
       body['id'] = todolist.id
       body['name'] = todolist.name
   except:        
        error = True
        db.session.rollback()
        print(sys.exc_info())
   finally:
        db.session.close()           
        if  error == True:
            abort(400)
        else:            
            return jsonify(body)
        
#set todo list to completed
@app.route('/lists/<list_id>/set-completed', methods=['POST'])
def set_completed_list(list_id):
    error = False

    try:
        list = db.session.get(TodoList,list_id) #TodoList.query.get(list_id)
        for todo in list.todos:
            todo.completed = True

        db.session.commit()
    except:
        db.session.rollback()

        error = True
    finally:
        db.session.close()

    if error:
        abort(500)
    else:
        return '', 200
#
@app.route('/lists/<list_id>/delete', methods=['DELETE'])
def delete_list(list_id):
    error = False
    try:
        list =  db.session.get(TodoList,list_id)#TodoList.query.get(list_id)
        for todo in list.todos:
            db.session.delete(todo)
        
        db.session.delete(list)
        db.session.commit()
    except():
        db.session.rollback()
        error = True
    finally:
        db.session.close()
    if error:
        abort(500)
    else:
        return jsonify({'success': True})

@app.route('/lists/<list_id>')
def get_list_todos(list_id):
    lists =  db.session.query(TodoList).all() #TodoList.query.all()
    active_list =  db.session.get(TodoList,list_id)#TodoList.query.get(list_id)
    todos = Todo.query.filter_by(list_id=list_id).order_by('id').all()

    return render_template('index.html', todos=todos, lists=lists, active_list=active_list)


@app.route('/')
def index():
   return redirect(url_for('get_list_todos',list_id =1))

#always include this at the bottom of your code
if __name__ == '__main__':
   app.debug=True
   app.run(host="0.0.0.0", port=3000)