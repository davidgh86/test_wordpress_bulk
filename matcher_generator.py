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

    # Configuración del caso de prueba
    return {
        "name": case_name,
        "scheduler": {
            "scheduler_name": f"Scheduler for {case_name}",
            "cron_expression": "*/10 * * * *",
            "matchers": matchers
        },
        "posts": posts,
        "expected": [i for i in range(num_posts) if random.choice([True, False])]
    }


def generate_test_cases(num_cases=10):
    """Genera varios casos de prueba y los guarda en un archivo JSON."""
    test_cases = [generate_case(f"TestCase_{i}") for i in range(num_cases)]

    with open("generated_test_cases.json", "w") as f:
        json.dump(test_cases, f, indent=4)

    print(f"{num_cases} test cases generated and saved to generated_test_cases.json")


# Genera 10 casos de prueba y guárdalos en un archivo JSON
generate_test_cases(10)
