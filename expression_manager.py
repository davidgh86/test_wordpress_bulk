import random
import re

# Constants for the expression generation
OPERATORS = ["AND", "OR", "NOT"]
PREDICATE_FORMAT = "P{}"
MAX_PREDICATES = 5
MAX_DEPTH = 2


class ExpressionNode:
    def __init__(self, value, left=None, right=None):
        self.value = value  # Can be "AND", "OR", "NOT", or a predicate
        self.left = left  # Left child node
        self.right = right  # Right child node (only for binary operators)

    def is_operator(self):
        return self.value in OPERATORS

    def is_unary(self):
        return self.value == "NOT"

    def evaluate(self, truth_values):
        """Evaluate the expression based on the provided truth values."""
        if self.is_operator():
            if self.is_unary():  # Handling NOT operation
                return not self.left.evaluate(truth_values)
            elif self.value == "AND":  # Handling AND operation
                return self.left.evaluate(truth_values) and self.right.evaluate(truth_values)
            elif self.value == "OR":  # Handling OR operation
                return self.left.evaluate(truth_values) or self.right.evaluate(truth_values)
        else:
            # Lookup in truth_values dictionary for predicates
            return truth_values.get(self.value, False)

    def __str__(self):
        """Recursively convert expression tree to string representation."""
        if self.is_operator():
            if self.is_unary():
                return f"NOT ({self.left})"
            else:
                return f"({self.left} {self.value} {self.right})"
        else:
            return self.value


class ExpressionTree:
    def __init__(self, max_depth=MAX_DEPTH):
        self.max_depth = max_depth

    def generate_predicate(self):
        """Generate a random predicate."""
        return PREDICATE_FORMAT.format(random.randint(1, MAX_PREDICATES))

    def generate_expression(self, depth=0):
        """Recursively build an expression tree with random operators and predicates."""
        if depth >= self.max_depth or (depth > 0 and random.choice([True, False])):
            # Return a predicate as a leaf node
            return ExpressionNode(self.generate_predicate())

        # Decide whether to use a unary or binary operator
        operator = random.choice(OPERATORS)
        if operator == "NOT":
            # Unary operator: only one subtree
            left = self.generate_expression(depth + 1)
            return ExpressionNode(operator, left=left)
        else:
            # Binary operator: two subtrees
            left = self.generate_expression(depth + 1)
            right = self.generate_expression(depth + 1)
            return ExpressionNode(operator, left=left, right=right)

    def evaluate_expression(self, expression, truth_values):
        """Evaluate the expression based on truth values of predicates."""
        return expression.evaluate(truth_values)

    def parse_expression(self, expression_str):
        """Parse a string expression and convert it into an expression tree."""

        tokens = re.findall(r'\(|\)|AND|OR|NOT|P\d+', expression_str)
        return self._parse_tokens(tokens)

    def _parse_tokens(self, tokens):
        """Helper method to recursively parse tokens into an expression tree."""
        stack = []

        while tokens:
            token = tokens.pop(0)
            if token == '(':
                stack.append(token)
            elif token == ')':
                # Pop until matching '('
                expr = []
                while stack and stack[-1] != '(':
                    expr.append(stack.pop())
                stack.pop()  # Remove '('
                expr = expr[::-1]  # Reverse the order
                stack.append(self._build_expression_from_list(expr))
            elif token in OPERATORS or re.match(r'P\d+', token):
                stack.append(token)

        # Final parsing
        if len(stack) == 1 and isinstance(stack[0], ExpressionNode):
            return stack[0]
        else:
            return self._build_expression_from_list(stack)

    def _build_expression_from_list(self, expr_list):
        """Builds an ExpressionNode from a list of tokens in RPN order."""
        stack = []
        for token in expr_list:
            if re.match(r'P\d+', token):
                stack.append(ExpressionNode(token))
            elif token == "NOT":
                operand = stack.pop()
                stack.append(ExpressionNode(token, left=operand))
            elif token in ["AND", "OR"]:
                right = stack.pop()
                left = stack.pop()
                stack.append(ExpressionNode(token, left=left, right=right))

        return stack[0] if stack else None

    def generate_and_evaluate(self, predicate_generator):
        """Generate a random expression, evaluate it with random truth values, and display the results."""
        expression = self.generate_expression()

        # Generate random truth values for each predicate
        truth_values = {PREDICATE_FORMAT.format(i): predicate_generator() for i in range(1, MAX_PREDICATES + 1)}
        print(f"Generated Expression: {expression}")
        print(f"Truth Values: {truth_values}")
        print(f"Evaluation Result: {expression.evaluate(truth_values)}")
        return expression.evaluate(truth_values)


# Usage example with fixed truth values for testing
if __name__ == "__main__":
    expr_tree = ExpressionTree()

    # Example expression string
    expression_str = "((P1 OR P2) AND (P3 AND P4))"
    expression = expr_tree.parse_expression(expression_str)

    # Testing with custom truth values
    truth_values = {"P1": True, "P2": False, "P3": True, "P4": True}
    print(f"Parsed Expression: {expression}")
    print(f"Truth Values: {truth_values}")
    result = expression.evaluate(truth_values)
    print(f"Evaluation Result: {result}")
