import simpy
import random

class Microservice:
    def __init__(self, env, name):
        self.env = env
        self.name = name
        self.process_count = 0
        self.total_processing_time = 0
        self.total_network_cost = 0
        self.total_memory_used = 0
        self.timeout_probability = 0.0002  # Example: 0.02% chance of a timeout

    def process_request(self, request):
        # Simulate occasional timeout
        if random.random() < self.timeout_probability:
            print(f"{self.name} experienced a timeout for request: {request}")
            yield self.env.timeout(10)  # Return the generator directly
        else:
            # Simulate variations in process time
            process_time = random.uniform(0.5, 3)
            yield self.env.timeout(process_time)

            # Update processing, network cost, and memory usage statistics
            self.total_processing_time += process_time

            # Hypothetical network cost model
            network_cost = random.uniform(0.01, 0.1)
            self.total_network_cost += network_cost

            # Hypothetical memory usage model
            memory_used = random.uniform(1, 10)
            self.total_memory_used += memory_used

            print(f"{self.name} processed request: {request} "
                  f"(Processing Time: {process_time:.2f} units, Network Cost: {network_cost:.2f} units, "
                  f"Memory Used: {memory_used:.2f} units)")

class LoadBalancer:
    def __init__(self, env, servers):
        self.env = env
        self.servers = servers

    def assign_task(self, request):
        # Measure network communication time
        start_time = self.env.now
        network_communication_time = random.uniform(0.001, 0.03)
        yield self.env.timeout(network_communication_time)
        end_time = self.env.now

        # Hypothetical network cost model
        network_cost = random.uniform(0.01, 0.1)
        print(f"Network Communication Time: {end_time - start_time:.2f} units, Network Cost: {network_cost:.2f} units")

        # Hypothetical memory usage model
        memory_used = random.uniform(1, 5)

        # Update memory usage statistics for each server
        for server in self.servers:
            server.total_memory_used += memory_used

        # Use Round Robin algorithm to assign tasks to servers
        selected_server = self.servers.pop(0)
        self.servers.append(selected_server)

        # Return the selected server
        return selected_server

def user_service(env, load_balancer, servers):
    while True:
        # Simulate user making a request to the User Service
        request = f"User Request at {env.now}"
        print(f"User Service received request: {request}")

        # Forward request to Load Balancer
        selected_server = load_balancer.assign_task(request)

        # Create a new process for the selected server's process_request method
        selected_server_process = env.process(selected_server.process_request(request))

        # Measure processes started
        selected_server.process_count += 1

        # Simulate delay before the next user request
        yield env.timeout(random.uniform(1, 7))

        # Ensure the selected server process is properly terminated
        try:
            yield selected_server_process
        except simpy.Interrupt:
            print(f"User Service received interrupt for request: {request}")

# Create SimPy environment
env = simpy.Environment()

# Create microservices
user_service_instance = Microservice(env, "User Service")
server1 = Microservice(env, "Server 1")
server2 = Microservice(env, "Server 2")
server3 = Microservice(env, "Server 3")

# Create a list of servers for the load balancer
servers = [server1, server2, server3]

# Create a Round Robin load balancer
load_balancer = LoadBalancer(env, servers)

# Create processes for each microservice and the load balancer
env.process(user_service(env, load_balancer, servers))
env.process(server1.process_request("Initial Request 1"))
env.process(server2.process_request("Initial Request 2"))
env.process(server3.process_request("Initial Request 3"))

# Run the simulation
env.run(until=20)

# Display overall statistics including space and time complexity
print("\nOverall Statistics:")
print(f"User Service Processes Started: {user_service_instance.process_count}")
print(f"User Service Total Processing Time: {user_service_instance.total_processing_time:.2f} units")
print(f"User Service Total Network Cost: {user_service_instance.total_network_cost:.2f} units")
print(f"User Service Total Memory Used: {user_service_instance.total_memory_used:.2f} units")
for server in servers:
    print(f"{server.name} Processes Started: {server.process_count}")
    print(f"{server.name} Total Processing Time: {server.total_processing_time:.2f} units")
    print(f"{server.name} Total Network Cost: {server.total_network_cost:.2f} units")
    print(f"{server.name} Total Memory Used: {server.total_memory_used:.2f} units")
