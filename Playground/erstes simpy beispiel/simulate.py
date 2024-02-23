import simpy
import random
import statistics

#beispiel: cinema

#reduce avg wait time to 10min or less

#arrive -> get in line -> buy ticket -> get in line for check -> ticket check -> get in line for food? -> buy food? -> go to seat

wait_times = []


class Theater(object):
    #erstellt kassierer
    def __init__(self, env, num_cashiers, num_servers, num_ushers) -> None:
        self.env = env
        self.cashier= simpy.Resource(env, num_cashiers)
        self.servers= simpy.Resource(env, num_servers)
        self.ushers= simpy.Resource(env, num_ushers)

    # methode um tickets zu kaufen, dauert ca 1-2min    
    def purchase_ticket(self, movie_customer):
        yield self.env.timeout(random.randint(1, 3))

    # ticket checken dauert ca 3s
    def check_ticket(self, movie_customer):
        yield self.env.timeout(3/60)

    # essen kaufen dauert ca 1-5min
    def sell_food(self, movie_customer):
        yield self.env.timeout(random.randint(1, 6))

    
    