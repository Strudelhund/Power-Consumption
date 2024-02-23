# funktioniert zum ersten mal

# vielleicht: architekturen vergleichen: komplexität nodes und verbindungen == prozesse & kommunikation
# --> architektur ist großer kostenfaktor

#wieviel kostet eine network connetion?
#wieviel kostet ein prozess? 0.003W ?

import simpy
import random

TOTAL_PROCESSES_STARTED = 0
TOTAL_PROCESS_TIMEOUTS = 0
TOTAL_PROCESSING_TIME = 0
TOTAL_NETWORK_COST = 0
TOTAL_MEMORY_USED = 0
TOTAL_PROCESS_COST = 0


class Microservice:
    def __init__(self, env, name):
        self.env = env
        self.name = name
        self.process_count = 0
        self.total_processing_time = 0
        self.total_network_cost = 0
        self.total_memory_used = 0
        self.process_cost = 0
        self.timeout_probability = 0.02 



    def process_request(self, request):
        global TOTAL_PROCESSING_TIME
        global TOTAL_NETWORK_COST
        global TOTAL_MEMORY_USED
        global TOTAL_PROCESS_TIMEOUTS
        global TOTAL_PROCESSES_STARTED
        global TOTAL_PROCESS_COST
    
        if random.random() < self.timeout_probability:
            print(f"{self.name} experienced a timeout for request: {request}")
            TOTAL_PROCESS_TIMEOUTS += 1
            yield self.env.timeout(10)
        else:
            process_time = random.uniform(0.5, 3)
            yield self.env.timeout(process_time)

            TOTAL_PROCESSING_TIME += process_time
            network_cost = random.uniform(0.002, 0.3)
            TOTAL_NETWORK_COST += network_cost
            memory_used = random.uniform(1, 10)
            TOTAL_MEMORY_USED += memory_used
            TOTAL_PROCESSES_STARTED += 1
            process_cost = random.uniform(0.001, 0.01)
            TOTAL_PROCESS_COST += process_cost

            self.process_count += 1
            self.process_cost += process_cost
            self.total_network_cost += network_cost
            self.total_memory_used += memory_used

            print(f"{self.name} processed request: {request} "
                  f"(Processing Time: {process_time:.2f} units, Network Cost: {network_cost:.2f} units, "
                  f"Memory Used: {memory_used:.2f} units)")

class LoadBalancer:
    def __init__(self, env, servers):
        self.env = env
        self.servers = servers

    def assign_task(self, request):
        # Round Robin Load Balancing:
        # 1. Pop the first server from the list, which represents the next server to handle the request.
        selected_server = self.servers.pop(0)
        
        # 2. Append the selected server back to the end of the list, making it the last in line for the next request.
        self.servers.append(selected_server)
        
        # 3. Return the selected server to be assigned the task.
        return selected_server


def user_service(env, load_balancer, servers):
    while True:
        request = f"User Request at {env.now}"
        print(f"User Service received request: {request}")

        selected_server = load_balancer.assign_task(request)
        selected_server_process = env.process(selected_server.process_request(request))

        yield env.timeout(random.uniform(1, 7))

        try:
            yield selected_server_process
        except simpy.Interrupt:
            print(f"User Service received interrupt for request: {request}")

env = simpy.Environment()

user_service_instance = Microservice(env, "User Service")
server1 = Microservice(env, "Server 1")
server2 = Microservice(env, "Server 2")
server3 = Microservice(env, "Server 3")

servers = [server1, server2, server3]
load_balancer = LoadBalancer(env, servers)

env.process(user_service(env, load_balancer, servers))
env.process(server1.process_request("Initial Request 1"))
env.process(server2.process_request("Initial Request 2"))
env.process(server3.process_request("Initial Request 3"))

env.run(until=30)

timeout_percentage = (TOTAL_PROCESS_TIMEOUTS / TOTAL_PROCESSES_STARTED) * 100 

# MEMORY COSTS noch dazu

print("\nOverall Statistics:\n")
print(f"User Service Processes Started: {TOTAL_PROCESSES_STARTED}")
print(f"User Service Processes Timed Out: {TOTAL_PROCESS_TIMEOUTS}")
print(f"Timeout Percentage: {timeout_percentage:.2f}%")
print("---------------------------------------------")
print(f"User Service Total Processing Time: {TOTAL_PROCESSING_TIME:.2f} ms")
print(f"User Service Total Process Cost: {TOTAL_PROCESS_COST:.2f} W")
print(f"User Service Total Network Cost: {TOTAL_NETWORK_COST:.2f} W")
print(f"User Service Total Memory Used: {TOTAL_MEMORY_USED:.2f} MB")
print("=============================================")
print("\nServer Statistics:\n")
for server in servers:
    print(f"{server.name} Processes Started: {server.process_count}")
    print(f"{server.name} Total Processing Time: {server.total_processing_time:.2f} ms")
    print(f"{server.name} Total Process Cost: {server.process_cost:.2f} W")
    print(f"{server.name} Total Network Cost: {server.total_network_cost:.2f} W")
    print(f"{server.name} Total Memory Used: {server.total_memory_used:.2f} MB")
    print("---------------------------------------------")