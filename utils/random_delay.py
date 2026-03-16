import random
import time

def random_delay(min_sec=2, max_sec=5):
    delay = random.uniform(min_sec, max_sec)
    time.sleep(delay)

def random_delay_short():
    random_delay(0.5, 1.5)

def random_delay_medium():
    random_delay(2, 4)

def random_delay_long():
    random_delay(5, 10)

def random_delay_between_actions():
    delay = random.uniform(1, 3)
    time.sleep(delay)
