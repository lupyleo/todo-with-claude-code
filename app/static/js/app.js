document.addEventListener('DOMContentLoaded', function () {
    const todoForm = document.getElementById('todo-form');
    const titleInput = document.getElementById('title-input');
    const descInput = document.getElementById('desc-input');
    const todoList = document.getElementById('todo-list');
    const searchBox = document.getElementById('search-box');
    const filterButtons = document.querySelectorAll('.filter-btn');
    const todoCount = document.getElementById('todo-count');

    let currentFilter = 'all';
    let searchTimeout = null;

    // Load todos on page load
    loadTodos();

    // Add todo form submit
    todoForm.addEventListener('submit', function (e) {
        e.preventDefault();
        const title = titleInput.value.trim();
        if (!title) return;

        fetch('/api/todos', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                title: title,
                description: descInput.value.trim()
            })
        })
            .then(function (r) { return r.json(); })
            .then(function () {
                titleInput.value = '';
                descInput.value = '';
                loadTodos();
            });
    });

    // Filter buttons
    filterButtons.forEach(function (btn) {
        btn.addEventListener('click', function () {
            filterButtons.forEach(function (b) { b.classList.remove('active'); });
            btn.classList.add('active');
            currentFilter = btn.dataset.filter;
            loadTodos();
        });
    });

    // Search with debounce
    searchBox.addEventListener('input', function () {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(function () {
            loadTodos();
        }, 300);
    });

    function loadTodos() {
        var url = '/api/todos';
        var params = [];

        if (currentFilter !== 'all') {
            params.push('status=' + currentFilter);
        }

        var query = searchBox.value.trim();
        if (query) {
            params.push('q=' + encodeURIComponent(query));
        }

        if (params.length > 0) {
            url += '?' + params.join('&');
        }

        fetch(url)
            .then(function (r) { return r.json(); })
            .then(function (data) {
                renderTodos(data.todos);
            });
    }

    function renderTodos(todos) {
        todoList.innerHTML = '';

        if (todos.length === 0) {
            todoList.innerHTML = '<li class="empty-state">No todos found</li>';
            todoCount.textContent = '';
            return;
        }

        todos.forEach(function (todo) {
            var li = document.createElement('li');
            li.className = 'todo-item' + (todo.completed ? ' completed' : '');
            li.dataset.id = todo.id;

            li.innerHTML =
                '<input type="checkbox" class="todo-checkbox" ' +
                (todo.completed ? 'checked' : '') + '>' +
                '<div class="todo-content">' +
                '<div class="todo-title">' + escapeHtml(todo.title) + '</div>' +
                (todo.description ? '<div class="todo-description">' + escapeHtml(todo.description) + '</div>' : '') +
                '</div>' +
                '<div class="todo-actions">' +
                '<button class="btn btn-edit" data-action="edit">Edit</button>' +
                '<button class="btn btn-danger" data-action="delete">Delete</button>' +
                '</div>';

            // Toggle checkbox
            li.querySelector('.todo-checkbox').addEventListener('change', function () {
                toggleTodo(todo.id);
            });

            // Edit button
            li.querySelector('[data-action="edit"]').addEventListener('click', function () {
                startEdit(li, todo);
            });

            // Delete button
            li.querySelector('[data-action="delete"]').addEventListener('click', function () {
                deleteTodo(todo.id);
            });

            todoList.appendChild(li);
        });

        var activeCount = todos.filter(function (t) { return !t.completed; }).length;
        todoCount.textContent = activeCount + ' item' + (activeCount !== 1 ? 's' : '') + ' remaining';
    }

    function toggleTodo(id) {
        fetch('/api/todos/' + id + '/toggle', { method: 'PATCH' })
            .then(function () { loadTodos(); });
    }

    function deleteTodo(id) {
        fetch('/api/todos/' + id, { method: 'DELETE' })
            .then(function () { loadTodos(); });
    }

    function startEdit(li, todo) {
        li.innerHTML =
            '<form class="edit-form">' +
            '<input type="text" class="edit-title" value="' + escapeAttr(todo.title) + '" placeholder="Title">' +
            '<input type="text" class="edit-desc" value="' + escapeAttr(todo.description || '') + '" placeholder="Description">' +
            '<div class="edit-actions">' +
            '<button type="submit" class="btn btn-save">Save</button>' +
            '<button type="button" class="btn btn-cancel">Cancel</button>' +
            '</div>' +
            '</form>';

        var form = li.querySelector('.edit-form');
        form.querySelector('.edit-title').focus();

        form.addEventListener('submit', function (e) {
            e.preventDefault();
            var newTitle = form.querySelector('.edit-title').value.trim();
            if (!newTitle) return;

            fetch('/api/todos/' + todo.id, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    title: newTitle,
                    description: form.querySelector('.edit-desc').value.trim()
                })
            })
                .then(function () { loadTodos(); });
        });

        form.querySelector('.btn-cancel').addEventListener('click', function () {
            loadTodos();
        });
    }

    function escapeHtml(text) {
        var div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    function escapeAttr(text) {
        return text.replace(/&/g, '&amp;').replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    }
});
