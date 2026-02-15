from datetime import datetime

from app.models import Todo
from app import db


class TestTodoCreation:
    def test_create_todo_with_title_only(self, db_session):
        todo = Todo(title='Buy groceries')
        db_session.add(todo)
        db_session.commit()

        saved = db_session.get(Todo, todo.id)
        assert saved is not None
        assert saved.title == 'Buy groceries'

    def test_create_todo_with_all_fields(self, db_session):
        todo = Todo(title='Buy groceries', description='Milk, eggs, bread')
        db_session.add(todo)
        db_session.commit()

        saved = db_session.get(Todo, todo.id)
        assert saved.title == 'Buy groceries'
        assert saved.description == 'Milk, eggs, bread'


class TestTodoDefaults:
    def test_description_defaults_to_empty_string(self, db_session):
        todo = Todo(title='Test todo')
        db_session.add(todo)
        db_session.commit()

        saved = db_session.get(Todo, todo.id)
        assert saved.description == ''

    def test_completed_defaults_to_false(self, db_session):
        todo = Todo(title='Test todo')
        db_session.add(todo)
        db_session.commit()

        saved = db_session.get(Todo, todo.id)
        assert saved.completed is False

    def test_created_at_is_set_automatically(self, db_session):
        before = datetime.utcnow()
        todo = Todo(title='Test todo')
        db_session.add(todo)
        db_session.commit()
        after = datetime.utcnow()

        saved = db_session.get(Todo, todo.id)
        assert saved.created_at is not None
        assert before <= saved.created_at <= after

    def test_updated_at_is_set_automatically(self, db_session):
        before = datetime.utcnow()
        todo = Todo(title='Test todo')
        db_session.add(todo)
        db_session.commit()
        after = datetime.utcnow()

        saved = db_session.get(Todo, todo.id)
        assert saved.updated_at is not None
        assert before <= saved.updated_at <= after


class TestTodoToDict:
    def test_to_dict_returns_all_keys(self, db_session):
        todo = Todo(title='Test todo', description='A description')
        db_session.add(todo)
        db_session.commit()

        result = todo.to_dict()
        expected_keys = {'id', 'title', 'description', 'completed', 'created_at', 'updated_at'}
        assert set(result.keys()) == expected_keys

    def test_to_dict_values_are_correct(self, db_session):
        todo = Todo(title='Test todo', description='A description')
        db_session.add(todo)
        db_session.commit()

        result = todo.to_dict()
        assert result['id'] == todo.id
        assert result['title'] == 'Test todo'
        assert result['description'] == 'A description'
        assert result['completed'] is False

    def test_to_dict_timestamps_are_strings(self, db_session):
        todo = Todo(title='Test todo')
        db_session.add(todo)
        db_session.commit()

        result = todo.to_dict()
        assert isinstance(result['created_at'], str)
        assert isinstance(result['updated_at'], str)


class TestTodoRepr:
    def test_repr_format(self, db_session):
        todo = Todo(title='Test todo')
        db_session.add(todo)
        db_session.commit()

        assert repr(todo) == f'<Todo {todo.id}: Test todo>'


class TestTodoTitleRequired:
    def test_create_todo_without_title_raises_error(self, db_session):
        import pytest
        todo = Todo()
        db_session.add(todo)
        with pytest.raises(Exception):
            db_session.commit()


class TestTodoCompletedToggle:
    def test_toggle_completed(self, db_session):
        todo = Todo(title='Test todo')
        db_session.add(todo)
        db_session.commit()
        assert todo.completed is False

        todo.completed = True
        db_session.commit()

        saved = db_session.get(Todo, todo.id)
        assert saved.completed is True

    def test_toggle_completed_back_to_false(self, db_session):
        todo = Todo(title='Test todo')
        todo.completed = True
        db_session.add(todo)
        db_session.commit()

        todo.completed = False
        db_session.commit()

        saved = db_session.get(Todo, todo.id)
        assert saved.completed is False
