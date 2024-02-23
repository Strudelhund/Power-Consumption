#DO NOT USE -- BROKENs

import simpy
import random

TOTAL_PROCESSES_INITIALIZED = 0
TOTAL_PROCESSES_STARTED = 0
TOTAL_PROCESS_TIMEOUTS = 0

TOTAL_SERVER_PROCESSES_STARTED = 0
TOTAL_SERVER_PROCESSES_FAILED = 0

TOTAL_PROCESSING_TIME = 0
TOTAL_NETWORK_COST = 0
TOTAL_MEMORY_USED = 0

TOTAL_LOADBALANCER_TIME_CONSUMPTION = 0

NUM_SERVERS = 3

class Microservice:
    def __init__(self, env, name, timeout):
        self.env = env
        self.name = name
        self.process_count = 0
        self.service_processing_time = 0
        self.service_network_cost = 0
        self.service_memory_used = 0
        self.timeout_probability = timeout
        self.service_timeouts = 0
        self.service_started = 0

    def process_request(self, request):
        global TOTAL_PROCESSING_TIME
        global TOTAL_NETWORK_COST
        global TOTAL_MEMORY_USED
        global TOTAL_PROCESS_TIMEOUTS
        global TOTAL_PROCESSES_STARTED
        global TOTAL_PROCESSES_INITIALIZED

        # initialize a service
        TOTAL_PROCESSES_INITIALIZED += 1
        print("process request initialized")
        #print(f"Initialized Service Requests: {TOTAL_PROCESSES_INITIALIZED}")

        # simulate runtime service error/timeouts/etc
        if random.random() < self.timeout_probability:
            # initialize a service
            print(f"{self.name} experienced a runtime error for request: {request}")
            self.service_timeouts += 1
            error_handling_time = random.uniform(0.5, 3)
            yield self.env.timeout(error_handling_time)
        else:
            # start a service on a server
            self.service_started += 1
            print("process request started")
            # simulate service process time
            process_time = random.uniform(1, 9)
            yield self.env.timeout(process_time)

            # simulate service network cost
            network_cost = random.uniform(0.002, 0.3)

            # simulate service memory usage
            memory_used = random.uniform(1, 10)

            self.process_count += 1
            self.service_network_cost += network_cost
            self.service_memory_used += memory_used
            self.service_processing_time += process_time

            #print(f"{self.name} processed request: {request} "
            #      f"(Processing Time: {process_time:.2f} ms, Network Cost: {network_cost:.2f} W, "
            #      f"Memory Used: {memory_used:.2f} KB)")
            print("process request finished")

class LoadBalancer:
    def __init__(self, env, servers):
        self.env = env
        self.servers = servers
        self.lb_network_cost = 0
        self.assign_time_consumption = 0

    def assign_task(self, request):

        print("assign task initialized")
        # time the load balancer assigns task to server
        start_time = self.env.now

        # Round Robin Load Balancing:
        # Pop the first server from the list, which represents the next server to handle the request.
        selected_server = self.servers.pop(0)

        # Assign the task to the selected server
        server_process = self.env.process(selected_server.process_request(request))
        yield server_process

        # Append the selected server back to the end of the list, making it the last in line for the next request.
        self.servers.append(selected_server)

        # Track the network cost of load balancing
        network_cost = random.uniform(0.002, 0.3)
        self.lb_network_cost += network_cost

        # Record LoadBalancer time consumption after a server has processed the request
        end_time = self.env.now
        self.assign_time_consumption += end_time - start_time

        print("assign task finished")

def user_service(env, load_balancer, user_service_instance):
    while True:
        print("user service started")
        request = f"User Request at {env.now}"
        print(f"User Service received request: {request}")

        # Assign a server for the user request
        selected_server = yield env.process(load_balancer.assign_task(request))

        # Start the user service on the selected server
        selected_server_process = env.process(selected_server.process_request(request))

        # Wait for the user service process to complete or be interrupted
        try:
            yield selected_server_process
        except simpy.Interrupt:
            print(f"User Service received interrupt for request: {request}")

        # Introduce some delay before the next user request
        print("user service started")
        yield env.timeout(random.uniform(1, 7))


class Server:
    def __init__(self, env, name, latency, timeout, read_time, write_time):
        self.env = env
        self.name = name
        self.server_latency = latency
        self.server_timeout_probability = timeout
        self.server_read_time = read_time
        self.server_write_time = write_time
        self.server_processing_time = 0
        self.server_network_cost = 0
        self.server_memory_used = 0
        self.server_processes_started = 0
        self.server_processes_error = 0
        self.process_cost = 0

    def process_request(self, request):
        global TOTAL_PROCESSING_TIME
        global TOTAL_NETWORK_COST
        global TOTAL_MEMORY_USED
        global TOTAL_PROCESS_TIMEOUTS
        global TOTAL_PROCESSES_STARTED

        start_time = self.env.now

        # Simulate server latency
        yield self.env.timeout(self.server_latency)

        # Simulate read time
        yield self.env.timeout(self.server_read_time)

        if random.random() < self.server_timeout_probability:
            print(f"{self.name} experienced a timeout for request: {request}")
            self.server_processes_error += 1
            yield self.env.timeout(10)
        else:
            # simulate server processing time
            process_time = random.uniform(0.5, 3)
            yield self.env.timeout(process_time)

            network_cost = random.uniform(0.002, 0.3)
            self.server_network_cost += network_cost
            memory_used = random.uniform(1, 10)
            self.server_memory_used += memory_used
            self.server_processes_started += 1
            process_cost = random.uniform(0.001, 0.01)
            self.process_cost += process_cost

            # Simulate write time
            yield self.env.timeout(self.server_write_time)

            print(f"{self.name} processed request: {request} "
                  f"(Processing Time: {process_time:.2f} ms, Network Cost: {network_cost:.2f} W, "
                  f"Memory Used: {memory_used:.2f} KB)")

        end_time = self.env.now
        self.server_processing_time = end_time - start_time

        print(f"{self.name} completed request: {request} "
              f"(Total Time: {end_time - start_time:.2f} ms)")

env = simpy.Environment()

user_service_instance = Microservice(env, "User Service", 10)
servers = [Server(env, f"Server {i+1}", latency=0.1*i, timeout=0.001*i, read_time=0.02*i, write_time=0.01*i) for i in range(NUM_SERVERS)]
load_balancer = LoadBalancer(env, servers)

# Create and run the user_service process
user_service_process = env.process(user_service(env, load_balancer, user_service_instance))

# Create and run server processes
for server in servers:
    env.process(server.process_request(f"Initial Request for {server.name}"))

env.run(until=30)

TOTAL_PROCESSES_INITIALIZED = TOTAL_PROCESS_TIMEOUTS + TOTAL_PROCESSES_STARTED
# timeout_percentage = (TOTAL_PROCESS_TIMEOUTS / TOTAL_PROCESSES_INITIALIZED) * 100

print("\nOverall Statistics:\n")
print(f"User Services Initialized: {TOTAL_PROCESSES_INITIALIZED}")
print(f"User Services Started: {TOTAL_PROCESSES_STARTED}")
print(f"User Services Processes Timed Out: {TOTAL_PROCESS_TIMEOUTS}")
print(f"Services started on Server: {TOTAL_SERVER_PROCESSES_STARTED}")
print(f"Services timed out on Server: {TOTAL_SERVER_PROCESSES_FAILED}")
print("=============================================")
print("Costs and Time Statistics:\n")
print(f"Total Services Processing Time: {TOTAL_PROCESSING_TIME}")
print(f"Total Network Costs: {TOTAL_NETWORK_COST}")
print(f"Total Memory used: {TOTAL_MEMORY_USED}")
# print(f"Timeout Percentage: {timeout_percentage:.2f}%")
print("=============================================")
print("Service Statistics:\n")
print(f"User Service Processing Time: {user_service_instance.service_processing_time:.2f} ms")
print(f"User Service Network Cost: {user_service_instance.service_network_cost:.2f} W")
print(f"User Service Memory Used: {user_service_instance.service_memory_used:.2f} KB")
print("=============================================")
print("Loadbalancer Statistics:\n")
print(f"LoadBalancer Processing Time: {load_balancer.assign_time_consumption:.2f} ms")
print(f"LoadBalancer Network Cost: {load_balancer.lb_network_cost:.2f} W")
print("=============================================")
print("\nServer Statistics:\n")

# Sort the servers based on their names
servers.sort(key=lambda server: server.name)

for server in servers:
    print(f"{server.name} Processes Started: {server.server_processes_started}")
    print(f"{server.name} Processes Failed: {server.server_processes_error}")
    print(f"{server.name} Processing Time: {server.server_processing_time:.2f} ms")
    print(f"{server.name} Process Cost: {server.process_cost:.2f} W")
    print(f"{server.name} Network Cost: {server.server_network_cost:.2f} W")
    print(f"{server.name} Memory Used: {server.server_memory_used:.2f} KB")
    print(f"{server.name} Read Time: {server.server_read_time:.2f} ms")
    print(f"{server.name} Write Time: {server.server_write_time:.2f} ms")
    print("---------------------------------------------")
