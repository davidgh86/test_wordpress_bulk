import requests
import random
import string
from datetime import datetime

# Variables globales
WP_URL = "http://bbbbb.local:10011/wp-json/wp/v2/"
PLUGIN_API_URL = "http://bbbbb.local:10011/wp-json/shuffler/v1/"
USERNAME = 'bbbbb'
PASSWORD = '5APN rDyS KBAv 0XHs 9EIZ IvLd'
NONCE = 'your-generated-nonce'  # Debes generar el nonce de WordPress

HEADERS = {
    'X-WP-Nonce': NONCE,
    'Authorization': f'Basic {USERNAME}:{PASSWORD}',
    'Content-Type': 'application/json'
}


# Generar un título aleatorio para los posts
def random_title():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))


# Crear un post en WordPress
def create_post():
    url = WP_URL + 'posts'
    data = {
        'title': random_title(),
        'content': 'This is a test post generated by Python script.',
        'status': 'publish'
    }
    response = requests.post(url, json=data, headers=HEADERS)

    if response.status_code == 201:
        print(f"Post created successfully with ID: {response.json()['id']}")
        return response.json()['id']
    else:
        print(f"Failed to create post: {response.text}")
        return None


# Crear una expresión booleana usando el plugin
def create_expression(scheduler_name, cron_expression, matchers):
    url = PLUGIN_API_URL + 'scheduler'
    data = {
        'scheduler_name': scheduler_name,
        'cron_expression': cron_expression,
        'matchers': matchers
    }

    response = requests.post(url, json=data, headers=HEADERS)

    if response.status_code == 200:
        print(f"Expression created successfully with Scheduler ID: {response.json()['message']}")
        return response.json()
    else:
        print(f"Failed to create expression: {response.text}")
        return None


# Obtener los IDs de los posts a los que aplica una expresión
def get_post_ids_by_expression(scheduler_id):
    url = PLUGIN_API_URL + f'scheduler-sql/{scheduler_id}'
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 200:
        post_ids = response.json().get('post_ids', [])
        print(f"Post IDs returned by expression: {post_ids}")
        return post_ids
    else:
        print(f"Failed to get post IDs: {response.text}")
        return None


# Aplicar el shuffling a los posts
def apply_shuffling(scheduler_id):
    url = PLUGIN_API_URL + f'shuffle-dates/{scheduler_id}'
    response = requests.post(url, headers=HEADERS)

    if response.status_code == 200:
        print(f"Shuffling applied successfully to posts with Scheduler ID: {scheduler_id}")
    else:
        print(f"Failed to apply shuffling: {response.text}")


# Función principal para ejecutar el generador
def main():
    # 1. Crear varios posts
    post_ids = []
    for _ in range(5):  # Genera 5 posts
        post_id = create_post()
        if post_id:
            post_ids.append(post_id)

    # 2. Crear una expresión booleana
    scheduler_name = "Test Scheduler"
    cron_expression = "*/5 * * * *"

    # Matchers example (you can adjust these matchers according to the needs)
    matchers = [
        {'type': 'tag', 'value': 'test-tag'},
        {'type': 'operator', 'value': 'AND'},
        {'type': 'category', 'value': 'Uncategorized'}
    ]

    # Create the expression
    scheduler = create_expression(scheduler_name, cron_expression, matchers)

    if scheduler:
        scheduler_id = scheduler.get('message')  # Adjust according to the actual response

        # 3. Obtener los IDs de los posts que aplican a la expresión
        post_ids = get_post_ids_by_expression(scheduler_id)

        # 4. Aplicar el shuffling de las fechas a los posts seleccionados
        apply_shuffling(scheduler_id)


if __name__ == '__main__':
    main()
