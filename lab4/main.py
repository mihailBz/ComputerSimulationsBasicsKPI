import simpy
from random import random

# Вхідні параметри
SIMULATION_TIME = 20
TOKEN_NUMBER = 20
Q1_CAPACITY = 20
Q2_CAPACITY = 10
T1_TIMEOUT = 0.8
T2_TIMEOUT = 0.3
P22_PROBABILITY = 0.2


class PetriNet:
    """Клас мережі з описом позицій і переходів"""

    def __init__(self, env, q1, q2, t1, t2):
        self.env = env
        self.queue1 = simpy.Resource(env, q1)
        self.queue2 = simpy.Resource(env, q2)

        self.t1_timeout = t1
        self.t2_timeout = t2

        self.transition11_ = simpy.Resource(env)
        self.transitions2 = [
            simpy.Resource(env),
            simpy.Resource(env),
            simpy.Resource(env),
        ]

    # методи, що імплементують логіку переходів
    def transition11(self, token_id):
        """Перехід T1"""
        with self.transition11_.request() as req:
            yield req
            print(f"transition11: token {token_id} entered at {self.env.now:.2f}")
            yield self.env.timeout(self.t1_timeout)
            print(f"transition11: token {token_id} left at {self.env.now:.2f}")

    def transition2(self, token_id):
        """Вибір одного з паралельних переходів T21 T22 T23"""
        is_handled = False
        for i, transition in enumerate(self.transitions2):
            if transition.count == 0:
                with transition.request() as req:
                    yield req
                    print(
                        f"transiotion2{i+1}: token {token_id} entered at {self.env.now:.2f}"
                    )
                    yield self.env.timeout(self.t2_timeout)
                    print(
                        f"transiotion2{i+1}: token {token_id} left at {self.env.now:.2f}"
                    )
                    is_handled = True
                    break
        if not is_handled:
            with self.transitions2[0].request() as req:
                yield req
                print(f"transiotion21: token {token_id} entered at {self.env.now:.2f}")
                yield self.env.timeout(self.t2_timeout)
                print(f"transiotion21: token {token_id} left at {self.env.now:.2f}")


def token(env, id, net):
    """Функція, що імплементує логіку маркера"""
    full_path = True
    while True:
        if full_path:
            # черга 1(позиція P1)
            with net.queue1.request() as request:
                print(f"place 1: token {id} entered at {env.now:.2f}")
                yield request
                yield env.process(net.transition11(id))
        # черга 2(позиція P2)
        with net.queue2.request() as request:
            print(f"place 2: token {id} entered at {env.now:.2f}")
            yield request

            yield env.process(net.transition2(id))

            # позиція P3 і ймовірнісні переходи T31 і T32
            if random() < P22_PROBABILITY:
                full_path = False
                print(f"Path choice: token {id} got short path at {env.now:.2f}")
            else:
                full_path = True
                print(f"Path choice: token {id} got long path at {env.now:.2f}")


def main():
    # Запуск моделювання
    env = simpy.Environment()
    net = PetriNet(
        env,
        Q1_CAPACITY,
        Q2_CAPACITY,
        T1_TIMEOUT,
        T2_TIMEOUT,
    )
    # Генерація 20 маркерів
    for i in range(1, TOKEN_NUMBER + 1):
        env.process(token(env, i, net))

    env.run(until=SIMULATION_TIME)


if __name__ == "__main__":
    main()
