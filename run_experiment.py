import matplotlib.pyplot as plt
import numpy as np
from World.simulation import Simulation
from World.config import *

NUM_TRIALS = 100

def run_simulation_mult(filename):
    with open(filename, 'w') as file:
        file.write("SIM CONFIG\n" +
                   f"NUM AGENTS={NUM_AGENTS}\n" +
                   f"WORLD SIZE={WORLD_SIZE}\n" +
                   f"NUM SITES={NUM_SITES}\n" +
                   f"NUM PREDATORS={NUM_PREDS}\n" +
                   f"SITE REGEN TIME={SITE_REGEN_TIME}\n" +
                   f"SITE MAX RESOURCES={SITE_MAX_RESOURCE}\n")
        ending_hunger = []
        avg_starting_hunger = 0.0
        avg_ending_hunger = 0.0
        avg_hunger_diff = 0.0
        avg_explore_agents = 0.0
        avg_rest_agents = 0.0
        avg_flee_agents = 0.0
        avg_site_resources = 0.0
        print("Starting Experiment\n")

        for i in range(NUM_TRIALS):
            simulation = Simulation()
            trial_avg_explore_agents = 0
            trial_avg_rest_agents = 0
            trial_avg_flee_agents = 0
            trial_avg_site_resources = 0

            file.write(f"\nTrial {i}: Starting hunger={simulation.avg_hunger}\n")
            print("Starting Trial\n")
            avg_starting_hunger += simulation.avg_hunger
            start_hunger = simulation.avg_hunger

            for j in range(NUM_ITERS):
                simulation.avg_hunger = 0
                
                simulation.bt_update()
                    
                simulation.avg_hunger = float(simulation.avg_hunger / NUM_AGENTS)
                for site in simulation.sites:
                    trial_avg_site_resources += site.resource_count
                
            avg_ending_hunger += simulation.avg_hunger
            ending_hunger.append(simulation.avg_hunger)
            hunger_diff = simulation.avg_hunger - start_hunger
            avg_hunger_diff += hunger_diff

            # Process stats for trial
            trial_avg_explore_agents = float(trial_avg_explore_agents / NUM_ITERS)
            trial_avg_rest_agents = float(trial_avg_rest_agents / NUM_ITERS)
            trial_avg_flee_agents = float(trial_avg_flee_agents / NUM_ITERS)
            trial_avg_site_resources = float(trial_avg_site_resources / (NUM_SITES * NUM_ITERS))

            # Do some processing for experiment
            avg_explore_agents += trial_avg_explore_agents
            avg_rest_agents += trial_avg_rest_agents
            avg_flee_agents += trial_avg_flee_agents
            avg_site_resources += trial_avg_site_resources

            # Record simulation results
            file.write(f"Ending Hunger={simulation.avg_hunger}\n")
            # file.write(f"Avg State Nums\n{EXPLORE_NAME}={trial_avg_explore_agents}\n"
            #         + f"{REST_NAME}={trial_avg_rest_agents}\n{FLEE_NAME}={trial_avg_flee_agents}\n")
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
        # file.write(f"AVG STATE NUMS\n{EXPLORE_NAME}={avg_explore_agents}\n"
        #             + f"{REST_NAME}={avg_rest_agents}\n{FLEE_NAME}={avg_flee_agents}\n")
        
        return ending_hunger

filename = 'bt_default_config_test2'

experiment_ending_hunger = run_simulation_mult('../experiment_results/' + filename + '.txt')

# save data to .npz
np.save(file='../experiment_results/experiment_data/' + filename + '.npy', arr=experiment_ending_hunger, allow_pickle=False)

# set up boxplot
fig = plt.figure(figsize=(10,7))
plt.boxplot(experiment_ending_hunger)

# save boxplot as .jpg
plt.savefig('../experiment_results/graphs/' + filename + 'graph.jpg')

# display
plt.show()