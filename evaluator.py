import glob
import json
import os
import re


def evaluate_matchers(matchers, post):
    stack = []

    def evaluate_condition(matcher, post):
        type_ = matcher["type"]
        value = matcher["value"]

        if type_ == "tag":
            return value in post.get("post_tag", [])
        elif type_ == "category":
            return value in post.get("post_category", [])
        elif type_ == "status":
            return post.get("post_status") == value
        elif type_ == "datetime_min":
            return post.get("post_date") >= value
        elif type_ == "datetime_max":
            return post.get("post_date") <= value
        elif type_ == "title":
            return value.lower() in post.get("post_title", "").lower()
        elif type_ == "author":
            # Assuming post has an "author" field to compare
            return post.get("author") == value
        elif type_ == "content":
            return value.lower() in post.get("post_content", "").lower()
        elif type_ == "slug":
            return post.get("post_name", "").lower() == value.lower()
        elif type_ == "comment_count_max":
            return post.get("comment_count", 0) <= int(value)
        elif type_ == "comment_count_min":
            return post.get("comment_count", 0) >= int(value)
        elif type_ == "comment_status":
            return post.get("comment_status") == value
        elif type_ == "modified_date_min":
            return post.get("modified_date") >= value
        elif type_ == "modified_date_max":
            return post.get("modified_date") <= value
        elif type_ == "post_type":
            return post.get("post_type") == value
        return False

    for matcher in matchers:
        if matcher["type"] == "operator":
            operator = matcher["value"]
            if operator in ["AND", "OR", "NOT"]:
                stack.append(operator)
            elif operator == "(":
                stack.append(operator)
            elif operator == ")":
                # Evaluate the expression inside the parentheses
                expr = []
                while stack and stack[-1] != "(":
                    expr.append(stack.pop())
                if stack:  # Remove the "(" if present
                    stack.pop()
                expr = expr[::-1]
                result = evaluate_expression(expr)
                stack.append(result)
        else:
            # It's a condition to evaluate against the post
            result = evaluate_condition(matcher, post)
            stack.append(result)

    # Evaluate the final expression
    return evaluate_expression(stack) if stack else False


def evaluate_expression(expr):
    stack = []
    i = 0
    while i < len(expr):
        if expr[i] == "NOT":
            if stack:
                operand = stack.pop()
                stack.append(not operand)
        elif expr[i] == "AND":
            if len(stack) >= 1 and i + 1 < len(expr):
                left = stack.pop()
                right = expr[i + 1]
                stack.append(left and right)
                i += 1
        elif expr[i] == "OR":
            if len(stack) >= 1 and i + 1 < len(expr):
                left = stack.pop()
                right = expr[i + 1]
                stack.append(left or right)
                i += 1
        else:
            stack.append(expr[i])
        i += 1
    return stack[0] if stack else False


def get_file_names(directory="output", base_name="failed_generated_matcher_Test_Case"):
    # Define the search pattern for the files in the specified directory
    pattern = os.path.join(directory, f"{base_name}_*.json")

    # Find all files matching the pattern
    files = glob.glob(pattern)

    # Sort files by the number extracted from the filename
    files_sorted = sorted(
        files,
        key=lambda file: int(re.search(rf"{base_name}_(\d+)\.json", file).group(1))
    )

    # Return the first file or None if no matching file is found
    return files_sorted


def get_json(path):
    with open(path, 'r') as file:
        data = json.load(file)
        return data

def get_matcher_and_posts(data):
    return {
        "matchers": data[0]["scheduler"]["matchers"],
        "posts": data[0]["posts"]
    }




if __name__ == "__main__":
    file_names = get_file_names()

    for file_name in file_names:
        data = get_json(file_name)
        matchers_and_posts = get_matcher_and_posts(data)
        posts = matchers_and_posts["posts"]
        matchers = matchers_and_posts["matchers"]
        indexes = []
        for i in range(len(posts)):
            is_matching = evaluate_matchers(matchers, posts[i])
            if is_matching:
                indexes.append(i)
        data[0]["expected"] = indexes
        with open(file_name, 'w') as file:
            json.dump(data, file, indent=4)
