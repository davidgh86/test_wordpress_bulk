import requests

# Variables globales
WP_URL = "http://bbbbb.local:10011/wp-json/wp/v2/"
PLUGIN_API_URL = "http://bbbbb.local:10011/wp-json/shuffler/v1/"
USERNAME = 'bbbbb'
PASSWORD = '5APN rDyS KBAv 0XHs 9EIZ IvLd'
NONCE = 'your-generated-nonce'

HEADERS = {
    'X-WP-Nonce': NONCE,
    'Authorization': f'Basic {USERNAME}:{PASSWORD}',
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


# Crear un post específico
def create_post(post_data):
    url = WP_URL + 'posts'
    response = requests.post(url, json=post_data, headers=HEADERS)
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


# Función principal para correr los tests
def run_tests(test_data):

    for test_case in test_data:
        try:
            delete_all_posts()
            delete_all_schedulers()

            scheduler_data = test_case["scheduler"]
            posts = test_case["posts"]
            expected_post_indices = test_case["expected"]

            # Crear el scheduler
            scheduler_response = create_expression(scheduler_data)
            scheduler_id = scheduler_response['message']

            # Crear los posts asociados a este scheduler
            post_ids = []
            for post_data in posts:
                post_id = create_post(post_data)
                post_ids.append(post_id)

            # Comprobar si los IDs devueltos por la expresión coinciden con los esperados
            post_ids_by_expression = get_post_ids_by_expression(scheduler_id)
            expected_ids = [post_ids[i] for i in expected_post_indices]

            # Verificar la igualdad
            if set(post_ids_by_expression) == set(expected_ids):
                print(f"Test passed for scheduler {scheduler_id}")
            else:
                print(f"Test failed for scheduler {scheduler_id}")
                print(f"Expected: {expected_ids}, Got: {post_ids_by_expression}")

        except RESTAPIError as e:
            print(f"Error in API request: {str(e)}")
        except Exception as e:
            print(f"An unexpected error occurred: {str(e)}")


# Datos de prueba que usarás para testear
test_data = [
    {
        "scheduler": {
            "id": 1,
            "scheduler_name": "Expresión con Tag y AND",
            "cron_expression": "*/5 * * * *",
            "matchers": [
                {
                    "matcher_type": "tag",
                    "matcher_value": "tech",
                    "order": 0
                },
                {
                    "matcher_type": "operator",
                    "matcher_value": "AND",
                    "order": 1
                },
                {
                    "matcher_type": "category",
                    "matcher_value": "news",
                    "order": 2
                }
            ]
        },
        "posts": [
            {
                "post_title": "Post for Expresión con Tag y AND",
                "post_content": "Content to match expression for Expresión con Tag y AND",
                "post_status": "publish",
                "post_category": [1],
                "post_tag": ["tech"]
            },
            {
                "post_title": "Another post for Expresión con Tag y AND",
                "post_content": "Another content for Expresión con Tag y AND",
                "post_status": "future",
                "post_category": [2],
                "post_tag": ["news"]
            }
        ],
        "expected": [0]
    }
]

if __name__ == "__main__":
    run_tests(test_data)
