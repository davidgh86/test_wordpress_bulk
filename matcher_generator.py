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
    """Genera un caso de prueba completo."""
    # Generar configuración del scheduler
    matchers = []
    num_matchers = random.randint(1, 5)  # Número aleatorio de condiciones

    for i in range(num_matchers):
        matcher_type = random.choice(["tag", "category", "status", "datetime_min", "operator"])

        if matcher_type == "tag":
            matcher = {
                "type": "tag",
                "value": random.choice(TAGS),
                "order": i
            }
        elif matcher_type == "category":
            matcher = {
                "type": "category",
                "value": random.choice(CATEGORIES),
                "order": i
            }
        elif matcher_type == "status":
            matcher = {
                "type": "status",
                "value": random.choice(STATES),
                "order": i
            }
        elif matcher_type == "datetime_min":
            matcher = {
                "type": "datetime_min",
                "value": random_date(datetime(2022, 1, 1), datetime(2023, 1, 1)).strftime(DATE_FORMAT),
                "order": i
            }
        else:  # Operator
            matcher = {
                "type": "operator",
                "value": random.choice(OPERATORS),
                "order": i
            }
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
    for matcher in matchers:
        if matcher['type'] == 'tag' and matcher['value'] not in post['post_tag']:
            return False
        if matcher['type'] == 'category' and matcher['value'] not in post['post_category']:
            return False
        if matcher['type'] == 'status' and matcher['value'] != post['post_status']:
            return False
        if matcher['type'] == 'datetime_min' and post['post_date'] < matcher['value']:
            return False
        # No se evalúan operadores en este ejemplo simplificado
    return True
