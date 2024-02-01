import matplotlib.pyplot as plt
import numpy as np
import World.simulation as sim
from Controllers.states import EXPLORE_NAME, LOW_DENSE_NAME, HIGH_DENSE_NAME, REST_NAME, FLEE_NAME

NUM_TRIALS = 50

# SIMULATION SET UP
def setup_simulation():
    simulation = sim.Simulation()
    # simulation.build_neighbor_matrix()
    sites_x = []
    sites_y = []
    sites_radius = []
    for site in simulation.sites:
        sites_x.append(site.pos[0])
        sites_y.append(site.pos[1])
        sites_radius.append(20*2**site.radius)
    return simulation, sites_x, sites_y, sites_radius

# GUI SET UP
def setup_gui():
    fig = plt.figure(figsize=(sim.WORLD_SIZE, sim.WORLD_SIZE), dpi=96)
    ax = plt.gca()
    return fig, ax

def display(fig, ax, agents, predators, sites_x, sites_y, sites_radius, agent_colors):
    agent_x = []
    agent_y = []
    for agent in agents:
        agent_x.append(agent.pos[0])
        agent_y.append(agent.pos[1])
    pred_x = []
    pred_y = []
    for predator in predators:
        pred_x.append(predator.pos[0])
        pred_y.append(predator.pos[1])
    plt.cla()
    plt.scatter(sites_x, sites_y, s=sites_radius, c='#008888', alpha=0.5)
    plt.scatter(agent_x, agent_y, c=agent_colors)
    plt.scatter(pred_x, pred_y, c="#FF0000")
    ax.set(xlim=(0, sim.WORLD_SIZE), ylim=(0, sim.WORLD_SIZE))
    ax.set_aspect('equal')
    plt.grid()
    plt.pause(0.1)

# RECORD KEEPING
def run_simulation():
    simulation, sites_x, sites_y, sites_radius = setup_simulation()
    fig, ax = setup_gui()

    with open('sim_stats.txt', 'w') as file:
        file.write(f"Starting Hunger: {simulation.avg_hunger}\n")
        # RUN SIM
        for i in range(sim.NUM_ITERS):
            print(f"Iter{i}\n")
            simulation.avg_hunger = 0
            for agent in simulation.agents:
                
                # BT implementation
                simulation.bt_update()

                # nearby_predators = simulation.get_predators(agent)
                # agent.update(neighbors, sites, nearby_predators)
                simulation.avg_hunger += agent.hunger

            # file.write(f"\nIter {i}\nSite resources:\n")
            # for site in simulation.sites:
            #     site.update()
            #     file.write(f"{site.resource_count}\n")

            # for predator in simulation.predators:
            #     predator.update()

            simulation.avg_hunger = float(simulation.avg_hunger / sim.NUM_AGENTS)
            display(fig, ax, simulation.agents, simulation.predators, sites_x, sites_y, sites_radius, simulation.agent_colors)
            # file.write(f"Agent states:\n{agent_states}\n")
            file.write(f"Agent 0 theta: {simulation.agents[0].theta} heading: {simulation.agents[0].heading()}" +
                       f" speed: {simulation.agents[0].speed} state: {simulation.agents[0].state}\n")

        # file.write(f"Ending Hunger: {simulation.avg_hunger}")
    plt.show()

run_simulation()
