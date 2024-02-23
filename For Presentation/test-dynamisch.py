import simpy
import random

TOTAL_PROCESSES_INITIALIZED = 0
TOTAL_PROCESSES_STARTED = 0
TOTAL_PROCESS_TIMEOUTS = 0
TOTAL_PROCESS_SUCCESS = 0

TOTAL_SERVER_PROCESSES_STARTED = 0
TOTAL_SERVER_PROCESSES_FAILED = 0

TOTAL_PROCESSING_TIME = 0
TOTAL_NETWORK_COST = 0
TOTAL_MEMORY_USED = 0

TOTAL_LOADBALANCER_TIME_CONSUMPTION = 0

SERVICE_PROCESSING_TIME = 0
SERVICE_NETWORK_COST = 0
SERVICE_MEMORY_USED = 0

SERVER_PROCESSING_TIME = 0
SERVER_PROCESS_COST = 0
SERVER_NETWORK_COST = 0
SERVER_MEMORY_USED = 0

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
        global TOTAL_PROCESS_SUCCESS

        # Initialize a service
        TOTAL_PROCESSES_INITIALIZED += 1
        print(f"Service {self.name} Process {process_id} request initialized")

        # Simulate runtime service error/timeouts/error handling/etc
        if random.random() < self.timeout_probability:
            TOTAL_PROCESS_TIMEOUTS += 1
            print(f"Service {self.name} Process {process_id} request failed")
            self.service_timeouts += 1
            error_handling_time = random.uniform(0.5, 3)
            yield self.env.timeout(error_handling_time)
        else:
            TOTAL_PROCESSES_STARTED += 1
            print(f"Service {self.name} Process {process_id} request started")
            # Start a service on a server
            self.service_started += 1
            # Simulate service process time
            process_time = random.uniform(15, 30)
            yield self.env.timeout(process_time)

            # Simulate service network cost
            network_cost = random.uniform(0.002, 0.3)

            # Simulate service memory usage
            memory_used = random.uniform(1, 10)

            self.process_count += 1
            self.service_network_cost += network_cost
            self.service_memory_used += memory_used
            self.service_processing_time += process_time

            # test timeout
            yield self.env.timeout(100)

            print(
                f"{self.name} Process {process_id} processed request: {request} "
                f"(Processing Time: {process_time:.3f} ms, Network Cost: {network_cost:.3f} µW, "
                f"Memory Used: {memory_used:.3f} KB)"
            )

class LoadBalancer:
    def __init__(self, env, servers):
        self.env = env
        self.servers = servers
        self.lb_network_cost = 0
        self.assing_time_consumption = 0
        self.last_assigned_server_index = 0  # Track the last assigned server

    def assign_task(self, request, process_id):
        # assign a service to a server
        print(f"Assign task Process {process_id} initialized")

        start_time = self.env.now

        # round-robin logic
        # Loop through servers starting from the last assigned server
        for i in range(1, len(self.servers) + 1):
            server_index = (self.last_assigned_server_index + i) % len(self.servers)
            server = self.servers[server_index]

            if server.resource.count < server.capacity:  # Check if the server has available capacity
                req = server.resource.request()
                try:
                    yield req  # Acquire the resource

                    # Server has available capacity
                    # Track the network cost of load balancing
                    network_cost = random.uniform(0.002, 0.3)
                    self.lb_network_cost += network_cost

                    # Introduce a delay for assignment before returning the selected server
                    yield self.env.timeout(20)

                    # Record LoadBalancer time consumption after the delay
                    end_time = self.env.now
                    time_diff = end_time - start_time
                    self.assing_time_consumption += time_diff

                    # Update the last assigned server index
                    self.last_assigned_server_index = server_index

                    # Return the selected server to be assigned the task.
                    print(f"Assign task Process {process_id} to finished: {server}")
                    return server

                except simpy.Interrupt as interrupt:
                    # Handle the specific interrupt indicating capacity reached
                    if "Capacity Reached 0" in str(interrupt):
                        print(f"Assign task Process {process_id} interrupted due to server capacity reached. Trying the next server.")
                        continue
                    else:
                        # Re-raise the interrupt if it's not the specific one we're handling
                        raise interrupt

        # If no server has available capacity, log or take corrective actions
        print(f"No server with available capacity for task {process_id} -> RETRY")

        # Introduce a delay for assignment before returning None
        error_handling = random.uniform(0.002, 0.3)
        yield self.env.timeout(error_handling)

        # Record LoadBalancer time consumption after the delay
        end_time = self.env.now
        time_diff = end_time - start_time

        print(f"diff: {time_diff}")
        self.assing_time_consumption += time_diff

        print(f"Assign task Process {process_id} to a Server failed!")
        return None  # Skip the remaining code and return without processing the task

def user_requests(env, load_balancer, user_service_instance):
    global TOTAL_PROCESS_SUCCESS
    process_id = 1

    print(f"User request Process {process_id} started")

    while True:
        request = f"User Request at {env.now}"

        # Assign a server for the user request using the load balancer
        try:
            selected_server = yield env.process(load_balancer.assign_task(request, process_id))

            if selected_server is None:
                # Handle the case where no server has available capacity
                print(f"User Request {process_id} dropped due to lack of server capacity")
                break  # End the simulation when no server has available capacity
            else:
                # Start the server process on the selected server
                selected_server_process = env.process(
                    selected_server.server_process_request(request, process_id, user_service_instance)
                )

                # Wait for the server process to complete or be interrupted
                yield selected_server_process

                # Introduce some delay before the next user request
                yield env.timeout(random.uniform(1, 7))
                process_id += 1
                TOTAL_PROCESS_SUCCESS += 1
        except simpy.Interrupt as interrupt:
            # Handle the interrupt from the server process
            print(f"User Request {process_id} terminated due to server interruption: {interrupt}")
            break  # End the simulation when a server process is interrupted

class Server:
    def __init__(self, env, name, capacity, latency, timeout, read_time, write_time):
        self.env = env
        self.name = name
        self.capacity = capacity  # Maximum number of services that can be handled simultaneously
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
        self.resource = simpy.Resource(env, capacity=capacity)  # Resource for server capacity

    def server_process_request(self, request, process_id, user_service_instance):
        global SERVER_PROCESSING_TIME
        global SERVER_NETWORK_COST
        global SERVER_MEMORY_USED
        global SERVER_PROCESS_COST
        global TOTAL_SERVER_PROCESSES_STARTED
        global TOTAL_SERVER_PROCESSES_FAILED

        print(f"{self.name} - Available Capacity: {self.resource.capacity - self.resource.count} / {self.resource.capacity}")
        print(f"{self.name} Process {process_id} task started")

        start_time = self.env.now

        # Simulate server latency
        yield self.env.timeout(self.server_latency)

        # Simulate read time
        yield self.env.timeout(self.server_read_time)

        try:
            # Request resource to handle the service
            with self.resource.request() as req:
                # Check if the server has available capacity
                if req.triggered:
                    yield req  # Acquire the resource

                    if random.random() < self.server_timeout_probability:
                        self.server_processes_error += 1
                        TOTAL_SERVER_PROCESSES_FAILED += 1
                        error_handling_time = random.uniform(0.5, 3)
                        yield self.env.timeout(error_handling_time)
                    else:
                        TOTAL_SERVER_PROCESSES_STARTED += 1
                        # Simulate server processing time
                        process_time = random.uniform(0.5, 3)
                        SERVER_PROCESSING_TIME += process_time
                        yield self.env.timeout(process_time)

                        network_cost = random.uniform(0.002, 0.3)
                        SERVER_NETWORK_COST += network_cost
                        self.server_network_cost += network_cost
                        memory_used = random.uniform(1, 10)
                        SERVER_MEMORY_USED += memory_used
                        self.server_memory_used += memory_used
                        self.server_processes_started += 1
                        process_cost = random.uniform(0.001, 0.01)
                        SERVER_PROCESS_COST += process_cost
                        self.process_cost += process_cost

                        yield self.env.timeout(300)

                        try:
                            # Call service_process_request of the corresponding Microservice instance
                            yield self.env.process(user_service_instance.service_process_request(request, process_id))
                            # Release the resource after the process is done
                            self.resource.release(req)
                        except simpy.Interrupt:
                            # Handle the interrupt
                            print(f"{self.name} Process {process_id} task failed due to Microservice interruption")
                            return

                        # Simulate write time
                        yield self.env.timeout(self.server_write_time)

                        print(
                            f"{self.name} Process {process_id} processed request: {request} "
                            f"(Processing Time: {process_time:.3f} ms, Network Cost: {network_cost:.3f} µW, "
                            f"Memory Used: {memory_used:.3f} KB)"
                        )
                else:
                    # Server does not have available capacity
                    print(f"{self.name} Process {process_id} task dropped due to lack of server capacity")
                    raise simpy.Interrupt(f"{self.name} Server Capacity Reached 0 - Terminating Server Process")
        except simpy.Interrupt as interrupt:
            # Handle the interrupt
            print(f"{self.name} Process {process_id} task failed due to Server interruption")
            raise interrupt  # Re-raise the interrupt after handling it
            
        end_time = self.env.now
        self.server_processing_time = end_time - start_time


### Simulation Code ###

env = simpy.Environment()

servers = [
    Server(env, f"Server {i+1}", capacity=10, latency=0.1 * i, timeout=0.01 * i, read_time=0.02 * i, write_time=0.01 * i)
    for i in range(NUM_SERVERS)
]

load_balancer = LoadBalancer(env, servers)
user_service_instance = Microservice(env, "User Service", 0.03)  # 3% fail

# Create and run the user_requests process
user_service_process = env.process(user_requests(env, load_balancer, user_service_instance))

# Create and run server processes
for server in servers:
    env.process(server.server_process_request(f"Initial Request for {server.name}", 0, user_service_instance))

env.run(until=300000)

service_timeout_percentage = (TOTAL_PROCESS_TIMEOUTS/TOTAL_PROCESSES_INITIALIZED)*100
server_timeout_percentage = (TOTAL_SERVER_PROCESSES_FAILED/TOTAL_SERVER_PROCESSES_STARTED)*100

print("\n\n=============================================")
print("Overall Statistics:\n")
print(f"User Requests Initialized: {TOTAL_PROCESSES_INITIALIZED}")
print(f"Services started on Server: {TOTAL_SERVER_PROCESSES_STARTED}")
print(f"Server Timeouts: {TOTAL_SERVER_PROCESSES_FAILED}")
print(f"Service Timeouts: {TOTAL_PROCESS_TIMEOUTS}")
print(f"Server Failure Rate: {server_timeout_percentage:.2f}%")
print(f"Service Failure Rate: {service_timeout_percentage:.2f}%")
print("---------------------------------------------")
print(f"User Services Started: {TOTAL_PROCESSES_STARTED}")
print("---------------------------------------------")
print(f"User Requests finished: {TOTAL_PROCESS_SUCCESS}")
print("=============================================\n")
print("Service Statistics:\n")
print(f"User Service Processing Time: {user_service_instance.service_processing_time:.3f} ms")
print(f"User Service Network Cost: {user_service_instance.service_network_cost:.3f} µW")
print(f"User Service Memory Consumption: {user_service_instance.service_memory_used:.3f} KB")
print("=============================================\n")
print("LoadBalancer Statistics:\n")
print(f"LoadBalancer Processing Time: {load_balancer.assing_time_consumption:.3f} ms")
print(f"LoadBalancer Network Cost: {load_balancer.lb_network_cost:.3f} µW")
print("=============================================")
print("\nServer Statistics:\n")
print(f"Server Processing Time: {SERVER_PROCESSING_TIME:.3f} ms")
print(f"Server Process Cost: {SERVER_PROCESS_COST:.3f} µW")
print(f"Server Network Costs: {SERVER_NETWORK_COST:.3f} µW")
print(f"Server Memory Consumption: {SERVER_MEMORY_USED:.3f} KB")
print("=============================================\n")

# Sort the servers based on their names
servers.sort(key=lambda server: server.name)

for server in servers:
    print(f"{server.name} Processes Started: {server.server_processes_started}")
    print(f"{server.name} Processes Failed: {server.server_processes_error}")
    print(f"{server.name} Processing Time: {server.server_processing_time:.3f} ms")
    print(f"{server.name} Process Cost: {server.process_cost:.3f} µW")
    print(f"{server.name} Network Cost: {server.server_network_cost:.3f} µW")
    print(f"{server.name} Memory Used: {server.server_memory_used:.3f} KB")
    print(f"{server.name} Read Time: {server.server_read_time:.3f} ms")
    print(f"{server.name} Write Time: {server.server_write_time:.3f} ms")
    print("---------------------------------------------")
