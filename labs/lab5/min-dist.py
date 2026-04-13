import threading
import math

graph = {
    0: [(1, 4), (2, 1)],
    1: [(0, 4), (2, 2), (3, 5)],
    2: [(0, 1), (1, 2), (3, 1)],
    3: [(1, 5), (2, 1), (4, 3)],
    4: [(3, 3)]
}

N = len(graph)
source = 0

dist = [math.inf] * N
dist[source] = 0

new_dist = dist.copy()

barrier = threading.Barrier(N)

def worker(v):
    global dist, new_dist

    for _ in range(N):
        # локальне обчислення
        best = dist[v]

        for u, w in graph[v]:
            best = min(best, dist[u] + w)

        new_dist[v] = best

        barrier.wait()

        dist[v] = new_dist[v]

        barrier.wait()


threads = []
for v in range(N):
    t = threading.Thread(target=worker, args=(v,))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

print("Shortest distances:", dist)