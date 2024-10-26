import random

# Constants for the expression generation
OPERATORS = ["AND", "OR", "NOT"]
PREDICATE_FORMAT = "P{}"
MAX_PREDICATES = 20
MAX_DEPTH = 5

class ExpressionNode:
    def __init__(self, value, left=None, right=None):
        self.value = value  # Can be "AND", "OR", "NOT", or a predicate
        self.left = left    # Left child node
        self.right = right  # Right child node (only for binary operators)

    def is_operator(self):
        return self.value in OPERATORS

    def is_unary(self):
        return self.value == "NOT"

    def evaluate(self, truth_values):
        """Evaluate the expression based on the provided truth values."""
        if self.is_operator():
            if self.is_unary():
                return not self.left.evaluate(truth_values)
            elif self.value == "AND":
                return self.left.evaluate(truth_values) and self.right.evaluate(truth_values)
            elif self.value == "OR":
                return self.left.evaluate(truth_values) or self.right.evaluate(truth_values)
        else:
            # Treat as predicate; lookup in truth_values dictionary
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
        if depth > self.max_depth or (depth > 0 and random.choice([True, False])):
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

    def generate_and_evaluate(self):
        """Generate a random expression, evaluate it with random truth values, and display the results."""
        expression = self.generate_expression()
        # Generate random truth values for each predicate
        truth_values = {PREDICATE_FORMAT.format(i): random.choice([True, False]) for i in range(1, MAX_PREDICATES + 1)}
        print(f"Generated Expression: {expression}")
        #print(f"Truth Values: {truth_values}")
        #print(f"Evaluation Result: {expression.evaluate(truth_values)}")


# Usage example

if __name__ == "__main__":
    for i in range(10):
        expr_tree = ExpressionTree()
        expr_tree.generate_and_evaluate()
