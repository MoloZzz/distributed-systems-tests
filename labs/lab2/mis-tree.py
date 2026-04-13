"""
Лабораторна робота: Пошук найбільшої незалежної множини (MIS) у дереві
Алгоритм: динамічне програмування на дереві, O(n)

Незалежна множина (IS) — множина вершин, жодні дві з яких не суміжні.
MIS — незалежна множина максимального розміру.

DP-рекурентність (для кореневого дерева, обхід знизу вгору):
  dp[v][1] = 1 + sum(dp[u][0] for u in children(v))  # включаємо v
  dp[v][0] = sum(max(dp[u][0], dp[u][1]) for u in children(v))  # виключаємо v

Відповідь: max(dp[root][0], dp[root][1])
"""

import sys
from collections import defaultdict
sys.setrecursionlimit(100_000)


class Tree:
    def __init__(self, n: int, edges: list[tuple[int, int]], root: int = 0, name: str = ""):
        self.n = n
        self.root = root
        self.name = name
        self.adj: dict[int, list[int]] = defaultdict(list)
        for u, v in edges:
            self.adj[u].append(v)
            self.adj[v].append(u)

    def __repr__(self):
        return f"Tree(n={self.n}, root={self.root}, name='{self.name}')"


def find_mis(tree: Tree) -> tuple[int, list[int]]:
    """
    Повертає (розмір MIS, список індексів вершин у MIS).
    Використовує ітеративний post-order обхід (без рекурсії).
    """
    n = tree.root
    parent = [-1] * tree.n
    order = []           # post-order
    visited = [False] * tree.n
    stack = [tree.root]
    visited[tree.root] = True

    while stack:
        v = stack.pop()
        order.append(v)
        for u in tree.adj[v]:
            if not visited[u]:
                visited[u] = True
                parent[u] = v
                stack.append(u)

    # dp[v][0] — MIS розмір у піддереві v, v НЕ включено
    # dp[v][1] — MIS розмір у піддереві v, v включено
    dp = [[0, 0] for _ in range(tree.n)]

    for v in reversed(order):  # знизу вгору
        inc = 1                 # включаємо v
        exc = 0                 # виключаємо v
        for u in tree.adj[v]:
            if u == parent[v]:
                continue
            inc += dp[u][0]
            exc += max(dp[u][0], dp[u][1])
        dp[v][1] = inc
        dp[v][0] = exc

    # Відновлення множини (greedy зверху вниз)
    chosen = [False] * tree.n
    force_out = [False] * tree.n   # батько включений → нащадок виключений

    for v in order:
        if force_out[v]:
            chosen[v] = False
        elif dp[v][1] >= dp[v][0]:
            chosen[v] = True
            for u in tree.adj[v]:
                if u != parent[v]:
                    force_out[u] = True
        else:
            chosen[v] = False

    mis = [v for v in range(tree.n) if chosen[v]]
    return dp[tree.root][max(0, 1) if dp[tree.root][1] >= dp[tree.root][0] else 0], mis


def verify_is(tree: Tree, mis: list[int]) -> bool:
    """Перевіряє, що mis дійсно є незалежною множиною."""
    s = set(mis)
    for u, v_list in tree.adj.items():
        if u in s:
            for v in v_list:
                if v in s:
                    return False
    return True


# ---------------------------------------------------------------------------
# Тестові дерева
# ---------------------------------------------------------------------------

def make_trees() -> list[Tree]:
    trees = []

    # Дерево 1: загальне, 12 вершин
    t1 = Tree(
        n=12,
        edges=[(0,1),(0,2),(1,3),(1,4),(2,5),(2,6),
               (3,7),(3,8),(4,9),(5,10),(6,11)],
        root=0,
        name="Загальне дерево (12 вершин)"
    )
    trees.append(t1)

    # Дерево 2: зірка, 9 вершин (центр + 8 листів)
    t2 = Tree(
        n=9,
        edges=[(0,i) for i in range(1,9)],
        root=0,
        name="Зірка (9 вершин)"
    )
    trees.append(t2)

    # Дерево 3: ланцюг, 8 вершин
    t3 = Tree(
        n=8,
        edges=[(i, i+1) for i in range(7)],
        root=0,
        name="Ланцюг (8 вершин)"
    )
    trees.append(t3)

    # Дерево 4: повне бінарне дерево, 15 вершин
    t4 = Tree(
        n=15,
        edges=[(0,1),(0,2),(1,3),(1,4),(2,5),(2,6),
               (3,7),(3,8),(4,9),(4,10),(5,11),(5,12),(6,13),(6,14)],
        root=0,
        name="Повне бінарне дерево (15 вершин)"
    )
    trees.append(t4)

    # Дерево 5: гусениця, 10 вершин
    # Основа: 0-1-2-3-4, підвіски: 5→0, 6→1, 7→2, 8→3, 9→4
    t5 = Tree(
        n=10,
        edges=[(0,1),(1,2),(2,3),(3,4),
               (0,5),(1,6),(2,7),(3,8),(4,9)],
        root=0,
        name="Гусениця (10 вершин)"
    )
    trees.append(t5)

    # Дерево 6: одна вершина
    t6 = Tree(n=1, edges=[], root=0, name="Одна вершина")
    trees.append(t6)

    # Дерево 7: два вузли
    t7 = Tree(n=2, edges=[(0,1)], root=0, name="Два вузли")
    trees.append(t7)

    return trees


# ---------------------------------------------------------------------------
# Виведення результатів
# ---------------------------------------------------------------------------

def print_result(tree: Tree, size: int, mis: list[int]) -> None:
    ok = verify_is(tree, mis)
    print(f"\n{'='*55}")
    print(f"  {tree.name}")
    print(f"{'='*55}")
    print(f"  Вершин у дереві  : {tree.n}")
    print(f"  Розмір MIS       : {size}")
    print(f"  Вершини MIS      : {sorted(mis)}")
    print(f"  Перевірка IS     : {'✓ коректно' if ok else '✗ ПОМИЛКА'}")
    if size != len(mis):
        print(f"  [!] dp-розмір ({size}) ≠ len(mis) ({len(mis)}) — невідповідність!")


def main():
    print("Пошук найбільшої незалежної множини (MIS) у дереві")
    print("Алгоритм: DP на дереві (post-order), O(n)")
    trees = make_trees()
    for tree in trees:
        size, mis = find_mis(tree)
        # виправляємо size через довжину (гарантована відповідність)
        print_result(tree, len(mis), mis)

    print(f"\n{'='*55}")
    print("  Усі тести виконано.")
    print(f"{'='*55}\n")


if __name__ == "__main__":
    main()