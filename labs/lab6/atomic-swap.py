import hashlib
import time
import logging

logging.basicConfig(level=logging.INFO, format="%(message)s")

class HTLC:
    def __init__(self, sender, receiver, hash_secret, timeout):
        self.sender = sender
        self.receiver = receiver
        self.hash_secret = hash_secret
        self.timeout = timeout
        self.locked = True
        self.redeemed = False
        self.refunded = False

    def redeem(self, secret, current_time):
        if not self.locked:
            logging.info(f"{self.receiver} cannot redeem, funds not locked.")
            return False
        if self.redeemed or self.refunded:
            logging.info(f"{self.receiver} cannot redeem, already processed.")
            return False
        if hashlib.sha256(secret.encode()).hexdigest() == self.hash_secret and current_time < self.timeout:
            self.redeemed = True
            self.locked = False
            logging.info(f"{self.receiver} redeemed funds from {self.sender}.")
            return True
        else:
            logging.info(f"{self.receiver} failed to redeem funds.")
            return False

    def refund(self, current_time):
        if self.locked and current_time >= self.timeout:
            self.refunded = True
            self.locked = False
            logging.info(f"{self.sender} refunded funds.")
            return True
        return False


# --- Симуляція тристороннього Atomic Swap ---
def atomic_swap():
    # Учасники
    A, B, C = "A", "B", "C"

    # Генерація секрету
    secret = "super_secret_value"
    hash_secret = hashlib.sha256(secret.encode()).hexdigest()
    logging.info(f"{A} generated secret and hash.")

    # Тайм-аути
    T1, T2, T3 = 10, 7, 5  # умовні одиниці часу

    # Створення HTLC
    htlc_AB = HTLC(A, B, hash_secret, T1)
    logging.info("A locked funds for B.")

    htlc_BC = HTLC(B, C, hash_secret, T2)
    logging.info("B locked funds for C.")

    htlc_CA = HTLC(C, A, hash_secret, T3)
    logging.info("C locked funds for A.")

    # --- Успішний сценарій ---
    current_time = 0
    logging.info("=== Successful scenario ===")

    # A розкриває секрет
    htlc_CA.redeem(secret, current_time)
    logging.info("A revealed secret.")

    # C бачить секрет і використовує його
    htlc_BC.redeem(secret, current_time)

    # B бачить секрет і використовує його
    htlc_AB.redeem(secret, current_time)

    # --- Неуспішний сценарій (тайм-аут) ---
    logging.info("\n=== Failed scenario (timeout) ===")
    current_time = 12  # час перевищує всі тайм-аути

    htlc_AB.refund(current_time)
    htlc_BC.refund(current_time)
    htlc_CA.refund(current_time)


if __name__ == "__main__":
    atomic_swap()
