import threading
import time
import random

N = 5

forks = [threading.Semaphore(1) for _ in range(N)]
mutex = threading.Lock()


def philosopher(i):
    left = i
    right = (i + 1) % N

    while True:
        print(f"Philosopher {i} thinking")
        time.sleep(random.uniform(0.5, 1.5))

        mutex.acquire()
        forks[left].acquire()
        forks[right].acquire()
        mutex.release()

        print(f"Philosopher {i} eating")
        time.sleep(random.uniform(0.5, 1.5))

        forks[left].release()
        forks[right].release()


threads = []
for i in range(N):
    t = threading.Thread(target=philosopher, args=(i,))
    t.daemon = True
    t.start()
    threads.append(t)

time.sleep(15)