from flask import Blueprint, request, jsonify
from app import db
from app.models import Todo

todo_bp = Blueprint('todo', __name__)


@todo_bp.route('/api/todos', methods=['GET'])
def get_todos():
    query = Todo.query
    status = request.args.get('status')
    keyword = request.args.get('q')

    if status == 'active':
        query = query.filter_by(completed=False)
    elif status == 'completed':
        query = query.filter_by(completed=True)

    if keyword:
        pattern = f'%{keyword}%'
        query = query.filter(
            db.or_(
                Todo.title.like(pattern),
                Todo.description.like(pattern),
            )
        )

    todos = query.all()
    return jsonify({'todos': [todo.to_dict() for todo in todos]}), 200


@todo_bp.route('/api/todos', methods=['POST'])
def create_todo():
    data = request.get_json()
    title = data.get('title', '').strip() if data else ''

    if not title:
        return jsonify({'error': 'Title is required'}), 400

    description = data.get('description', '') if data else ''
    todo = Todo(title=title, description=description)
    db.session.add(todo)
    db.session.commit()

    return jsonify({'todo': todo.to_dict()}), 201


@todo_bp.route('/api/todos/<int:todo_id>', methods=['GET'])
def get_todo(todo_id: int):
    todo = db.session.get(Todo, todo_id)
    if not todo:
        return jsonify({'error': 'Todo not found'}), 404

    return jsonify({'todo': todo.to_dict()}), 200


@todo_bp.route('/api/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id: int):
    todo = db.session.get(Todo, todo_id)
    if not todo:
        return jsonify({'error': 'Todo not found'}), 404

    data = request.get_json()
    if 'title' in data:
        todo.title = data['title']
    if 'description' in data:
        todo.description = data['description']
    if 'completed' in data:
        todo.completed = data['completed']

    db.session.commit()
    return jsonify({'todo': todo.to_dict()}), 200


@todo_bp.route('/api/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id: int):
    todo = db.session.get(Todo, todo_id)
    if not todo:
        return jsonify({'error': 'Todo not found'}), 404

    db.session.delete(todo)
    db.session.commit()
    return jsonify({'message': 'Todo deleted'}), 200


@todo_bp.route('/api/todos/<int:todo_id>/toggle', methods=['PATCH'])
def toggle_todo(todo_id: int):
    todo = db.session.get(Todo, todo_id)
    if not todo:
        return jsonify({'error': 'Todo not found'}), 404

    todo.completed = not todo.completed
    db.session.commit()
    return jsonify({'todo': todo.to_dict()}), 200
