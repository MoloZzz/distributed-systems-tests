import threading
import random
import math

# Граф (adjacency list)
graph = {
    0: [(1, 4), (2, 1)],
    1: [(0, 4), (2, 2), (3, 5)],
    2: [(0, 1), (1, 2), (3, 1)],
    3: [(1, 5), (2, 1), (4, 3)],
    4: [(3, 3)]
}

N = len(graph)
source = 0

# ---------- Алгоритм 1: найкоротші відстані ----------

dist = [math.inf] * N
dist[source] = 0

barrier = threading.Barrier(N)
lock = threading.Lock()

def relax(v):
    global dist
    for _ in range(N):
        local_min = dist[v]
        for u, w in graph[v]:
            local_min = min(local_min, dist[u] + w)

        barrier.wait()

        with lock:
            dist[v] = min(dist[v], local_min)

        barrier.wait()


threads = []
for v in range(N):
    t = threading.Thread(target=relax, args=(v,))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

print("Shortest distances:", dist)

# ---------- Алгоритм 2: мінімізація розфарбування ----------

colors = [random.randint(0, N) for _ in range(N)]
changed = True
iterations = 0

lock = threading.Lock()

def minimize(v):
    global colors, changed
    neighbor_colors = {colors[u] for u, _ in graph[v]}

    new_color = 0
    while new_color in neighbor_colors:
        new_color += 1

    if new_color < colors[v]:
        with lock:
            colors[v] = new_color
            changed = True


while True:
    changed = False
    threads = []

    for v in range(N):
        t = threading.Thread(target=minimize, args=(v,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    iterations += 1

    if not changed:
        break

print("Final coloring:", colors)
print("Iterations:", iterations)