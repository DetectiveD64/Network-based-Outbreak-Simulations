import networkx as nx
import matplotlib.pyplot as plt
import random

# Create a Scale-Free Network with 20,000 nodes
G = nx.barabasi_albert_graph(n=20000, m=3)  # 20,000 nodes, each new node connects to 3 existing nodes

# Randomize the number of Super-Spreaders
num_super_spreaders = random.randint(1, 10)  # Randomize the number of super-spreaders (1 to 10)

# Identify Super-Spreaders (Top k nodes with highest degrees)
super_spreaders = [node for node, degree in sorted(G.degree, key=lambda x: x[1], reverse=True)[:num_super_spreaders]]

# Infection Parameters
initial_infection_prob = 0.001  # Starting with a very low infection probability (0.1%)
timesteps = 150         # Maximum number of time steps to simulate (increase for longer simulation)
infection_timeline = []  # Store number of new infections per step

# Start with one infected super-spreader
infected = {super_spreaders[0]}  # Only one super-spreader is initially infected
recovered = set()  # Nodes that have recovered
recovery_timer = {}  # Dictionary to track recovery time of infected nodes
recovery_time = 20  # Increased recovery time (20 timesteps for slower recovery)
incubation_min = 10  # Minimum incubation period (in timesteps)
incubation_max = 20  # Maximum incubation period (in timesteps)

# Track the incubation timers for each infected individual
incubation_timers = {}

# Infection probability increases as the infection spreads
def get_infection_probability(t, initial_prob):
    """Gradually increases the infection probability over time."""
    max_prob = 0.0625  # Maximum infection probability (10%)
    growth_factor = 0.0003  # Rate of increase in infection probability
    return min(initial_prob + growth_factor * t, max_prob)

# Simulate Disease Spread with Slower Recovery and No Reinfection
for t in range(timesteps):
    # Get the infection probability for the current timestep
    infection_prob = get_infection_probability(t, initial_infection_prob)

    # New infections list at each timestep
    new_infections = set()

    # Handle Infection Spread
    for node in list(infected):
        # Only infect neighbors if the node is in the incubation period or is currently infected
        if node in incubation_timers and incubation_timers[node] > 0:
            # Incubating nodes can still infect others
            neighbors = list(G.neighbors(node))
            for neighbor in neighbors:
                # Only susceptible nodes that are not already infected or recovered
                if neighbor not in infected and neighbor not in recovered and random.random() < infection_prob:
                    new_infections.add(neighbor)
        elif node not in recovered:
            # Currently infected individuals (not yet recovered) can also spread the infection
            neighbors = list(G.neighbors(node))
            for neighbor in neighbors:
                # Only susceptible nodes that are not already infected or recovered
                if neighbor not in infected and neighbor not in recovered and random.random() < infection_prob:
                    new_infections.add(neighbor)

    # If there are new infections, update the infected set
    if new_infections:
        infected.update(new_infections)

    # Update incubation timers for infected nodes
    for node in list(infected):
        if node not in recovered and node not in recovery_timer and node not in incubation_timers:
            incubation_period = random.randint(incubation_min, incubation_max)  # Random incubation period
            incubation_timers[node] = incubation_period  # Assign the incubation period
    
    # Decrement incubation timers
    for node in list(incubation_timers.keys()):
        incubation_timers[node] -= 1
    
    # Update recovery timers for infected nodes that have passed the incubation period
    to_recover = [node for node, timer in incubation_timers.items() if timer == 0]  # Nodes that have finished incubation
    for node in to_recover:
        if node in infected:  # Check if the node is still infected
            recovered.add(node)
            infected.remove(node)
        del incubation_timers[node]  # Remove from incubation timers
        recovery_timer[node] = recovery_time  # Start recovery timer after incubation period

    # Handle recovery (slower recovery based on recovery time)
    to_recover = [node for node, timer in recovery_timer.items() if timer == 1]  # Nodes that are ready to recover
    for node in to_recover:
        if node in infected:  # Check if the node is still infected
            recovered.add(node)
            infected.remove(node)
        del recovery_timer[node]  # Remove from recovery timer

    # Decrement recovery timers
    for node in list(recovery_timer.keys()):
        recovery_timer[node] -= 1

    # Track new infections each step
    infection_timeline.append(len(new_infections))  # Store number of new cases at this step

# Plot Epidemic Curve as Histogram (New Cases at Each Time Step)
plt.figure(figsize=(10, 6))
plt.bar(range(len(infection_timeline)), infection_timeline, color="b")
plt.xlabel("Time Step")
plt.ylabel("New Infections")
plt.title(f"Epidemic Curve (Histogram)")
plt.grid()
plt.show()


