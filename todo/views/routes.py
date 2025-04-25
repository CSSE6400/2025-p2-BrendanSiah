from flask import Blueprint, jsonify, request
from todo.models import db
from todo.models.todo import Todo
from datetime import datetime
 
api = Blueprint('api', __name__, url_prefix='/api/v1') 

TEST_ITEM = {
    "id": 1,
    "title": "Watch CSSE6400 Lecture",
    "description": "Watch the CSSE6400 lecture on ECHO360 for week 1",
    "completed": True,
    "deadline_at": "2023-02-27T00:00:00",
    "created_at": "2023-02-20T00:00:00",
    "updated_at": "2023-02-20T00:00:00"
}

### Added to ensure the request only contains allowed fields
ALLOWED_FIELDS = ['title', 'description', 'completed', 'deadline_at']
 
@api.route('/health') 
def health():
    """Return a status of 'ok' if the server is running and listening to request"""
    return jsonify({"status": "ok"})


@api.route('/todos', methods=['GET'])
def get_todos():
    todos = Todo.query.all()
    result = []
    for todo in todos:
        result.append(todo.to_dict())
    return jsonify(result)

@api.route('/todos/<int:todo_id>', methods=['GET'])
def get_todo(todo_id):
    todo = Todo.query.get(todo_id)
    if todo is None:
        return jsonify({'error': 'Todo not found'}), 404
    return jsonify(todo.to_dict())

@api.route('/todos', methods=['POST'])
def create_todo():
    ### Added to check for unexpected fields
    for key in request.json.keys():
        if key not in ALLOWED_FIELDS:
            return jsonify({'error': 'Unexpected field: {key}'}), 400
    
    todo = Todo(
        title=request.json.get('title'),
        description=request.json.get('description'),
        completed=request.json.get('completed', False),
    )
    
    ### Typos
    ### if 'deadine_at' in request.json:
    ###    todo.deadline_at = datetime.fromisoformat(request.json/get('deadline_at'))
    if 'deadline_at' in request.json:
        todo.deadline_at = datetime.fromisoformat(request.json.get('deadline_at'))

    ### Added to ensure title is not missing
    if not request.json.get('title'):
        return jsonify({'error': 'Title is required'}), 400

    # Adds a new record to the database or will update an existing record.
    db.session.add(todo)
    # Commits the change to the database.
    # This must be called for the changes to be saved.
    db.session.commit()
    return jsonify(todo.to_dict()), 201

@api.route('/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    todo = Todo.query.get(todo_id)
    if todo is None:
        return jsonify({'error': 'Todo not found'}), 404
    
    ### Added to reject ID modifications
    if 'id' in request.json and request.json['id'] != todo_id:
        return jsonify({'error': 'ID cannot be modified'}), 400
    
    ### Added to check for unexpected fields
    for key in request.json.keys():
        if key not in ALLOWED_FIELDS:
            return jsonify({'error': 'Unexpected field: {key}'}), 400

    todo.title = request.json.get('title', todo.title)
    todo.description = request.json.get('description', todo.description)
    todo.completed = request.json.get('completed', todo.completed)
    todo.deadline_at = request.json.get('deadline_at', todo.deadline_at)
    db.session.commit()

    return jsonify(todo.to_dict())

@api.route('/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    todo = Todo.query.get(todo_id)
    if todo is None:
        ### return jsonify({'error': 'Todo not found'}), 200
        ### -> should return 404
        return jsonify({'error': 'Todo not found'}), 404
    
    db.session.delete(todo)
    db.session.commit()
    return jsonify(todo.to_dict()), 200
 
