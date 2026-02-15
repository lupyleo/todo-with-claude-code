import json


class TestPageLoad:
    def test_index_returns_200(self, client):
        response = client.get('/')
        assert response.status_code == 200

    def test_index_content_type_is_html(self, client):
        response = client.get('/')
        assert 'text/html' in response.content_type

    def test_index_contains_todo_form(self, client):
        response = client.get('/')
        html = response.data.decode()
        assert 'id="todo-form"' in html

    def test_index_contains_title_input(self, client):
        response = client.get('/')
        html = response.data.decode()
        assert 'id="title-input"' in html

    def test_index_contains_desc_input(self, client):
        response = client.get('/')
        html = response.data.decode()
        assert 'id="desc-input"' in html

    def test_index_contains_todo_list(self, client):
        response = client.get('/')
        html = response.data.decode()
        assert 'id="todo-list"' in html

    def test_index_contains_search_box(self, client):
        response = client.get('/')
        html = response.data.decode()
        assert 'id="search-box"' in html

    def test_index_links_css(self, client):
        response = client.get('/')
        html = response.data.decode()
        assert 'style.css' in html

    def test_index_links_js(self, client):
        response = client.get('/')
        html = response.data.decode()
        assert 'app.js' in html


class TestFilterButtons:
    def test_has_three_filter_buttons(self, client):
        response = client.get('/')
        html = response.data.decode()
        assert html.count('class="filter-btn') == 3

    def test_filter_all_exists(self, client):
        response = client.get('/')
        html = response.data.decode()
        assert 'data-filter="all"' in html

    def test_filter_active_exists(self, client):
        response = client.get('/')
        html = response.data.decode()
        assert 'data-filter="active"' in html

    def test_filter_completed_exists(self, client):
        response = client.get('/')
        html = response.data.decode()
        assert 'data-filter="completed"' in html

    def test_filter_all_has_label(self, client):
        response = client.get('/')
        html = response.data.decode()
        assert '>All</button>' in html

    def test_filter_active_has_label(self, client):
        response = client.get('/')
        html = response.data.decode()
        assert '>Active</button>' in html

    def test_filter_completed_has_label(self, client):
        response = client.get('/')
        html = response.data.decode()
        assert '>Completed</button>' in html


class TestStaticFiles:
    def test_css_file_accessible(self, client):
        response = client.get('/static/css/style.css')
        assert response.status_code == 200

    def test_js_file_accessible(self, client):
        response = client.get('/static/js/app.js')
        assert response.status_code == 200


class TestFrontendApiIntegration:
    def test_page_loads_after_creating_todo(self, client):
        client.post(
            '/api/todos',
            data=json.dumps({'title': 'Test todo'}),
            content_type='application/json',
        )

        response = client.get('/')
        assert response.status_code == 200
        assert 'text/html' in response.content_type

    def test_api_available_from_same_app(self, client):
        response = client.get('/')
        assert response.status_code == 200

        api_response = client.get('/api/todos')
        assert api_response.status_code == 200
        data = api_response.get_json()
        assert 'todos' in data
