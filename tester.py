import json
import requests
import base64
import pytest

# Variables globales
WP_URL = "http://bbbbb.local:10011/wp-json/wp/v2/"
PLUGIN_API_URL = "http://bbbbb.local:10011/wp-json/shuffler/v1/"
USERNAME = 'bbbbb'
PASSWORD = 'nunn fRps ls6M Hfvx nntU 5cQq'
NONCE = 'your-generated-nonce'

# Formar la cadena 'usuario:contraseña'
auth_string = f'{USERNAME}:{PASSWORD}'

# Codificar la cadena en Base64
auth_base64 = base64.b64encode(auth_string.encode()).decode()

HEADERS = {
    'X-WP-Nonce': NONCE,
    'Authorization': f'Basic {auth_base64}',
    'Content-Type': 'application/json'
}


class RESTAPIError(Exception):
    """Clase personalizada para errores de la API"""
    pass


# Borrar todos los posts
def delete_all_posts():
    url = WP_URL + 'posts?per_page=100'
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        raise RESTAPIError(f"Failed to retrieve posts: {response.text}")

    posts = response.json()
    for post in posts:
        delete_url = WP_URL + f'posts/{post["id"]}?force=true'
        delete_response = requests.delete(delete_url, headers=HEADERS)
        if delete_response.status_code != 200:
            raise RESTAPIError(f"Failed to delete post {post['id']}: {delete_response.text}")
        print(f"Deleted post {post['id']}")


# Borrar todos los schedulers
def delete_all_schedulers():
    url = PLUGIN_API_URL + 'schedulers'
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        raise RESTAPIError(f"Failed to retrieve schedulers: {response.text}")

    schedulers = response.json()
    for scheduler in schedulers:
        delete_url = PLUGIN_API_URL + f'scheduler/{scheduler["id"]}'
        delete_response = requests.delete(delete_url, headers=HEADERS)
        if delete_response.status_code != 200:
            raise RESTAPIError(f"Failed to delete scheduler {scheduler['id']}: {delete_response.text}")
        print(f"Deleted scheduler {scheduler['id']}")

# Crear un post con categorías y tags
def create_post(post_data):
    url = WP_URL + 'posts'

    category_ids = [create_category_if_not_exists(cat) for cat in post_data.get('post_category', [])]
    tag_ids = [create_tag_if_not_exists(tag) for tag in post_data.get('post_tag', [])]

    payload = {
        'title': post_data.get('post_title'),
        'content': post_data.get('post_content'),
        'status': post_data.get('post_status', 'draft'),
        'categories': category_ids,
        'tags': tag_ids
    }

    response = requests.post(url, json=payload, headers=HEADERS)
    if response.status_code != 201:
        raise RESTAPIError(f"Failed to create post: {response.text}")

    post_id = response.json()['id']
    print(f"Post created successfully with ID: {post_id}")
    return post_id

# Crear un scheduler
def create_expression(scheduler_data):
    url = PLUGIN_API_URL + 'scheduler'
    response = requests.post(url, json=scheduler_data, headers=HEADERS)
    if response.status_code != 200:
        raise RESTAPIError(f"Failed to create scheduler: {response.text}")

    print(f"Scheduler created successfully: {response.json()['message']}")
    return response.json()

# Obtener los IDs de los posts a los que aplica una expresión
def get_post_ids_by_expression(scheduler_id):
    url = PLUGIN_API_URL + f'scheduler-sql/{scheduler_id}'
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        raise RESTAPIError(f"Failed to get post IDs: {response.text}")

    post_ids = response.json().get('post_ids', [])
    print(f"Post IDs returned by expression: {post_ids}")
    return post_ids

# Verificar si una tag ya existe
def get_tag_id_by_name(tag_name):
    url = WP_URL + 'tags?search=' + tag_name
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        raise RESTAPIError(f"Failed to search tag: {response.text}")

    tags = response.json()
    if tags:
        return tags[0]['id']
    return None

# Crear una tag si no existe
def create_tag_if_not_exists(tag_name):
    tag_id = get_tag_id_by_name(tag_name)
    if tag_id:
        print(f"Tag '{tag_name}' already exists with ID: {tag_id}")
        return tag_id

    url = WP_URL + 'tags'
    payload = {'name': tag_name}
    response = requests.post(url, json=payload, headers=HEADERS)
    if response.status_code != 201:
        raise RESTAPIError(f"Failed to create tag: {response.text}")

    tag_id = response.json()['id']
    print(f"Tag created successfully with ID: {tag_id}")
    return tag_id

# Verificar si una categoría ya existe
def get_category_id_by_name(category_name):
    url = WP_URL + 'categories?search=' + category_name
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        raise RESTAPIError(f"Failed to search category: {response.text}")

    categories = response.json()
    if categories:
        return categories[0]['id']
    return None

# Crear una categoría si no existe
def create_category_if_not_exists(category_name):
    category_id = get_category_id_by_name(category_name)
    if category_id:
        print(f"Category '{category_name}' already exists with ID: {category_id}")
        return category_id

    url = WP_URL + 'categories'
    payload = {'name': category_name}
    response = requests.post(url, json=payload, headers=HEADERS)
    if response.status_code != 201:
        raise RESTAPIError(f"Failed to create category: {response.text}")

    category_id = response.json()['id']
    print(f"Category created successfully with ID: {category_id}")
    return category_id

# Borrar todas las tags
def delete_all_tags():
    url = WP_URL + 'tags?per_page=100'
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        raise RESTAPIError(f"Failed to retrieve tags: {response.text}")

    tags = response.json()
    for tag in tags:
        delete_url = WP_URL + f'tags/{tag["id"]}?force=true'
        delete_response = requests.delete(delete_url, headers=HEADERS)
        if delete_response.status_code != 200:
            raise RESTAPIError(f"Failed to delete tag {tag['id']}: {delete_response.text}")
        print(f"Deleted tag {tag['id']}")

# Borrar todas las categorías
# Verificar si la categoría es la predeterminada
def get_default_category_id():
    url = WP_URL + 'settings'
    response = requests.get(url, headers=HEADERS)

    if response.status_code != 200:
        raise RESTAPIError(f"Failed to retrieve WordPress settings: {response.text}")

    settings = response.json()
    return settings.get('default_category', 1)  # La categoría por defecto es la ID 1 en muchos casos


# Borrar todas las categorías excepto la predeterminada
def delete_all_categories():
    default_category_id = get_default_category_id()
    url = WP_URL + 'categories?per_page=100'
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        raise RESTAPIError(f"Failed to retrieve categories: {response.text}")

    categories = response.json()
    for category in categories:
        if category["id"] == default_category_id:
            print(f"Skipping default category {category['id']}")
            continue

        delete_url = WP_URL + f'categories/{category["id"]}?force=true'
        delete_response = requests.delete(delete_url, headers=HEADERS)
        if delete_response.status_code != 200:
            raise RESTAPIError(f"Failed to delete category {category['id']}: {delete_response.text}")
        print(f"Deleted category {category['id']}")

# Test principal usando pytest
@pytest.mark.parametrize("test_case", json.load(open('test_resources.json', 'r', encoding='utf-8')))
#@pytest.mark.parametrize("test_case", json.load(open('current.json', 'r', encoding='utf-8')))
def test_scheduler_system(test_case):
    try:
        delete_all_posts()
        delete_all_categories()
        delete_all_tags()
        delete_all_schedulers()

        scheduler_data = test_case["scheduler"]
        posts = test_case["posts"]
        expected_post_indices = test_case["expected"]

        # Crear el scheduler
        scheduler_response = create_expression(scheduler_data)
        scheduler_id = scheduler_response['scheduler_id']

        # Crear los posts asociados a este scheduler
        post_ids = []
        for post_data in posts:
            post_id = create_post(post_data)
            post_ids.append(str(post_id))

        # Comprobar si los IDs devueltos por la expresión coinciden con los esperados
        post_ids_by_expression = get_post_ids_by_expression(scheduler_id)
        expected_ids = [post_ids[i] for i in expected_post_indices]

        # Asertar que los IDs coincidan
        assert set(post_ids_by_expression) == set(expected_ids), f"Expected: {expected_ids}, Got: {post_ids_by_expression}"

    except RESTAPIError as e:
        pytest.fail(f"API request failed: {str(e)}")
    except Exception as e:
        pytest.fail(f"An unexpected error occurred: {str(e)}")
