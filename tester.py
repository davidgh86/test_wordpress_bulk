import glob
import json
import os
import re

import requests
import base64
import pytest
from _pytest.outcomes import Failed

from expression_manager2 import ExpressionManager
from matcher_generator2 import generate_test_cases, generate_test_case, evaluate_post_against_matcher

# Variables globales

HOSTNAME = "http://ccccc.local"
#HOSTNAME = "http://bbbbb.local:10011"

WP_URL = HOSTNAME + "/wp-json/wp/v2/"
PLUGIN_API_URL = HOSTNAME + "/wp-json/shuffler/v1/"

#USERNAME = 'bbbbb'
USERNAME = 'ccccc'

#PASSWORD = 'nunn fRps ls6M Hfvx nntU 5cQq'
PASSWORD = 't9by bUzR 0t5g 3HTk KB7T pxyr'

NONCE = 'your-generated-nonce'

# Formar la cadena 'usuario:contraseña'k
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
    page = 1
    while True:
        url = f"{WP_URL}posts?per_page=100&page={page}&status=any"
        response = requests.get(url, headers=HEADERS)

        if response.status_code != 200:
            raise RESTAPIError(f"Failed to retrieve posts: {response.text}")

        posts = response.json()
        if not posts:
            break  # No more posts to delete

        for post in posts:
            delete_url = WP_URL + f'posts/{post["id"]}?force=true'
            delete_response = requests.delete(delete_url, headers=HEADERS)
            if delete_response.status_code != 200:
                raise RESTAPIError(f"Failed to delete post {post['id']}: {delete_response.text}")
            print(f"Deleted post {post['id']}")
        page += 1


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


# Crear un comentario para un post
def create_comment(post_id, comment_content):
    url = WP_URL + 'comments'
    payload = {
        'post': post_id,
        'content': comment_content,
        'author_name': 'Test Author',  # Nombre del autor del comentario
        'author_email': 'test_author@example.com',  # Email del autor
    }

    response = requests.post(url, json=payload, headers=HEADERS)
    if response.status_code != 201:
        raise RESTAPIError(f"Failed to create comment: {response.text}")

    comment_id = response.json()['id']
    print(f"Comment created successfully with ID: {comment_id} for post ID: {post_id}")
    return comment_id



# Crear un post específico con categorías, tags y comentarios

def create_post(post_data):
    url = WP_URL + 'posts'

    # Obtén las categorías y etiquetas, creando las que no existan.
    category_ids = [create_category_if_not_exists(cat) for cat in post_data.get('post_category', [])]
    tag_ids = [create_tag_if_not_exists(tag) for tag in post_data.get('post_tag', [])]

    # Crea el payload con los nuevos valores incluidos, incluyendo fechas
    payload = {
        'title': post_data.get('post_title'),
        'content': post_data.get('post_content'),
        'status': post_data.get('post_status', 'draft'),
        'categories': category_ids,
        'tags': tag_ids,
        'date': post_data.get('post_date'),      # Fecha de publicación en UTC
        'modified': post_data.get('modified_date'),     # Fecha de modificación en UTC
        'slug': post_data.get('post_slug'),
        'author': post_data.get('author'),
        'comment_status': post_data.get('comment_status')
    }

    # Realiza la solicitud POST para crear el post
    response = requests.post(url, json=payload, headers=HEADERS)
    if response.status_code != 201:
        raise RESTAPIError(f"Failed to create post: {response.text}")

    post_id = response.json()['id']
    print(f"Post created successfully with ID: {post_id}")

    # Crear comentarios si se especifica comment_count
    if 'comment_count' in post_data:
        for i in range(post_data['comment_count']):
            create_comment(post_id, f"Test comment {i + 1}")

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


def get_post_count():
    url = WP_URL + 'posts'
    total_posts = 0
    page = 1

    while True:
        # Solicitar una página de resultados con todos los estados
        response = requests.get(f"{url}?per_page=100&status=any&page={page}", headers=HEADERS)

        if response.status_code != 200:
            raise RESTAPIError(f"Failed to retrieve post count: {response.text}")

        posts = response.json()
        total_posts += len(posts)

        # Si la longitud de posts es menor que el límite, significa que no hay más páginas
        if len(posts) < 100:
            break

        page += 1  # Avanzar a la siguiente página

    return total_posts


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


# Borrar todos los comentarios
def delete_all_comments():
    url = WP_URL + 'comments?per_page=100'

    # Get all comments
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        raise RESTAPIError(f"Failed to retrieve comments: {response.text}")

    comments = response.json()

    # Loop through each comment and delete it
    for comment in comments:
        delete_url = WP_URL + f'comments/{comment["id"]}?force=true'
        delete_response = requests.delete(delete_url, headers=HEADERS)
        if delete_response.status_code != 200:
            raise RESTAPIError(f"Failed to delete comment {comment['id']}: {delete_response.text}")
        print(f"Deleted comment {comment['id']}")


# Obtener todos los usuarios de WordPress
def get_all_users():
    url = WP_URL + 'users'
    response = requests.get(url, headers=HEADERS)

    if response.status_code != 200:
        raise RESTAPIError(f"Failed to retrieve users: {response.text}")

    users = response.json()
    result = dict()
    for user in users:
        result[user['id']] = user['name']
    return result


def get_next_filename(directory="output", base_name="failed_generated_matcher_Test_Case"):
    # Define el patrón completo con el directorio
    pattern = os.path.join(directory, f"{base_name}_*.json")

    # Encuentra todos los archivos que coinciden con el patrón en el directorio
    files = glob.glob(pattern)

    if not(files) or len(files)==0:
        return os.path.join(directory, f"{base_name}_1.json")

    # Extrae los números de cada archivo
    numbers = []
    for file in files:
        match = re.search(rf"{base_name}_(\d+)\.json", file)
        if match:
            numbers.append(int(match.group(1)))

    # Encuentra el siguiente número
    next_number = max(numbers) + 1 if numbers else 1
    next_file_name = os.path.join(directory, f"{base_name}_{next_number}.json")

    return next_file_name


def get_first_matching_filename(directory="output", base_name="failed_generated_matcher_Test_Case"):
    # Define the search pattern for the files in the specified directory
    pattern = os.path.join(directory, f"{base_name}_*.json")

    # Find all files matching the pattern
    files = glob.glob(pattern)

    if not(files):
        return "current.json"

    # Sort files by the number extracted from the filename
    files_sorted = sorted(
        files,
        key=lambda file: int(re.search(rf"{base_name}_(\d+)\.json", file).group(1))
    )

    # Return the first file or None if no matching file is found
    return files_sorted[0] if files_sorted else None

def recalculate_expected(test_case, users):
    posts = test_case["posts"]

    expression = ""
    matcher_evaluations = [dict() for _ in posts]

    result_evaluations = []

    i = 0
    for matcher in test_case["scheduler"]["matchers"]:
        if matcher["type"] == "operator":
            expression += " " + matcher["value"]
        else:
            i += 1
            expression += " P" + str(i)
            for j in range(len(posts)):
                matcher_evaluations[j]["P"+str(i)] = evaluate_post_against_matcher(posts[j], matcher, users)

    expression = expression.strip()

    manager = ExpressionManager()

    parsed = manager.parse_expression(expression)

    for i in range(len(matcher_evaluations)):
        if parsed.evaluate(matcher_evaluations[i]):
            result_evaluations.append(i)

    test_case["expected"] = result_evaluations
    return test_case


all_users = get_all_users()

testing_file = get_first_matching_filename()

# Test principal usando pytest
#@pytest.mark.parametrize("test_case", json.load(open('test_resources.json', 'r', encoding='utf-8')), ids= lambda val : f"{val["scheduler"]["scheduler_name"]}")
#@pytest.mark.parametrize("test_case", json.load(open('current.json', 'r', encoding='utf-8')), ids= lambda val : f"{val["scheduler"]["scheduler_name"]}")
#@pytest.mark.parametrize("test_case", json.load(open('current2.json', 'r', encoding='utf-8')), ids= lambda val : f"{val["scheduler"]["scheduler_name"]}")
@pytest.mark.parametrize("test_case", json.load(open(testing_file, 'r', encoding='utf-8')), ids= lambda val : f"{val["scheduler"]["scheduler_name"]}")
def test_scheduler_system(test_case):
    try:
        test_case_recalculated = recalculate_expected(test_case, all_users)
        execute_test(test_case_recalculated)

    except RESTAPIError as e:
        pytest.fail(f"API request failed: {str(e)}")
    except Exception as e:
        pytest.fail(f"An unexpected error occurred: {str(e)}")


def execute_test(test_case):
    delete_all_comments()
    delete_all_posts()
    delete_all_categories()
    delete_all_tags()
    delete_all_schedulers()
    # Assert initial post count is zero
    assert get_post_count() == 0, "Expected 0 posts at start, found otherwise."
    scheduler_data = test_case["scheduler"]
    posts = test_case["posts"]
    expected_post_indices = test_case["expected"]
    # Create Scheduler
    scheduler_response = create_expression(scheduler_data)
    scheduler_id = scheduler_response['scheduler_id']
    # Crear los posts asociados a este scheduler
    post_ids = []
    for post_data in posts:
        post_id = create_post(post_data)
        post_ids.append(str(post_id))
    assert get_post_count() == len(posts), f"Expected {len(posts)} posts created, but found different."
    # Comprobar si los IDs devueltos por la expresión coinciden con los esperados
    post_ids_by_expression = get_post_ids_by_expression(scheduler_id)
    expected_ids = [post_ids[i] for i in expected_post_indices]
    # Asertar que los IDs coincidan
    assert set(post_ids_by_expression) == set(expected_ids), f"Expected: {expected_ids}, Got: {post_ids_by_expression}"


def test_with_generated():
    generated_matcher = generate_test_case("Test case generated", all_users)
    try:
        test_scheduler_system(generated_matcher)
    except AssertionError as e:
        # Save the generated matcher JSON if the test fails
        with open("failed_generated_matcher.json", "w", encoding="utf-8") as f:
            json.dump(generated_matcher, f, ensure_ascii=False, indent=4)
        # Re-raise the assertion error to mark the test as failed
        raise e


# Generate test cases for 100 iterations with explicit "id" values
generated_cases = generate_test_cases(1, all_users)

# Parametrize the test with the generated cases and unique IDs
@pytest.mark.parametrize("generated_test_case", generated_cases, ids=lambda val: f"test_run_{val["scheduler"]["scheduler_name"]}")
def test_with_generated(generated_test_case):
    try:
        test_scheduler_system(generated_test_case)
    except (AssertionError, Failed, Exception) as e:
        # Save the generated matcher JSON if the test fails
        with open(get_next_filename(), "w", encoding="utf-8") as f:
            json.dump([generated_test_case], f, ensure_ascii=False, indent=4)
        # Re-raise the assertion error to mark the test as failed
        raise e

