# callcenter

import random
import simpy
import numpy

NUM_EMPLOYEES = 2
AVG_SUPPORT_TIME = 5 #min
CUSTOMER_INTERVAL = 2 #min
SIM_TIME = 120 #min


customers_handled = 0


class CallCenter:
    def __init__(self, env, num_employees, support_time) -> None:
        self.env = env
        self.num_employees = simpy.Resource(env, num_employees)
        self.support_time = support_time

    def support(self, customer):
        # normalverteilung min 1, daher max(x,y) & nv: 5, div: 4 links und rechts
        random_time = max(1, numpy.random.noprmal(self.support_time, 4))

        yield self.env.timeout(random_time)
        print(f"Support finished for {customer} at {self.env.now: .2f}")

def customer(env, name, call_center):
    global customers_handled
    print(f"Customer {name} enters waiting queue at {env.now:.2f}")