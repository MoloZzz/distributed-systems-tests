import threading
import time
import random

N = 5

forks = [threading.Lock() for _ in range(N)]
room = threading.Semaphore(N - 1)


def philosopher(i):
    left = i
    right = (i + 1) % N

    while True:
        print(f"Philosopher {i} thinking")
        time.sleep(random.uniform(0.5, 1.5))

        room.acquire()

        forks[left].acquire()
        forks[right].acquire()

        print(f"Philosopher {i} eating")
        time.sleep(random.uniform(0.5, 1.5))

        forks[right].release()
        forks[left].release()

        room.release()


threads = []
for i in range(N):
    t = threading.Thread(target=philosopher, args=(i,))
    t.daemon = True
    t.start()
    threads.append(t)

time.sleep(15)