import json
import random
from datetime import datetime, timedelta

# Opciones de parámetros para los casos de prueba
TAGS = ["sports", "technology", "health", "news", "lifestyle"]
CATEGORIES = ["tech", "lifestyle", "news", "jobs", "state"]
STATES = ["publish", "draft", "pending", "future"]
OPERATORS = ["AND", "OR", "NOT", "(", ")"]
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

def random_date(start, end):
    """Genera una fecha aleatoria entre start y end."""
    return start + timedelta(
        seconds=random.randint(0, int((end - start).total_seconds())),
    )

def generate_case(case_name):
    """Genera un caso de prueba completo con todos los matcher types."""
    # Generar configuración del scheduler
    matchers = []
    num_matchers = random.randint(1, 5)  # Número aleatorio de condiciones

    for i in range(num_matchers):
        matcher_type = random.choice([
            "tag", "category", "status", "datetime_min", "datetime_max",
            "title", "author", "content", "slug", "comment_count_min",
            "comment_count_max", "comment_status", "modified_date_min",
            "modified_date_max", "post_type", "operator"
        ])

        if matcher_type == "tag":
            matcher = {"type": "tag", "value": random.choice(TAGS), "order": i}
        elif matcher_type == "category":
            matcher = {"type": "category", "value": random.choice(CATEGORIES), "order": i}
        elif matcher_type == "status":
            matcher = {"type": "status", "value": random.choice(STATES), "order": i}
        elif matcher_type == "datetime_min":
            matcher = {"type": "datetime_min", "value": random_date(datetime(2022, 1, 1), datetime(2023, 1, 1)).strftime(DATE_FORMAT), "order": i}
        elif matcher_type == "datetime_max":
            matcher = {"type": "datetime_max", "value": random_date(datetime(2022, 1, 1), datetime(2023, 1, 1)).strftime(DATE_FORMAT), "order": i}
        elif matcher_type == "title":
            matcher = {"type": "title", "value": "Generated", "order": i}
        elif matcher_type == "author":
            matcher = {"type": "author", "value": "author_name", "order": i}
        elif matcher_type == "content":
            matcher = {"type": "content", "value": "test", "order": i}
        elif matcher_type == "slug":
            matcher = {"type": "slug", "value": f"generated-post-{i}", "order": i}
        elif matcher_type == "comment_count_min":
            matcher = {"type": "comment_count_min", "value": str(random.randint(0, 5)), "order": i}
        elif matcher_type == "comment_count_max":
            matcher = {"type": "comment_count_max", "value": str(random.randint(5, 10)), "order": i}
        elif matcher_type == "comment_status":
            matcher = {"type": "comment_status", "value": random.choice(["open", "closed"]), "order": i}
        elif matcher_type == "modified_date_min":
            matcher = {"type": "modified_date_min", "value": random_date(datetime(2022, 1, 1), datetime(2023, 1, 1)).strftime(DATE_FORMAT), "order": i}
        elif matcher_type == "modified_date_max":
            matcher = {"type": "modified_date_max", "value": random_date(datetime(2022, 1, 1), datetime(2023, 1, 1)).strftime(DATE_FORMAT), "order": i}
        elif matcher_type == "post_type":
            matcher = {"type": "post_type", "value": random.choice(["post", "page"]), "order": i}
        else:  # Operator
            matcher = {"type": "operator", "value": random.choice(OPERATORS), "order": i}

        matchers.append(matcher)

    # Generar posts asociados a este caso
    posts = []
    num_posts = random.randint(1, 5)

    for j in range(num_posts):
        post = {
            "post_title": f"Generated Post {j} for {case_name}",
            "post_content": "Generated content for test case.",
            "post_status": random.choice(STATES),
            "post_category": [random.choice(CATEGORIES)],
            "post_tag": [random.choice(TAGS)],
            "post_date": random_date(datetime(2022, 1, 1), datetime(2023, 1, 1)).strftime(DATE_FORMAT),
            "post_comment_count": random.randint(0, 10),
            "post_modified_date": random_date(datetime(2022, 1, 1), datetime(2023, 1, 1)).strftime(DATE_FORMAT),
            "post_type": random.choice(["post", "page"]),
            "post_slug": f"generated-post-{j}",
            "post_comment_status": random.choice(["open", "closed"])
        }
        posts.append(post)

    # Calcular el expected basándose en los matchers
    expected = []
    for idx, post in enumerate(posts):
        if matches_conditions(post, matchers):
            expected.append(idx)

    # Configuración del caso de prueba
    return {
        "name": case_name,
        "scheduler": {
            "scheduler_name": f"Scheduler for {case_name}",
            "cron_expression": "*/10 * * * *",
            "matchers": matchers
        },
        "posts": posts,
        "expected": expected
    }


def matches_conditions(post, matchers):
    """Evalúa si el post cumple con las condiciones de los matchers."""
    for matcher in matchers:
        if matcher['type'] == 'tag' and matcher['value'] not in post['post_tag']:
            return False
        if matcher['type'] == 'category' and matcher['value'] not in post['post_category']:
            return False
        if matcher['type'] == 'status' and matcher['value'] != post['post_status']:
            return False
        if matcher['type'] == 'datetime_min' and post['post_date'] < matcher['value']:
            return False
        if matcher['type'] == 'datetime_max' and post['post_date'] > matcher['value']:
            return False
        if matcher['type'] == 'title' and matcher['value'].lower() not in post['post_title'].lower():
            return False
        if matcher['type'] == 'author' and matcher['value'] != "author_name":
            return False
        if matcher['type'] == 'content' and matcher['value'].lower() not in post['post_content'].lower():
            return False
        if matcher['type'] == 'slug' and matcher['value'].lower() != post['post_slug'].lower():
            return False
        if matcher['type'] == 'comment_count_min' and post['post_comment_count'] < int(matcher['value']):
            return False
        if matcher['type'] == 'comment_count_max' and post['post_comment_count'] > int(matcher['value']):
            return False
        if matcher['type'] == 'comment_status' and matcher['value'] != post['post_comment_status']:
            return False
        if matcher['type'] == 'modified_date_min' and post['post_modified_date'] < matcher['value']:
            return False
        if matcher['type'] == 'modified_date_max' and post['post_modified_date'] > matcher['value']:
            return False
        if matcher['type'] == 'post_type' and matcher['value'] != post['post_type']:
            return False
        # No se evalúan operadores en este ejemplo simplificado
    return True
