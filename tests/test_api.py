import json


def create_todo(client, title='Test todo', description=''):
    """Helper to create a todo via the API."""
    payload = {'title': title}
    if description:
        payload['description'] = description
    return client.post(
        '/api/todos',
        data=json.dumps(payload),
        content_type='application/json',
    )


class TestCreateTodo:
    def test_create_with_title(self, client):
        response = create_todo(client, title='Buy groceries')
        assert response.status_code == 201
        data = response.get_json()
        assert 'todo' in data
        assert data['todo']['title'] == 'Buy groceries'
        assert data['todo']['completed'] is False
        assert data['todo']['id'] is not None

    def test_create_with_title_and_description(self, client):
        response = create_todo(client, title='Buy groceries', description='Milk and eggs')
        assert response.status_code == 201
        data = response.get_json()
        assert data['todo']['title'] == 'Buy groceries'
        assert data['todo']['description'] == 'Milk and eggs'

    def test_create_without_title_returns_400(self, client):
        response = client.post(
            '/api/todos',
            data=json.dumps({}),
            content_type='application/json',
        )
        assert response.status_code == 400
        data = response.get_json()
        assert data['error'] == 'Title is required'

    def test_create_with_empty_title_returns_400(self, client):
        response = client.post(
            '/api/todos',
            data=json.dumps({'title': ''}),
            content_type='application/json',
        )
        assert response.status_code == 400
        data = response.get_json()
        assert data['error'] == 'Title is required'

    def test_create_with_whitespace_title_returns_400(self, client):
        response = client.post(
            '/api/todos',
            data=json.dumps({'title': '   '}),
            content_type='application/json',
        )
        assert response.status_code == 400
        data = response.get_json()
        assert data['error'] == 'Title is required'


class TestGetTodos:
    def test_empty_list(self, client):
        response = client.get('/api/todos')
        assert response.status_code == 200
        data = response.get_json()
        assert data == {'todos': []}

    def test_list_multiple_todos(self, client):
        create_todo(client, title='Todo 1')
        create_todo(client, title='Todo 2')
        create_todo(client, title='Todo 3')

        response = client.get('/api/todos')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['todos']) == 3

    def test_filter_active(self, client):
        create_todo(client, title='Active todo')
        resp = create_todo(client, title='Completed todo')
        todo_id = resp.get_json()['todo']['id']
        client.patch(f'/api/todos/{todo_id}/toggle')

        response = client.get('/api/todos?status=active')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['todos']) == 1
        assert data['todos'][0]['title'] == 'Active todo'
        assert data['todos'][0]['completed'] is False

    def test_filter_completed(self, client):
        create_todo(client, title='Active todo')
        resp = create_todo(client, title='Completed todo')
        todo_id = resp.get_json()['todo']['id']
        client.patch(f'/api/todos/{todo_id}/toggle')

        response = client.get('/api/todos?status=completed')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['todos']) == 1
        assert data['todos'][0]['title'] == 'Completed todo'
        assert data['todos'][0]['completed'] is True

    def test_search_by_title_keyword(self, client):
        create_todo(client, title='Buy groceries')
        create_todo(client, title='Read a book')
        create_todo(client, title='Buy new shoes')

        response = client.get('/api/todos?q=Buy')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['todos']) == 2

    def test_search_by_description_keyword(self, client):
        create_todo(client, title='Shopping', description='Buy milk and eggs')
        create_todo(client, title='Reading', description='Finish chapter 5')

        response = client.get('/api/todos?q=milk')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['todos']) == 1
        assert data['todos'][0]['title'] == 'Shopping'

    def test_filter_and_search_combined(self, client):
        create_todo(client, title='Buy groceries')
        resp = create_todo(client, title='Buy shoes')
        todo_id = resp.get_json()['todo']['id']
        client.patch(f'/api/todos/{todo_id}/toggle')
        create_todo(client, title='Read a book')

        response = client.get('/api/todos?status=active&q=Buy')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['todos']) == 1
        assert data['todos'][0]['title'] == 'Buy groceries'
        assert data['todos'][0]['completed'] is False

    def test_search_no_results(self, client):
        create_todo(client, title='Buy groceries')

        response = client.get('/api/todos?q=nonexistent')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['todos']) == 0


class TestGetSingleTodo:
    def test_get_existing_todo(self, client):
        resp = create_todo(client, title='My todo')
        todo_id = resp.get_json()['todo']['id']

        response = client.get(f'/api/todos/{todo_id}')
        assert response.status_code == 200
        data = response.get_json()
        assert data['todo']['title'] == 'My todo'
        assert data['todo']['id'] == todo_id

    def test_get_nonexistent_todo_returns_404(self, client):
        response = client.get('/api/todos/999')
        assert response.status_code == 404
        data = response.get_json()
        assert data['error'] == 'Todo not found'


class TestUpdateTodo:
    def test_update_title(self, client):
        resp = create_todo(client, title='Old title')
        todo_id = resp.get_json()['todo']['id']

        response = client.put(
            f'/api/todos/{todo_id}',
            data=json.dumps({'title': 'New title'}),
            content_type='application/json',
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['todo']['title'] == 'New title'

    def test_update_description(self, client):
        resp = create_todo(client, title='My todo')
        todo_id = resp.get_json()['todo']['id']

        response = client.put(
            f'/api/todos/{todo_id}',
            data=json.dumps({'description': 'Updated description'}),
            content_type='application/json',
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['todo']['description'] == 'Updated description'

    def test_update_completed(self, client):
        resp = create_todo(client, title='My todo')
        todo_id = resp.get_json()['todo']['id']

        response = client.put(
            f'/api/todos/{todo_id}',
            data=json.dumps({'completed': True}),
            content_type='application/json',
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['todo']['completed'] is True

    def test_update_nonexistent_todo_returns_404(self, client):
        response = client.put(
            '/api/todos/999',
            data=json.dumps({'title': 'Updated'}),
            content_type='application/json',
        )
        assert response.status_code == 404
        data = response.get_json()
        assert data['error'] == 'Todo not found'


class TestDeleteTodo:
    def test_delete_existing_todo(self, client):
        resp = create_todo(client, title='To delete')
        todo_id = resp.get_json()['todo']['id']

        response = client.delete(f'/api/todos/{todo_id}')
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'Todo deleted'

    def test_deleted_todo_is_gone(self, client):
        resp = create_todo(client, title='To delete')
        todo_id = resp.get_json()['todo']['id']

        client.delete(f'/api/todos/{todo_id}')

        response = client.get(f'/api/todos/{todo_id}')
        assert response.status_code == 404

    def test_delete_nonexistent_todo_returns_404(self, client):
        response = client.delete('/api/todos/999')
        assert response.status_code == 404
        data = response.get_json()
        assert data['error'] == 'Todo not found'


class TestToggleTodo:
    def test_toggle_false_to_true(self, client):
        resp = create_todo(client, title='My todo')
        todo_id = resp.get_json()['todo']['id']

        response = client.patch(f'/api/todos/{todo_id}/toggle')
        assert response.status_code == 200
        data = response.get_json()
        assert data['todo']['completed'] is True

    def test_toggle_true_to_false(self, client):
        resp = create_todo(client, title='My todo')
        todo_id = resp.get_json()['todo']['id']

        # First toggle: False -> True
        client.patch(f'/api/todos/{todo_id}/toggle')
        # Second toggle: True -> False
        response = client.patch(f'/api/todos/{todo_id}/toggle')
        assert response.status_code == 200
        data = response.get_json()
        assert data['todo']['completed'] is False

    def test_toggle_nonexistent_todo_returns_404(self, client):
        response = client.patch('/api/todos/999/toggle')
        assert response.status_code == 404
        data = response.get_json()
        assert data['error'] == 'Todo not found'
