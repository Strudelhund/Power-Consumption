# nur noch service_process_request fehlt!

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
        self.timeout_probability = timeout  # 0.00002
        self.service_timeouts = 0
        self.service_started = 0

    def service_process_request(self, request, process_id):
        global TOTAL_PROCESSING_TIME
        global TOTAL_NETWORK_COST
        global TOTAL_MEMORY_USED
        global TOTAL_PROCESS_TIMEOUTS
        global TOTAL_PROCESSES_STARTED
        global TOTAL_PROCESSES_INITIALIZED

        # Initialize a service
        TOTAL_PROCESSES_INITIALIZED += 1
        print(f"Service {self.name} Process {process_id} request initialized")

        # Simulate runtime service error/timeouts/etc
        if random.random() < self.timeout_probability:
            print(f"Service {self.name} Process {process_id} request failed")
            self.service_timeouts += 1
            error_handling_time = random.uniform(0.5, 3)
            yield self.env.timeout(error_handling_time)
        else:
            # Start a service on a server
            print(f"Service {self.name} Process {process_id} request started")
            self.service_started += 1
            # Simulate service process time
            process_time = random.uniform(1, 9)
            yield self.env.timeout(process_time)

            # Simulate service network cost
            network_cost = random.uniform(0.002, 0.3)

            # Simulate service memory usage
            memory_used = random.uniform(1, 10)

            self.process_count += 1
            self.service_network_cost += network_cost
            self.service_memory_used += memory_used
            self.service_processing_time += process_time

            print(
                f"{self.name} Process {process_id} processed request: {request} "
                f"(Processing Time: {process_time:.2f} ms, Network Cost: {network_cost:.2f} W, "
                f"Memory Used: {memory_used:.2f} KB)"
            )

        print(f"Service {self.name} Process {process_id} request finished")


class LoadBalancer:
    def __init__(self, env, servers):
        self.env = env
        self.servers = servers
        self.lb_network_cost = 0
        self.assing_time_consumption = 0

    def assign_task(self, request, process_id):
        print(f"Assign task Process {process_id} initialized")
        # Time the load balancer assigns task to server
        start_time = self.env.now

        # Round Robin Load Balancing:
        # Pop the first server from the list, which represents the next server to handle the request.
        selected_server = self.servers.pop(0)

        # Append the selected server back to the end of the list, making it the last in line for the next request.
        self.servers.append(selected_server)

        # Track the network cost of load balancing
        network_cost = random.uniform(0.002, 0.3)
        self.lb_network_cost += network_cost

        # Record LoadBalancer time consumption after a server has processed the request
        end_time = self.env.now
        self.assing_time_consumption += end_time - start_time

        # Introduce a delay for assignment before returning the selected server
        yield self.env.timeout(20)

        # Return the selected server to be assigned the task.
        print(f"Assign task Process {process_id} finished")
        return selected_server


def user_requests(env, load_balancer, user_service_instance):
    process_id = 1
    while True:
        print(f"User request Process {process_id} started")
        request = f"User Request at {env.now}"

        # Assign a server for the user request using the load balancer
        selected_server = yield env.process(load_balancer.assign_task(request, process_id))

        # Start the server process on the selected server
        selected_server_process = env.process(
            selected_server.server_process_request(request, process_id)
        )

        # Wait for the server process to complete or be interrupted
        try:
            yield selected_server_process
        except simpy.Interrupt:
            print(f"User request Process {process_id} failed")
            print(f"User Request Process {process_id} received interrupt for request: {request}")

        # Introduce some delay before the next user request
        print(f"User request Process {process_id} finished")
        yield env.timeout(random.uniform(1, 7))
        process_id += 1


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

    def server_process_request(self, request, process_id):
        print(f"{self.name} Process {process_id}  task started")
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
            print(f"{self.name} Process {process_id}  task failed")
            self.server_processes_error += 1
            yield self.env.timeout(10)
        else:
            # Simulate server processing time
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

            print(
                f"{self.name} Process {process_id} processed request: {request} "
                f"(Processing Time: {process_time:.2f} ms, Network Cost: {network_cost:.2f} W, "
                f"Memory Used: {memory_used:.2f} KB)"
            )

        end_time = self.env.now
        self.server_processing_time = end_time - start_time

        print(f"{self.name} Process {process_id}  task finished")


env = simpy.Environment()

servers = [
    Server(env, f"Server {i+1}", latency=0.1 * i, timeout=0.001 * i, read_time=0.02 * i, write_time=0.01 * i)
    for i in range(NUM_SERVERS)
]
load_balancer = LoadBalancer(env, servers)
user_service_instance = Microservice(env, "User Service", 10)

# Create and run the user_requests process
user_service_process = env.process(user_requests(env, load_balancer, user_service_instance))

# Create and run server processes
for server in servers:
    env.process(server.server_process_request(f"Initial Request for {server.name}", 0))

env.run(until=3000)

TOTAL_PROCESSES_INITIALIZED = TOTAL_PROCESS_TIMEOUTS + TOTAL_PROCESSES_STARTED
# timeout_percentage = (TOTAL_PROCESS_TIMEOUTS / TOTAL_PROCESSES_INITIALIZED) * 100

print("\nOverall Statistics:\n")
print(f"User Requests Initialized: {TOTAL_PROCESSES_INITIALIZED}")
print(f"User Requests Started: {TOTAL_PROCESSES_STARTED}")
print(f"User Requests Processes Timed Out: {TOTAL_PROCESS_TIMEOUTS}")
print(f"Services started on Server: {TOTAL_SERVER_PROCESSES_STARTED}")
print(f"Services timed out on Server: {TOTAL_SERVER_PROCESSES_FAILED}")
print("---------------------------------------------")
print("\Costs and Time Statistics:\n")
print(f"Total Services Processing Time: {TOTAL_PROCESSING_TIME}")
print(f"Total Network Costs: {TOTAL_NETWORK_COST}")
print(f"Total Memory used: {TOTAL_MEMORY_USED}")
# print(f"Timeout Percentage: {timeout_percentage:.2f}%")
print("=============================================")
print("\Service Statistics:\n")
print(f"User Service Processing Time: {user_service_instance.service_processing_time:.2f} ms")
print(f"User Service Network Cost: {user_service_instance.service_network_cost:.2f} W")
print(f"User Service Memory Used: {user_service_instance.service_memory_used:.2f} KB")
print("=============================================")
print("\Loadbalancer Statistics:\n")
print(f"LoadBalancer Processing Time: {load_balancer.assing_time_consumption:.2f} ms")
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
