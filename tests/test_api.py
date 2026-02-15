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


class TestEdgeCases:
    def test_create_without_json_body(self, client):
        response = client.post('/api/todos', content_type='application/json')
        assert response.status_code in (400, 415, 500)

    def test_create_with_wrong_content_type(self, client):
        response = client.post(
            '/api/todos',
            data='title=Test',
            content_type='application/x-www-form-urlencoded',
        )
        assert response.status_code == 415

    def test_update_multiple_fields_at_once(self, client):
        resp = create_todo(client, title='Original', description='Old desc')
        todo_id = resp.get_json()['todo']['id']

        response = client.put(
            f'/api/todos/{todo_id}',
            data=json.dumps({
                'title': 'Updated',
                'description': 'New desc',
                'completed': True,
            }),
            content_type='application/json',
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['todo']['title'] == 'Updated'
        assert data['todo']['description'] == 'New desc'
        assert data['todo']['completed'] is True

    def test_deleted_todo_not_in_list(self, client):
        create_todo(client, title='Keep this')
        resp = create_todo(client, title='Delete this')
        todo_id = resp.get_json()['todo']['id']

        client.delete(f'/api/todos/{todo_id}')

        response = client.get('/api/todos')
        data = response.get_json()
        assert len(data['todos']) == 1
        assert data['todos'][0]['title'] == 'Keep this'

    def test_invalid_status_filter_returns_all(self, client):
        create_todo(client, title='Todo 1')
        create_todo(client, title='Todo 2')

        response = client.get('/api/todos?status=invalid')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['todos']) == 2

    def test_bulk_create_and_filter(self, client):
        for i in range(20):
            create_todo(client, title=f'Todo {i}')

        # Toggle every other one to completed
        list_resp = client.get('/api/todos')
        todos = list_resp.get_json()['todos']
        for i, todo in enumerate(todos):
            if i % 2 == 0:
                client.patch(f'/api/todos/{todo["id"]}/toggle')

        active_resp = client.get('/api/todos?status=active')
        active_todos = active_resp.get_json()['todos']
        assert len(active_todos) == 10

        completed_resp = client.get('/api/todos?status=completed')
        completed_todos = completed_resp.get_json()['todos']
        assert len(completed_todos) == 10

    def test_bulk_create_and_search(self, client):
        create_todo(client, title='Buy apples')
        create_todo(client, title='Buy bananas')
        create_todo(client, title='Read a book')
        create_todo(client, title='Write code')
        create_todo(client, title='Buy oranges')

        response = client.get('/api/todos?q=Buy')
        data = response.get_json()
        assert len(data['todos']) == 3
        for todo in data['todos']:
            assert 'Buy' in todo['title']

    def test_search_case_sensitivity(self, client):
        create_todo(client, title='Buy Groceries')
        create_todo(client, title='buy milk')

        # SQLite LIKE is case-insensitive for ASCII by default
        response = client.get('/api/todos?q=buy')
        data = response.get_json()
        assert len(data['todos']) == 2

    def test_create_returns_timestamps(self, client):
        response = create_todo(client, title='Test timestamps')
        data = response.get_json()
        assert data['todo']['created_at'] is not None
        assert data['todo']['updated_at'] is not None

    def test_api_responses_are_json(self, client):
        response = create_todo(client, title='Test json')
        assert 'application/json' in response.content_type

        response = client.get('/api/todos')
        assert 'application/json' in response.content_type
