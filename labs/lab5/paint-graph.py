import random

graph = {
    0: [1, 2],
    1: [0, 2, 3],
    2: [0, 1, 3],
    3: [1, 2, 4],
    4: [3]
}

N = len(graph)

colors = [random.randint(0, N) for _ in range(N)]

iterations = 0


def minimization(v):
    neighbor_colors = {colors[u] for u in graph[v]}
    c = 0
    while c in neighbor_colors:
        c += 1

    colors[v] = c


def is_stable():
    for v in range(N):
        neighbor_colors = {colors[u] for u in graph[v]}
        c = 0
        while c in neighbor_colors:
            c += 1
        if c != colors[v]:
            return False
    return True


while True:
    v = random.randint(0, N - 1)

    minimization(v)
    iterations += 1

    if is_stable():
        break


print("Final coloring:", colors)
print("Iterations:", iterations)