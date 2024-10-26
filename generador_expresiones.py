import random

OPERATORS = ["AND", "OR", "NOT"]
PREDICATE_FORMAT = "P{}"
MAX_PREDICATES = 20  # Limita la cantidad de predicados en una expresión
MAX_DEPTH = 5  # Máxima profundidad de anidación de paréntesis


def generate_predicate(pred_count):
    """Genera un predicado en formato 'Px'."""
    return PREDICATE_FORMAT.format(pred_count)


def generate_expression(depth=0):
    """Genera una expresión lógica válida con predicados, operadores y paréntesis."""
    if depth > MAX_DEPTH:
        # Si se ha alcanzado la profundidad máxima, devuelve un predicado simple
        return generate_predicate(random.randint(1, MAX_PREDICATES))

    expression = ""
    add_not = random.choice([True, False])

    if add_not:
        expression += "NOT "

    # Decide entre agregar un predicado o iniciar un paréntesis para más profundidad
    if random.choice([True, False]) or depth == 0:
        # Agregar predicado simple o expresión con paréntesis
        expression += generate_predicate(random.randint(1, MAX_PREDICATES))
    else:
        # Agregar expresión compleja entre paréntesis
        expression += f"( {generate_expression(depth + 1)} )"

    # Añadir un operador y otra expresión recursivamente, aleatoriamente
    if depth < MAX_DEPTH:
        operator = random.choice(["AND", "OR"])
        expression += f" {operator} {generate_expression(depth + 1)}"

    return expression

if __name__ == "__main__":
    for _ in range(5):  # Genera 5 ejemplos
        print(generate_expression())
