"""
HS-алгоритм пошуку лідера у кільці (Hirschberg & Sinclair, 1980)

Вхідні дані : кількість процесів (N)
Вихідні дані: UID переможця, кількість раундів, сумарна кількість повідомлень

Алгоритм (покроково):
  Раунд r = 1, 2, 3, ...
  TTL у раунді r = 2^(r-1).

  Кожен АКТИВНИЙ процес P надсилає probe(uid_P) у обидва напрямки (CW та CCW).

  Обробка probe(u) процесом Q:
    - u > uid(Q): якщо hops < TTL → пересилаємо далі; якщо hops == TTL → reply назад
    - u < uid(Q): зонд відкидається (процес u "програв")
    - u == uid(Q): зонд повернувся до відправника → Q виграв раунд

  Обробка reply(u) процесом Q:
    - u == uid(Q): reply дійшов до відправника, знімаємо один «очікуваний» reply
    - інакше: пересилаємо reply далі у тому ж напрямку

  Коли процес отримав reply з обох напрямків → готовий до наступного раунду.
  Коли залишається 1 активний процес → він є лідером.
"""

from __future__ import annotations
import random
from collections import deque
from typing import Optional

CW  = "cw"
CCW = "ccw"


def opposite(d: str) -> str:
    return CCW if d == CW else CW


class Message:
    __slots__ = ("uid", "direction", "hops", "ttl", "is_reply")

    def __init__(self, uid: int, direction: str, hops: int, ttl: int, is_reply: bool = False):
        self.uid       = uid
        self.direction = direction
        self.hops      = hops
        self.ttl       = ttl
        self.is_reply  = is_reply

    def __repr__(self) -> str:
        kind = "reply" if self.is_reply else "probe"
        return f"<{kind} uid={self.uid} dir={self.direction} hops={self.hops}/{self.ttl}>"


class HSSimulator:
    def __init__(self, n: int, uids: Optional[list] = None):
        if n < 2:
            raise ValueError("Потрібно щонайменше 2 процеси")
        if uids is None:
            uids = random.sample(range(1, 10 * n + 1), n)
        else:
            if len(uids) != n or len(set(uids)) != n:
                raise ValueError("UIDs мають бути унікальними та кількість має відповідати N")
        self.n    = n
        self.uids = list(uids)
        self.active = [True] * n
        self.total_messages = 0
        self.current_round  = 0
        self.winner_uid     = None
        self.winner_pid     = None
        self.log            = []

    def _next(self, pid: int, direction: str) -> int:
        return (pid + 1) % self.n if direction == CW else (pid - 1) % self.n

    def _active_pids(self):
        return [i for i in range(self.n) if self.active[i]]

    def _log(self, text: str):
        self.log.append(text)

    def run(self, verbose: bool = True) -> dict:
        self._log(f"HS-алгоритм: N={self.n}")
        self._log(f"UIDs: {self.uids}")

        for round_num in range(1, self.n + 2):
            self.current_round = round_num
            ttl = 2 ** (round_num - 1)
            active = self._active_pids()

            self._log(f"\n{'='*44}\nРаунд {round_num}  (TTL={ttl})")
            self._log(f"Активні: {[(i, self.uids[i]) for i in active]}")

            if len(active) == 1:
                self.winner_pid = active[0]
                self.winner_uid = self.uids[active[0]]
                break

            # Ініціалізуємо inbox
            inbox = [deque() for _ in range(self.n)]

            # Очікування reply для кожного активного процесу
            # [cw_done, ccw_done]
            reply_received = {pid: [False, False] for pid in active}

            # Надсилаємо probe з обох напрямків
            for pid in active:
                for d in (CW, CCW):
                    dest = self._next(pid, d)
                    inbox[dest].append(Message(uid=self.uids[pid], direction=d, hops=1, ttl=ttl))
                    self.total_messages += 1

            # Виконуємо такти
            max_ticks = self.n * (ttl * 2 + 4)
            for _ in range(max_ticks):
                if all(len(q) == 0 for q in inbox):
                    break

                next_inbox = [deque() for _ in range(self.n)]
                newly_dead = []

                for pid in range(self.n):
                    for msg in inbox[pid]:
                        self._process_msg(pid, msg, next_inbox, newly_dead,
                                          reply_received)

                for pid in newly_dead:
                    if self.active[pid]:
                        self.active[pid] = False
                        if pid in reply_received:
                            del reply_received[pid]
                        self._log(f"  P{pid}(uid={self.uids[pid]}) виключено")

                inbox = next_inbox

                # Перевірка: залишився один?
                alive = self._active_pids()
                if len(alive) == 1:
                    self.winner_pid = alive[0]
                    self.winner_uid = self.uids[alive[0]]
                    break

            if self.winner_uid is not None:
                break

            # Перевірка після раунду
            alive = self._active_pids()
            if len(alive) == 1:
                self.winner_pid = alive[0]
                self.winner_uid = self.uids[alive[0]]
                break

        result = {
            "winner_uid":     self.winner_uid,
            "rounds":         self.current_round,
            "total_messages": self.total_messages,
        }

        if verbose:
            self._print_result(result)

        return result

    def _process_msg(self, pid: int, msg: Message, next_inbox, newly_dead, reply_received):
        if msg.is_reply:
            u = msg.uid
            my_uid = self.uids[pid]
            if u == my_uid:
                self._log(f"  P{pid}(uid={my_uid}): reply [{msg.direction}] отримано")
                if pid in reply_received:
                    if msg.direction == CCW:
                        reply_received[pid][0] = True  # CW probe закрито
                    else:
                        reply_received[pid][1] = True  # CCW probe закрито
            else:
                dest = self._next(pid, msg.direction)
                next_inbox[dest].append(msg)
                self.total_messages += 1
            return

        # Probe
        if not self.active[pid]:
            # Неактивний просто пересилає
            dest = self._next(pid, msg.direction)
            next_inbox[dest].append(msg)
            self.total_messages += 1
            return

        u, my_uid = msg.uid, self.uids[pid]

        if u == my_uid:
            # Probe повернувся → виграв раунд (закриваємо цей напрямок)
            self._log(f"  P{pid}(uid={my_uid}): probe повернувся [{msg.direction}]")
            if pid in reply_received:
                if msg.direction == CW:
                    reply_received[pid][0] = True
                else:
                    reply_received[pid][1] = True

        elif u > my_uid:
            if msg.hops < msg.ttl:
                dest = self._next(pid, msg.direction)
                next_inbox[dest].append(
                    Message(uid=u, direction=msg.direction, hops=msg.hops + 1, ttl=msg.ttl))
                self.total_messages += 1
            else:
                # Досягнуто TTL → reply назад
                back = opposite(msg.direction)
                dest = self._next(pid, back)
                next_inbox[dest].append(
                    Message(uid=u, direction=back, hops=1, ttl=msg.ttl, is_reply=True))
                self.total_messages += 1
        else:
            # u < my_uid: знаходимо та виключаємо процес з uid=u
            victim = next((i for i in range(self.n)
                           if self.uids[i] == u and self.active[i]), None)
            if victim is not None and victim not in newly_dead:
                newly_dead.append(victim)

    def _print_result(self, result: dict):
        print("\n" + "="*50)
        print("      РЕЗУЛЬТАТИ HS-АЛГОРИТМУ")
        print("="*50)
        print(f"  UID переможця     : {result['winner_uid']}")
        print(f"  Кількість раундів : {result['rounds']}")
        print(f"  Всього повідомлень: {result['total_messages']}")
        print("="*50)
        print("\n--- Деталі раундів ---")
        for line in self.log:
            print(line)


def main():
    try:
        n = int(input("Введіть кількість процесів: "))
        if n < 2:
            print("Потрібно щонайменше 2 процеси.")
            return
    except ValueError:
        print("Помилка: введіть ціле число.")
        return
    sim = HSSimulator(n=n)
    sim.run(verbose=True)


if __name__ == "__main__":
    main()