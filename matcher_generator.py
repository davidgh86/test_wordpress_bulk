import json
import random
from datetime import datetime, timedelta
from generador_expresiones import generate_expression, OPERATORS  # Assuming this script is saved as expression_generator.py

# Available matcher types
MATCHER_TYPES = [
    "tag", "category", "status", "datetime_min", "datetime_max",
    "title", "author", "content", "slug", "comment_count_min",
    "comment_count_max", "comment_status", "modified_date_min",
    "modified_date_max", "post_type"
]

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
MAX_PREDICATES = 20
PREDICATE_FORMAT = "P{}"


def generate_matcher(matcher_type, order):
    """Generate a matcher based on the type."""
    if matcher_type == "datetime_min":
        value = (datetime.now() - timedelta(days=random.randint(1, 365))).strftime(DATE_FORMAT)
    elif matcher_type == "datetime_max":
        value = (datetime.now() + timedelta(days=random.randint(1, 365))).strftime(DATE_FORMAT)
    elif matcher_type in ["tag", "category", "status", "comment_status", "post_type"]:
        value = f"sample_{matcher_type}_{random.randint(1, 5)}"
    elif matcher_type in ["title", "author", "content", "slug"]:
        value = f"sample_{matcher_type}"
    elif matcher_type in ["comment_count_min", "comment_count_max"]:
        value = random.randint(0, 100)
    elif matcher_type in ["modified_date_min", "modified_date_max"]:
        value = (datetime.now() - timedelta(days=random.randint(1, 365))).strftime(DATE_FORMAT)
    else:
        value = ""
    return {"type": matcher_type, "value": value, "order": order}


def generate_post():
    """Generate a random post with values for various fields."""
    post_date = (datetime.now() - timedelta(days=random.randint(1, 365))).strftime(DATE_FORMAT)
    return {
        "post_title": f"Generated Post",
        "post_content": "Generated content for test case.",
        "post_status": random.choice(["publish", "draft", "pending", "future"]),
        "post_category": [f"category_{random.randint(1, 5)}"],
        "post_tag": [f"tag_{random.randint(1, 5)}"],
        "post_date": post_date,
        "comment_count": random.randint(0, 100),
        "comment_status": random.choice(["open", "closed"]),
        "post_type": random.choice(["post", "page"]),
        "modified_date": (datetime.now() - timedelta(days=random.randint(1, 365))).strftime(DATE_FORMAT)
    }


def generate_test_case(case_name):
    """Generate a full test case with an expression, posts, and expected output."""
    expression_str = generate_expression()
    tokens = expression_str.split(" ")

    # Build matchers based on predicates in the expression
    matchers = []
    predicate_to_matcher = {}
    order = 0

    for token in tokens:
        if token.startswith("P"):  # Predicate, create a matcher
            if token not in predicate_to_matcher:
                matcher_type = random.choice(MATCHER_TYPES)
                matcher = generate_matcher(matcher_type, order)
                predicate_to_matcher[token] = matcher
                matchers.append(matcher)
            order += 1

    # Generate posts
    posts = [generate_post() for _ in range(5)]

    # Determine expected output by evaluating the posts against the matchers
    expected = []
    for idx, post in enumerate(posts):
        if evaluate_post_against_expression(post, tokens, predicate_to_matcher):
            expected.append(idx)

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


def evaluate_post_against_expression(post, tokens, predicate_to_matcher):
    """Evaluate whether a post satisfies the expression based on the matchers."""
    stack = []

    for token in tokens:
        if token in OPERATORS:
            if token == "NOT":
                stack.append(not stack.pop())
            elif token == "AND":
                stack.append(stack.pop() and stack.pop())
            elif token == "OR":
                stack.append(stack.pop() or stack.pop())
        elif token.startswith("P"):
            matcher = predicate_to_matcher[token]
            stack.append(evaluate_post_against_matcher(post, matcher))

    return stack[0] if stack else False


def evaluate_post_against_matcher(post, matcher):
    """Evaluate a single matcher against a post."""
    if matcher["type"] == "tag":
        return matcher["value"] in post["post_tag"]
    elif matcher["type"] == "category":
        return matcher["value"] in post["post_category"]
    elif matcher["type"] == "status":
        return matcher["value"] == post["post_status"]
    elif matcher["type"] == "datetime_min":
        return post["post_date"] >= matcher["value"]
    elif matcher["type"] == "datetime_max":
        return post["post_date"] <= matcher["value"]
    elif matcher["type"] == "comment_count_min":
        return post["comment_count"] >= matcher["value"]
    elif matcher["type"] == "comment_count_max":
        return post["comment_count"] <= matcher["value"]
    elif matcher["type"] == "comment_status":
        return matcher["value"] == post["comment_status"]
    elif matcher["type"] == "modified_date_min":
        return post["modified_date"] >= matcher["value"]
    elif matcher["type"] == "modified_date_max":
        return post["modified_date"] <= matcher["value"]
    elif matcher["type"] == "post_type":
        return matcher["value"] == post["post_type"]
    else:
        return False


def generate_test_cases(num_cases=5):
    cases = [generate_test_case(f"Test Case {i + 1}") for i in range(num_cases)]
    return cases


# Save test cases to a JSON file
if __name__ == "__main__":
    test_cases = generate_test_cases()
    with open("test_cases.json", "w") as f:
        json.dump(test_cases, f, indent=4)
