import matplotlib.pyplot as plt
import numpy as np
import simulation as sim
from states import EXPLORE_NAME, LOW_DENSE_NAME, HIGH_DENSE_NAME, REST_NAME, FLEE_NAME

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
                agent.neighbors, agent.group_neighbors = simulation.get_neighbor_ids(agent)
                agent.potential_sites = simulation.get_sites(agent)
                agent.bt.tick()

                # nearby_predators = simulation.get_predators(agent)
                # agent.update(neighbors, sites, nearby_predators)
                simulation.avg_hunger += agent.hunger

            # file.write(f"\nIter {i}\nSite resources:\n")
            # for site in simulation.sites:
            #     site.update()
            #     file.write(f"{site.resource_count}\n")

            # for predator in simulation.predators:
            #     predator.update()
            #     file.write(f"Predator target: {predator.target}\n")

            simulation.avg_hunger = float(simulation.avg_hunger / sim.NUM_AGENTS)
            display(fig, ax, simulation.agents, simulation.predators, sites_x, sites_y, sites_radius, simulation.agent_colors)
            # file.write(f"Agent states:\n{agent_states}\n")
            file.write(f"Agent 0 theta: {simulation.agents[0].theta} heading: {simulation.agents[0].heading()}" +
                       f" speed: {simulation.agents[0].speed} state: {simulation.agents[0].state}\n")

        # file.write(f"Ending Hunger: {simulation.avg_hunger}")
    plt.show()

def run_simulation_mult():
    with open('experiment_results/world_size/experiment_stats_world_size_40.txt', 'w') as file:
        file.write("SIM CONFIG\n" +
                   f"NUM AGENTS={sim.NUM_AGENTS}\n" +
                   f"WORLD SIZE={sim.WORLD_SIZE}\n" +
                   f"NUM SITES={sim.NUM_SITES}\n" +
                   f"NUM PREDATORS={sim.NUM_PREDS}\n" +
                   f"SITE REGEN TIME={sim.SITE_REGEN_TIME}\n" +
                   f"SITE MAX RESOURCES={sim.SITE_MAX_RESOURCE}\n")
        ending_hunger = []
        avg_starting_hunger = 0.0
        avg_ending_hunger = 0.0
        avg_hunger_diff = 0.0
        avg_explore_agents = 0.0
        avg_rest_agents = 0.0
        avg_flee_agents = 0.0
        avg_site_resources = 0.0

        for i in range(NUM_TRIALS):
            simulation, sites_x, sites_y, sites_radius = setup_simulation()
            trial_avg_explore_agents = 0
            trial_avg_rest_agents = 0
            trial_avg_flee_agents = 0
            trial_avg_site_resources = 0

            file.write(f"\nTrial {i}: Starting hunger={simulation.avg_hunger}\n")
            avg_starting_hunger += simulation.avg_hunger

            for j in range(sim.NUM_ITERS):
                simulation.avg_hunger = 0
                agent_states = {EXPLORE_NAME: 0,
                        REST_NAME: 0,
                        FLEE_NAME: 0}
                
                for agent in simulation.agents:
                    neighbors = simulation.get_neighbor_ids(agent)
                    nearby_predators = simulation.get_predators(agent)
                    sites = simulation.get_sites(agent)
                    agent.update(neighbors, sites, nearby_predators) # replace object with actual site readings later
                    agent_states[agent.state.name] = agent_states.get(agent.state.name) + 1
                    simulation.avg_hunger += agent.hunger
                trial_avg_explore_agents += agent_states.get(EXPLORE_NAME)
                trial_avg_rest_agents += agent_states.get(REST_NAME)
                trial_avg_flee_agents += agent_states.get(FLEE_NAME)

                for site in simulation.sites:
                    site.update()
                    trial_avg_site_resources += site.resource_count

                for predator in simulation.predators:
                    predator.update()
                    
                simulation.avg_hunger = float(simulation.avg_hunger / sim.NUM_AGENTS)
                ending_hunger.append(simulation.avg_hunger)
                
            avg_ending_hunger += simulation.avg_hunger
            avg_hunger_diff += (avg_ending_hunger - avg_starting_hunger)

            # Process stats for trial
            trial_avg_explore_agents = float(trial_avg_explore_agents / sim.NUM_ITERS)
            trial_avg_rest_agents = float(trial_avg_rest_agents / sim.NUM_ITERS)
            trial_avg_flee_agents = float(trial_avg_flee_agents / sim.NUM_ITERS)
            trial_avg_site_resources = float(trial_avg_site_resources / (sim.NUM_SITES * sim.NUM_ITERS))

            # Do some processing for experiment
            avg_explore_agents += trial_avg_explore_agents
            avg_rest_agents += trial_avg_rest_agents
            avg_flee_agents += trial_avg_flee_agents
            avg_site_resources += trial_avg_site_resources

            # Record simulation results
            file.write(f"Ending Hunger={simulation.avg_hunger}\n")
            file.write(f"Avg State Nums\n{EXPLORE_NAME}={trial_avg_explore_agents}\n"
                    + f"{REST_NAME}={trial_avg_rest_agents}\n{FLEE_NAME}={trial_avg_flee_agents}\n")
            file.write(f"Avg Resources per Iter={trial_avg_site_resources}\n")
        
        # Process data for experiment
        avg_starting_hunger = avg_starting_hunger / NUM_TRIALS
        avg_ending_hunger = avg_ending_hunger / NUM_TRIALS
        avg_hunger_diff = avg_hunger_diff / NUM_TRIALS
        avg_explore_agents = avg_explore_agents / NUM_TRIALS
        avg_rest_agents = avg_rest_agents / NUM_TRIALS
        avg_flee_agents = avg_flee_agents / NUM_TRIALS
        avg_site_resources = avg_site_resources / NUM_TRIALS

        # Record experiment results
        file.write(f"\nOVERALL STATISTICS\n")
        file.write(f"Avg Starting Hunger={avg_starting_hunger}, Avg Ending Hunger={avg_ending_hunger}\n")
        file.write(f"Avg Hunger Difference={avg_hunger_diff}\n")
        file.write(f"Avg Site Resources per Iter={avg_site_resources}\n")
        file.write(f"AVG STATE NUMS\n{EXPLORE_NAME}={avg_explore_agents}\n"
                    + f"{REST_NAME}={avg_rest_agents}\n{FLEE_NAME}={avg_flee_agents}\n")
        
        return ending_hunger


run_simulation()
# experiment_ending_hunger = run_simulation_mult()

# # save data to .npz
# np.save(file='experiment_results/experiment_data/experiment_stats_world_size_40_data.npy', arr=experiment_ending_hunger, allow_pickle=False)

# # set up boxplot
# fig = plt.figure(figsize=(10,7))
# plt.boxplot(experiment_ending_hunger)

# # save boxplot as .jpg
# plt.savefig('experiment_results/graphs/experiment_stats_world_size_40_graph.jpg')

# # display
# plt.show()
