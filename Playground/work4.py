# geht aber user service is auf 0

import simpy
import random

TOTAL_PROCESSES_STARTED = 0
TOTAL_PROCESS_TIMEOUTS = 0
TOTAL_PROCESSING_TIME = 0
TOTAL_NETWORK_COST = 0
TOTAL_MEMORY_USED = 0

class Microservice:
    def __init__(self, env, name):
        self.env = env
        self.name = name
        self.process_count = 0
        self.total_processing_time = 0
        self.total_network_cost = 0
        self.total_memory_used = 0
        self.timeout_probability = 0.00002

    def process_request(self, request):
        global TOTAL_PROCESSING_TIME
        global TOTAL_NETWORK_COST
        global TOTAL_MEMORY_USED
        global TOTAL_PROCESS_TIMEOUTS
        global TOTAL_PROCESSES_STARTED

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

            self.process_count += 1
            self.total_network_cost += network_cost
            self.total_memory_used += memory_used
            self.total_processing_time += process_time

            print(f"{self.name} processed request: {request} "
                  f"(Processing Time: {process_time:.2f} ms, Network Cost: {network_cost:.2f} W, "
                  f"Memory Used: {memory_used:.2f} KB)")

class LoadBalancer:
    def __init__(self, env, servers):
        self.env = env
        self.servers = servers
        self.total_network_cost = 0

    def assign_task(self, request):
        # Round Robin Load Balancing:
        # 1. Pop the first server from the list, which represents the next server to handle the request.
        selected_server = self.servers.pop(0)

        # 2. Append the selected server back to the end of the list, making it the last in line for the next request.
        self.servers.append(selected_server)

        # 3. Return the selected server to be assigned the task.
        network_cost = random.uniform(0.002, 0.3)
        self.total_network_cost += network_cost  # Track the network cost of load balancing
        return selected_server

def user_service(env, load_balancer, servers, user_service_instance):
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

class Server:
    def __init__(self, env, name, latency, timeout, read_time, write_time):
        self.env = env
        self.name = name
        self.latency = latency
        self.timeout = timeout
        self.read_time = read_time
        self.write_time = write_time
        self.total_processing_time = 0
        self.total_network_cost = 0
        self.total_memory_used = 0
        self.process_count = 0
        self.process_cost = 0

    def process_request(self, request):
        global TOTAL_PROCESSING_TIME
        global TOTAL_NETWORK_COST
        global TOTAL_MEMORY_USED
        global TOTAL_PROCESS_TIMEOUTS
        global TOTAL_PROCESSES_STARTED

        start_time = self.env.now

        # Simulate network latency
        yield self.env.timeout(self.latency)

        if random.random() < self.timeout:
            print(f"{self.name} experienced a timeout for request: {request}")
            TOTAL_PROCESS_TIMEOUTS += 1
            yield self.env.timeout(10)
        else:
            # Simulate read time
            yield self.env.timeout(self.read_time)

            process_time = random.uniform(0.5, 3)
            yield self.env.timeout(process_time)

            TOTAL_PROCESSING_TIME += process_time
            network_cost = random.uniform(0.002, 0.3)
            TOTAL_NETWORK_COST += network_cost
            memory_used = random.uniform(1, 10)
            TOTAL_MEMORY_USED += memory_used
            TOTAL_PROCESSES_STARTED += 1
            process_cost = random.uniform(0.001, 0.01)
            self.process_cost += process_cost

            self.process_count += 1
            self.total_network_cost += network_cost
            self.total_memory_used += memory_used
            self.total_processing_time += process_time

            # Simulate write time
            yield self.env.timeout(self.write_time)

            print(f"{self.name} processed request: {request} "
                  f"(Processing Time: {process_time:.2f} ms, Network Cost: {network_cost:.2f} W, "
                  f"Memory Used: {memory_used:.2f} KB)")

        end_time = self.env.now

        print(f"{self.name} completed request: {request} "
              f"(Total Time: {end_time - start_time:.2f} ms)")

env = simpy.Environment()

user_service_instance = Microservice(env, "User Service")
server1 = Server(env, "Server 1", latency=0.1, timeout=0.001, read_time=0.02, write_time=0.01)
server2 = Server(env, "Server 2", latency=0.2, timeout=0.005, read_time=0.01, write_time=0.02)
server3 = Server(env, "Server 3", latency=0.15, timeout=0.02, read_time=0.015, write_time=0.015)

servers = [server1, server2, server3]
load_balancer = LoadBalancer(env, servers)

# Create and run the user_service process
user_service_process = env.process(user_service(env, load_balancer, servers, user_service_instance))

# Create and run server processes
for server in servers:
    env.process(server.process_request(f"Initial Request for {server.name}"))

env.run(until=3000)

timeout_percentage = (TOTAL_PROCESS_TIMEOUTS / TOTAL_PROCESSES_STARTED) * 100

print("\nOverall Statistics:\n")
print(f"User Service Processes Started: {TOTAL_PROCESSES_STARTED}")
print(f"User Service Processes Timed Out: {TOTAL_PROCESS_TIMEOUTS}")
print(f"Timeout Percentage: {timeout_percentage:.2f}%")
print("---------------------------------------------")
print(f"User Service Total Processing Time: {TOTAL_PROCESSING_TIME:.2f} ms")
print(f"User Service Total Network Cost: {TOTAL_NETWORK_COST:.2f} W")
print(f"User Service Total Memory Used: {TOTAL_MEMORY_USED:.2f} KB")
print("---------------------------------------------")
print(f"LoadBalancer Total Network Cost: {load_balancer.total_network_cost:.2f} W")
print("=============================================")
print("\nServer Statistics:\n")

# Sort the servers based on their names
servers.sort(key=lambda server: server.name)

for server in servers:
    print(f"{server.name} Processes Started: {server.process_count}")
    print(f"{server.name} Total Processing Time: {server.total_processing_time:.2f} ms")
    print(f"{server.name} Total Process Cost: {server.process_cost:.2f} W")
    print(f"{server.name} Total Network Cost: {server.total_network_cost:.2f} W")
    print(f"{server.name} Total Memory Used: {server.total_memory_used:.2f} KB")
    print("---------------------------------------------")
