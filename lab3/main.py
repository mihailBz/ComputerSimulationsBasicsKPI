import simpy
import pandas as pd

SIMULATION_TIME = 30

INTENSITY = 0.22

Q1_CAPACITY = 9
Q2_CAPACITY = 3

MU_1 = 0.23
T_1 = 1 / MU_1
T_2 = 5
T_3 = 10

event_handled_number = 0
event_unhandled_number = 0
measurements = []


class MMO:
    """Клас мережі масового обслуговування"""
    def __init__(self, env, q1, q2, t_1, t_2, t_3):
        """Конструктор приймає параметри мережі"""
        self.env = env
        self.queue1 = simpy.Resource(env, q1)
        self.t_1 = t_1
        self.k1_queue = simpy.Resource(env)

        self.t_2 = t_2
        self.k2_queue = simpy.Resource(env)

        self.queue2 = simpy.Resource(env, q2)
        self.t_3 = t_3
        self.k3_queue = simpy.Resource(env)

    # кожен з методів нижче відповідає каналу обробки ММО
    def k1(self, event_id):
        with self.k1_queue.request() as req:
            yield req
            print(f"k1: Event {event_id} entered at {self.env.now:.2f}")
            yield self.env.timeout(self.t_1)
            print(f"k1: Event {event_id} handled at {self.env.now:.2f}")

    def k2(self, event_id):
        print(f"k2: Event {event_id} entered at {self.env.now:.2f}")
        yield self.env.timeout(self.t_2)
        print(f"k2: Event {event_id} handled at {self.env.now:.2f}")

    def k3(self, event_id):
        with self.k3_queue.request() as req:
            yield req
            print(f"k3: Event {event_id} entered at {self.env.now:.2f}")
            yield self.env.timeout(self.t_3)
            print(f"k3: Event {event_id} handled at {self.env.now:.2f}")


def event(env, id, mmo):
    """Функція, що визначає маршрут слідування вимоги. Відбуваються перевірки, чи є місце в черзі, чи не відбувається блокування"""
    global event_handled_number, event_unhandled_number, measurements
    event_stat = {"id": id}

    if mmo.queue1.count == mmo.queue1.capacity:
        print(f"UNHANDLED: Event {id} left mmo unhandled. Queue 1 is full.")
        event_unhandled_number += 1
        return

    with mmo.queue1.request() as request:
        print(f"queue 1: Event {id} entered at {env.now:.2f}")
        q1_enter_time = env.now
        event_stat["q1_length"] = mmo.queue1.count
        yield request
        yield env.process(mmo.k1(id))
        # print(f'queue 1: Event {id} left at {(env.now - mmo.t_1):.2f}')
        event_stat["q1_waiting_time"] = env.now - mmo.t_1 - q1_enter_time

    print(f"Event {id} is requesting k2 at {env.now:.2f}")
    if mmo.k2_queue.count == 0:
        print(f"Event {id} is passed to k2 at {env.now:.2f}")
        with mmo.k2_queue.request() as request:
            yield request
            yield env.process(mmo.k2(id))
    else:
        print(f"Event {id} is blocked by k2 at {env.now:.2f}")
        print(f"Event {id} is passed to queue 2 at {env.now:.2f}")
        if mmo.queue2.count == mmo.queue2.capacity:
            print(f"UNHANDLED: Event {id} left mmo unhandled. Queue 2 is full.")
            event_unhandled_number += 1
            return
        with mmo.queue2.request() as request:
            print(f"queue 2: Event {id} entered at {env.now:.2f}")
            q2_enter_time = env.now
            event_stat["q2_length"] = mmo.queue2.count
            yield request
            print(f"queue 2: Event {id} left at {env.now:.2f}")
            yield env.process(mmo.k3(id))
            event_stat["q2_waiting_time"] = env.now - mmo.t_3 - q2_enter_time

    measurements.append(event_stat)
    event_handled_number += 1
    print(f"MMO Exit: Event {id} left MMO {env.now:.2f}")


def setup(env, intensity, t1, t2, t3):
    """Ініціалізація мережі МО та генереція вимог з заданим інтервалом"""
    mmo = MMO(env, Q1_CAPACITY, Q2_CAPACITY, t1, t2, t3)

    i = 0
    while True:
        yield env.timeout(1/intensity)
        i += 1
        print(f"MMO Enter: Event {i} entered MMO at {env.now:.2f}")
        env.process(event(env, i, mmo))


def main():
    env = simpy.Environment()
    print(f"Simulation started at {env.now:.2f}")
    env.process(setup(env, INTENSITY, T_1, T_2, T_3))
    env.run(until=SIMULATION_TIME)
    print(f"Simulation finished at {env.now:.2f}")
    print("\n\n\n")
    print(f"Total events handled: {event_handled_number}")
    print(f"Total events not handled: {event_unhandled_number}")
    print("Unhandled events percentage:")
    print(
        round(
            event_unhandled_number / (event_handled_number + event_unhandled_number), 3
        )
    )
    print("\n")
    stat_df = pd.DataFrame(measurements)

    # print(stat_df)
    print("Queue 1 average stats")
    print(stat_df[["q1_length", "q1_waiting_time"]].mean().round(3))
    print("\nQueue 2 average stats")
    print(stat_df[["q2_length", "q2_waiting_time"]].dropna().mean().round(3))


if __name__ == "__main__":
    main()
