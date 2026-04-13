import threading
import random
import copy

graph = {
    0: [1, 2],
    1: [0, 2, 3],
    2: [0, 1, 3],
    3: [1, 2, 4],
    4: [3]
}

N = len(graph)

colors = [random.randint(0, N) for _ in range(N)]
new_colors = colors.copy()

barrier = threading.Barrier(N)
lock = threading.Lock()

changed_global = [False]
stop_flag = [False]

def worker(v):
    global colors, new_colors, changed_global, stop_flag

    while True:
        neighbor_colors = {colors[u] for u in graph[v]}

        c = 0
        while c in neighbor_colors:
            c += 1

        if c < colors[v]:
            new_colors[v] = c
        else:
            new_colors[v] = colors[v]

        barrier.wait()

        if new_colors[v] != colors[v]:
            changed_global[0] = True

        colors[v] = new_colors[v]

        barrier.wait()

        if v == 0:
            stop_flag[0] = not changed_global[0]
            changed_global[0] = False

        barrier.wait()

        if stop_flag[0]:
            break


threads = []
for v in range(N):
    t = threading.Thread(target=worker, args=(v,))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

print("Final coloring:", colors)