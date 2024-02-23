# round robin implementiert
# splittet in network calls = 1W und processing internally = 2W

#kosten hängen von calls auf stack ab --> link

#wieviel kostet ein network call
#wieviel kostet ein prozess der app
#wieviel kostet lesen/schreibena auf speicher
# wieviele prozesse/calls/read&writes pro app?

import simpy
import random

TOTAL_PROCESSES_STARTED = 0
TOTAL_PROCESS_TIMEOUTS = 0
TOTAL_PROCESSING_TIME = 0
TOTAL_NETWORK_COST = 0
TOTAL_MEMORY_USED = 0
TOTAL_LOADBALANCER_TIME_CONSUMPTION = 0

NUM_SERVERS = 10

class Microservice:
    def __init__(self, env, name):
        self.env = env
        self.name = name
        self.process_count = 0
        self.total_processing_time = 0
        self.total_network_cost = 0
        self.total_memory_used = 0
        self.timeout_probability = 0.002 #0.2% prob

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
        self.total_time_consumption = 0

    def assign_task(self, request):
        start_time = self.env.now

        # Round Robin Load Balancing:
        # 1. Pop the first server from the list, which represents the next server to handle the request.
        selected_server = self.servers.pop(0)

        # 2. Append the selected server back to the end of the list, making it the last in line for the next request.
        self.servers.append(selected_server)

        # 3. Return the selected server to be assigned the task.
        network_cost = random.uniform(0.002, 0.3)
        self.total_network_cost += network_cost  # Track the network cost of load balancing

        end_time = self.env.now
        self.total_time_consumption += end_time - start_time

        return selected_server

def user_service(env, load_balancer, servers, user_service_instance):
    while True:
        request = f"User Request at {env.now}"
        print(f"User Service received request: {request}")

        load_balancer_start_time = env.now  # Record LoadBalancer start time
        selected_server = load_balancer.assign_task(request)
        selected_server_process = env.process(selected_server.process_request(request))

        yield env.timeout(random.uniform(1, 7))

        try:
            yield selected_server_process
        except simpy.Interrupt:
            print(f"User Service received interrupt for request: {request}")

        # Record LoadBalancer time consumption after the selected server has processed the request
        load_balancer_end_time = env.now
        load_balancer.total_time_consumption += load_balancer_end_time - load_balancer_start_time

# Create and run the simulation environment
env = simpy.Environment()

user_service_instance = Microservice(env, "User Service")
servers = [Microservice(env, f"Server {i+1}") for i in range(NUM_SERVERS)]
load_balancer = LoadBalancer(env, servers)

# Create and run the user_service process
user_service_process = env.process(user_service(env, load_balancer, servers, user_service_instance))

# Run the simulation
env.run(until=30000)

# Calculate timeout percentage
timeout_percentage = (TOTAL_PROCESS_TIMEOUTS / TOTAL_PROCESSES_STARTED) * 100

# Print overall statistics
print("\nOverall Statistics:\n")
print("=============================================")
print(f"User Service Processes Started: {TOTAL_PROCESSES_STARTED}")
print(f"User Service Processes Timed Out: {TOTAL_PROCESS_TIMEOUTS}")
print(f"Timeout Percentage: {timeout_percentage:.2f}%")
print("---------------------------------------------")
print(f"User Service Total Processing Time: {TOTAL_PROCESSING_TIME:.2f} ms")
print(f"User Service Total Network Cost: {TOTAL_NETWORK_COST:.2f} W")
print(f"User Service Total Memory Used: {TOTAL_MEMORY_USED:.2f} KB")
print("---------------------------------------------")
print(f"LoadBalancer Total Time Consumption: {load_balancer.total_time_consumption:.2f} ms")
print(f"LoadBalancer Total Network Cost: {load_balancer.total_network_cost:.2f} W")
print("=============================================")
print("\nServer Statistics:\n")

print("=============================================")

# Sort the servers based on their names
servers.sort(key=lambda server: server.name)

for server in servers:
    print(f"{server.name} Processes Started: {server.process_count}")
    print(f"{server.name} Total Processing Time: {server.total_processing_time:.2f} ms")
    print(f"{server.name} Total Process Cost: {server.total_network_cost:.2f} W")
    print(f"{server.name} Total Network Cost: {server.total_memory_used:.2f} W")
    print(f"{server.name} Total Memory Used: {server.total_memory_used:.2f} KB")
    print("=============================================")
