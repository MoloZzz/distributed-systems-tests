import random

def luby_algorithm(adj_list):
    """
    Реалізація алгоритму Luby для пошуку максимальної незалежної множини.
    adj_list: словник {вершина: [список сусідів]}
    """
    # Активні вершини
    active_vertices = set(adj_list.keys())
    MIS = set()

    while active_vertices:
        # Генеруємо випадкові пріоритети для активних вершин
        priorities = {v: random.random() for v in active_vertices}

        # Кандидати у MIS
        candidates = set()
        for v in active_vertices:
            higher_than_neighbors = True
            for u in adj_list[v]:
                if u in active_vertices and priorities[u] >= priorities[v]:
                    higher_than_neighbors = False
                    break
            if higher_than_neighbors:
                candidates.add(v)

        # Додаємо кандидатів у MIS
        MIS.update(candidates)

        # Видаляємо кандидатів та їх сусідів з активних вершин
        to_remove = set(candidates)
        for v in candidates:
            to_remove.update(adj_list[v])

        active_vertices -= to_remove

    return MIS


# === Приклад використання ===
if __name__ == "__main__":
    # Граф у вигляді списку суміжності
    graph = {
        1: [2, 3],
        2: [1, 3, 4],
        3: [1, 2, 4],
        4: [2, 3, 5],
        5: [4]
    }

    mis = luby_algorithm(graph)
    print("Розмір MIS:", len(mis))
    print("Вершини MIS:", mis)
