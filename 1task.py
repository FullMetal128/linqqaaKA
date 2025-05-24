import re
from itertools import product


def parse_polynomial(poly_str):
    """
    Парсит строку с многочленом Жегалкина и возвращает функцию от списка битов.
    Поддерживаются операции: ^ (XOR), & (AND)
    """

    def eval_poly(values):
        # Заменяем переменные на значения
        expr = poly_str
        for i in range(1, len(values) + 1):
            expr = expr.replace(f'x{i}', str(values[i - 1]))
        # Вычисляем выражение безопасно
        return eval(expr.replace('^', '^^'))  # XOR как ^

    return eval_poly


def apply_transition(state, feedback_func):
    """
    Применяет один шаг перехода к текущему состоянию регистра.
    """
    new_bit = feedback_func(state)
    return (new_bit,) + state[:-1]


def find_components(n, feedback_func):
    """
    Находит все компоненты связности автомата R(σ).
    Возвращает список словарей {путь, цикл}.
    """
    total_states = list(product([0, 1], repeat=n))
    visited = set()
    components = []

    for start_state in total_states:
        if start_state in visited:
            continue

        current = start_state
        component = []
        path = {}
        step = 0

        while True:
            if current in path:
                cycle_start = path[current]
                cycle = component[cycle_start:]
                break
            if current in visited:
                cycle = []
                break

            path[current] = step
            component.append(current)
            visited.add(current)
            step += 1
            current = apply_transition(current, feedback_func)

        components.append({
            'path': component,
            'cycle': cycle
        })

    return components


def save_components_to_file(components, filename):
    """
    Сохраняет найденные компоненты в файл.
    """
    with open(filename, 'a', encoding='utf-8-sig') as f:
        f.write("\n\n--- Компоненты связности ---\n")
        for i, comp in enumerate(components):
            f.write(f"Компонента {i + 1}:\n")
            f.write("Путь: " + str(comp['path']) + "\n")
            f.write("Цикл: " + str(comp['cycle']) + "\n")

# Правильное преобразование переменных x1..xn в s[0]..s[n-1]
def build_feedback_function(poly_str, n):
    def feedback_func(s):
        expr = poly_str
        # Замена всех x1, x2... на s[0], s[1]...
        expr = re.sub(r'x(\d+)', lambda m: f's[{int(m.group(1)) - 1}]', expr)
        # Замена ^ на ^
        expr = expr.replace('^', '^')
        return eval(expr, {'s': s})
    return feedback_func


def main():
    input_file = "input.txt"

    # Чтение данных из файла
    with open(input_file, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]

    n = int(lines[0].split('=')[1].strip())
    feedback_str = lines[1].split('=')[1].strip()
    complexity_str = lines[2].split('=')[1].strip()

    print(f"Длина регистра: {n}")
    print(f"Функция обратной связи: {feedback_str}")
    print(f"Функция усложнения: {complexity_str}")

    # Парсим функции
    feedback_func = build_feedback_function(feedback_str, n)

    # Поиск компонент связности
    components = find_components(n, feedback_func)

    # Сохранение результатов в файл
    save_components_to_file(components, input_file)
    print("Результаты сохранены в файл.")


if __name__ == "__main__":
    main()