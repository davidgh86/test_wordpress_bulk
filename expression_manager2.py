import glob
import itertools
import json
import os
import random
import re

# Constants for expression generation
OPERATORS = ["AND", "OR", "NOT"]
PREDICATE_FORMAT = "P{}"
MAX_PREDICATES = 5
MAX_DEPTH = 2


class ExpressionNode:
    """Represents a node in an expression tree, which can be an operator or a predicate."""

    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right

    def is_operator(self):
        return self.value in OPERATORS

    def evaluate(self, truth_values):
        """Recursively evaluates the expression based on provided truth values."""
        if self.is_operator():
            if self.value == "NOT":
                return not self.left.evaluate(truth_values)
            elif self.value == "AND":
                return self.left.evaluate(truth_values) and self.right.evaluate(truth_values)
            elif self.value == "OR":
                return self.left.evaluate(truth_values) or self.right.evaluate(truth_values)
        else:
            return truth_values.get(self.value, False)

    def __str__(self):
        """Returns a string representation of the expression node."""
        if self.value == "NOT":
            return f"NOT ({self.left})"
        elif self.value in ["AND", "OR"]:
            return f"({self.left} {self.value} {self.right})"
        return str(self.value)


class ExpressionParser:
    """Parses a string expression and converts it into an expression tree."""

    def parse(self, expression_str):
        tokens = self.tokenize(expression_str)
        expression_tree = self._parse_tokens(tokens)
        if expression_tree is None:
            raise ValueError("Failed to parse expression. Check syntax.")
        return expression_tree

    def tokenize(self, expression_str):
        """Tokenizes the input expression string into components (operators, predicates, parentheses)."""
        return re.findall(r'\(|\)|AND|OR|NOT|P\d+', expression_str)

    def _parse_tokens(self, tokens):
        """Parses tokens into an expression tree using recursive descent parsing."""
        stack = []
        output = []

        for token in tokens:
            if token == "(":
                stack.append(token)
            elif token == ")":
                # Pop from stack until matching "("
                while stack and stack[-1] != "(":
                    output.append(stack.pop())
                if stack and stack[-1] == "(":
                    stack.pop()  # Remove the opening "("
            elif token in OPERATORS:
                # Ensure correct operator precedence and associativity
                while (stack and stack[-1] in OPERATORS and
                       self._precedence(stack[-1]) >= self._precedence(token)):
                    output.append(stack.pop())
                stack.append(token)
            else:
                # This is a predicate (like P1, P2, etc.)
                output.append(token)

        # Pop any remaining operators in the stack
        while stack:
            output.append(stack.pop())

        # Convert the output list (in postfix notation) into an expression tree
        return self._build_expression_from_postfix(output)

    def _precedence(self, operator):
        """Defines precedence of operators: NOT > AND > OR."""
        if operator == "NOT":
            return 3
        elif operator == "AND":
            return 2
        elif operator == "OR":
            return 1
        return 0

    def _build_expression_from_postfix(self, postfix_tokens):
        """Builds an expression tree from a postfix (RPN) expression list."""
        stack = []

        for token in postfix_tokens:
            if token in OPERATORS:
                if token == "NOT":
                    # NOT is a unary operator
                    operand = stack.pop()
                    stack.append(ExpressionNode(token, left=operand))
                else:
                    # AND and OR are binary operators
                    right = stack.pop()
                    left = stack.pop()
                    stack.append(ExpressionNode(token, left=left, right=right))
            else:
                # This is a predicate, add as a leaf node
                stack.append(ExpressionNode(token))

        # The final item on the stack should be the root of the expression tree
        return stack[0] if stack else None


class ExpressionTree:
    """Manages the generation and evaluation of random expressions."""

    def __init__(self, max_depth=MAX_DEPTH):
        self.max_depth = max_depth

    def generate_expression(self, depth=0):
        """Generates a random expression tree up to a specified depth."""
        if depth >= self.max_depth or (depth > 0 and random.choice([True, False])):
            return ExpressionNode(self.generate_predicate())

        operator = random.choice(OPERATORS)
        if operator == "NOT":
            left = self.generate_expression(depth + 1)
            return ExpressionNode(operator, left=left)
        else:
            left = self.generate_expression(depth + 1)
            right = self.generate_expression(depth + 1)
            return ExpressionNode(operator, left=left, right=right)

    def generate_predicate(self):
        """Generates a random predicate."""
        return PREDICATE_FORMAT.format(random.randint(1, MAX_PREDICATES))

    def evaluate_expression(self, expression, truth_values):
        """Evaluates an expression tree based on given truth values."""
        return expression.evaluate(truth_values)


class ExpressionManager:
    """Main class to manage expression generation, parsing, and evaluation."""

    def __init__(self):
        self.tree_generator = ExpressionTree()
        self.parser = ExpressionParser()

    def create_random_expression(self):
        """Creates a random expression tree, prints and evaluates it."""
        expression = self.tree_generator.generate_expression()
        return expression

    def parse_expression(self, expression_str):
        """Parses a string expression and evaluates it based on given truth values."""
        expression = self.parser.parse(expression_str)
        return expression


def get_first_matching_filename(directory="output", base_name="failed_generated_matcher_Test_Case"):
    # Define the search pattern for the files in the specified directory
    pattern = os.path.join(directory, f"{base_name}_*.json")

    # Find all files matching the pattern
    files = glob.glob(pattern)

    if not (files):
        return "current.json"

    # Sort files by the number extracted from the filename
    files_sorted = sorted(
        files,
        key=lambda file: int(re.search(rf"{base_name}_(\d+)\.json", file).group(1))
    )

    # Return the first file or None if no matching file is found
    return files_sorted[0] if files_sorted else None


def generar_combinaciones(n):
    # Genera todas las combinaciones de valores booleanos para `n` posiciones
    combinaciones = list(itertools.product([False, True], repeat=n))

    # Convierte cada combinación en un diccionario con claves "P1", "P2", etc.
    resultado = []
    for combinacion in combinaciones:
        diccionario = {f"P{i + 1}": valor for i, valor in enumerate(combinacion)}
        resultado.append(diccionario)

    return resultado

# Usage example
def test_evaluation_from_file():

    with open(get_first_matching_filename(), "r", encoding="utf-8") as f:
        schedulers = json.load(f)

    expression = ""
    i = 0
    for matcher in schedulers[0]["scheduler"]["matchers"]:
       if matcher["type"] == "operator":
           expression += " " + matcher["value"]
       else:
           i += 1
           expression += " P"+str(i)

    expression = expression.strip()

    manager = ExpressionManager()
    parsed = manager.parse_expression(expression)

    combianciones = generar_combinaciones(i)

    for comb in combianciones:
        print(f"Expression:\t{expression}")
        print(f"Parsed:\t{parsed}")
        print(f"Values:\t{comb}")
        print(f"evaluation:\t{parsed.evaluate(comb)}")

def test_test_evaluation():

    expression = "NOT ((P1 OR P2))"

    manager = ExpressionManager()
    parsed = manager.parse_expression(expression)

    combianciones = [
        {'P1': True, 'P2': True},
        {'P1': False, 'P2': True}
    ]

    for comb in combianciones:
        print(f"Expression:\t{expression}")
        print(f"Parsed:\t{parsed}")
        print(f"Values:\t{comb}")
        print(f"evaluation:\t{parsed.evaluate(comb)}")




