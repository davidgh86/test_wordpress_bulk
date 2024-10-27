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


# Ejemplo de uso
matchers = [
                {
                    "type": "operator",
                    "value": "NOT",
                    "order": 0
                },
                {
                    "type": "operator",
                    "value": "(",
                    "order": 1
                },
                {
                    "type": "operator",
                    "value": "(",
                    "order": 2
                },
                {
                    "type": "operator",
                    "value": "(",
                    "order": 3
                },
                {
                    "type": "operator",
                    "value": "(",
                    "order": 4
                },
                {
                    "type": "content",
                    "value": "sample_content",
                    "order": 5
                },
                {
                    "type": "operator",
                    "value": "OR",
                    "order": 6
                },
                {
                    "type": "operator",
                    "value": "(",
                    "order": 7
                },
                {
                    "type": "modified_date_min",
                    "value": "2023-11-10 16:50:54",
                    "order": 8
                },
                {
                    "type": "operator",
                    "value": "OR",
                    "order": 9
                },
                {
                    "type": "title",
                    "value": "sample_title",
                    "order": 10
                },
                {
                    "type": "operator",
                    "value": ")",
                    "order": 11
                },
                {
                    "type": "operator",
                    "value": ")",
                    "order": 12
                },
                {
                    "type": "operator",
                    "value": "OR",
                    "order": 13
                },
                {
                    "type": "operator",
                    "value": "(",
                    "order": 14
                },
                {
                    "type": "operator",
                    "value": "(",
                    "order": 15
                },
                {
                    "type": "modified_date_max",
                    "value": "2024-06-23 16:50:54",
                    "order": 16
                },
                {
                    "type": "operator",
                    "value": "AND",
                    "order": 17
                },
                {
                    "type": "tag",
                    "value": "sample_tag_3",
                    "order": 18
                },
                {
                    "type": "operator",
                    "value": ")",
                    "order": 19
                },
                {
                    "type": "operator",
                    "value": "OR",
                    "order": 20
                },
                {
                    "type": "datetime_min",
                    "value": "2024-04-06 16:50:54",
                    "order": 21
                },
                {
                    "type": "operator",
                    "value": ")",
                    "order": 22
                },
                {
                    "type": "operator",
                    "value": ")",
                    "order": 23
                },
                {
                    "type": "operator",
                    "value": "AND",
                    "order": 24
                },
                {
                    "type": "operator",
                    "value": "NOT",
                    "order": 25
                },
                {
                    "type": "operator",
                    "value": "(",
                    "order": 26
                },
                {
                    "type": "operator",
                    "value": "(",
                    "order": 27
                },
                {
                    "type": "operator",
                    "value": "(",
                    "order": 28
                },
                {
                    "type": "operator",
                    "value": "(",
                    "order": 29
                },
                {
                    "type": "title",
                    "value": "sample_title",
                    "order": 30
                },
                {
                    "type": "operator",
                    "value": "AND",
                    "order": 31
                },
                {
                    "type": "comment_status",
                    "value": "sample_comment_status_5",
                    "order": 32
                },
                {
                    "type": "operator",
                    "value": ")",
                    "order": 33
                },
                {
                    "type": "operator",
                    "value": "AND",
                    "order": 34
                },
                {
                    "type": "operator",
                    "value": "(",
                    "order": 35
                },
                {
                    "type": "category",
                    "value": "sample_category_3",
                    "order": 36
                },
                {
                    "type": "operator",
                    "value": "OR",
                    "order": 37
                },
                {
                    "type": "comment_count_min",
                    "value": 12,
                    "order": 38
                },
                {
                    "type": "operator",
                    "value": ")",
                    "order": 39
                },
                {
                    "type": "operator",
                    "value": ")",
                    "order": 40
                },
                {
                    "type": "operator",
                    "value": "OR",
                    "order": 41
                },
                {
                    "type": "operator",
                    "value": "(",
                    "order": 42
                },
                {
                    "type": "operator",
                    "value": "NOT",
                    "order": 43
                },
                {
                    "type": "operator",
                    "value": "(",
                    "order": 44
                },
                {
                    "type": "datetime_min",
                    "value": "2024-03-07 16:50:54",
                    "order": 45
                },
                {
                    "type": "operator",
                    "value": ")",
                    "order": 46
                },
                {
                    "type": "operator",
                    "value": "AND",
                    "order": 47
                },
                {
                    "type": "operator",
                    "value": "(",
                    "order": 48
                },
                {
                    "type": "comment_count_min",
                    "value": 55,
                    "order": 49
                },
                {
                    "type": "operator",
                    "value": "OR",
                    "order": 50
                },
                {
                    "type": "status",
                    "value": "sample_status_4",
                    "order": 51
                },
                {
                    "type": "operator",
                    "value": ")",
                    "order": 52
                },
                {
                    "type": "operator",
                    "value": ")",
                    "order": 53
                },
                {
                    "type": "operator",
                    "value": ")",
                    "order": 54
                },
                {
                    "type": "operator",
                    "value": ")",
                    "order": 55
                },
                {
                    "type": "operator",
                    "value": ")",
                    "order": 56
                },
                {
                    "type": "operator",
                    "value": ")",
                    "order": 57
                }
            ]

posts = [
            {
                "post_title": "Generated Post",
                "post_content": "Generated content for test case.",
                "post_status": "future",
                "post_category": [
                    "category_1"
                ],
                "post_tag": [
                    "tag_2"
                ],
                "post_date": "2024-09-04 16:50:54",
                "comment_count": 56,
                "comment_status": "closed",
                "post_type": "post",
                "modified_date": "2024-09-07 16:50:54"
            },
            {
                "post_title": "Generated Post",
                "post_content": "Generated content for test case.",
                "post_status": "future",
                "post_category": [
                    "category_4"
                ],
                "post_tag": [
                    "tag_1"
                ],
                "post_date": "2024-08-26 16:50:54",
                "comment_count": 74,
                "comment_status": "closed",
                "post_type": "page",
                "modified_date": "2024-07-17 16:50:54"
            },
            {
                "post_title": "Generated Post",
                "post_content": "Generated content for test case.",
                "post_status": "future",
                "post_category": [
                    "category_1"
                ],
                "post_tag": [
                    "tag_2"
                ],
                "post_date": "2023-12-19 16:50:54",
                "comment_count": 0,
                "comment_status": "closed",
                "post_type": "post",
                "modified_date": "2024-08-29 16:50:54"
            },
            {
                "post_title": "Generated Post",
                "post_content": "Generated content for test case.",
                "post_status": "publish",
                "post_category": [
                    "category_2"
                ],
                "post_tag": [
                    "tag_1"
                ],
                "post_date": "2024-07-17 16:50:54",
                "comment_count": 6,
                "comment_status": "open",
                "post_type": "post",
                "modified_date": "2024-01-29 16:50:54"
            },
            {
                "post_title": "Generated Post",
                "post_content": "Generated content for test case.",
                "post_status": "draft",
                "post_category": [
                    "category_2"
                ],
                "post_tag": [
                    "tag_1"
                ],
                "post_date": "2024-06-30 16:50:54",
                "comment_count": 51,
                "comment_status": "closed",
                "post_type": "page",
                "modified_date": "2023-12-06 16:50:54"
            }
        ]


if __name__ == "__main__":
    for i in range(len(posts)):
        print(f"{i}-. {evaluate_matchers(matchers, posts[1])}")
