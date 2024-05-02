from Model.agent import Agent
from Model.feeding_site import Site
from Model.predator import Predator
from World.config import *
from Controllers.bt_construction import build_bt, build_ppa_bt

import numpy as np
import math

"""
Simulation() is the base simulation class, and it manages the simulation by retrieving
information about all agents for other agents, and updating the agents and the environment.
There are two methods that should be overridden: update_agent() and get_neighbor_ids().
If information about an agent that is not the agent's self is needed, call
agent.sim.get_agent_x() (x being the info you need).
"""
class Simulation:
    def __init__(self):
        self.avg_hunger = 0 # Measures the mean hunger of all the agents at any given point
        self.prev_state = dict() # Keeps track of agent information prior to the current' iteration's update; key: agent_id, value: [pos, speed, heading]
        self.agent_colors = [] # Tracks the agents' group's color for use for the display; assumes self.agents and self.agent_colors refer to the same agent at the same index
        self.agents = self.build_agents() # A list of the agents in the simulation
        self.sites = self.build_sites() # A list of the sites in the simulation
        self.predators = self.build_predators() # A list of the predators in the simulation
        self.avg_hunger = float(self.avg_hunger / NUM_AGENTS)

    def build_agents(self):
        agents = []
        group_sizes = np.zeros(NUM_GROUPS)
        for i in range(NUM_AGENTS): # TODO: generate agent colors based on group so as to not rely on hardcoding
            # generate group_id
            group_num = np.random.choice(list(range(NUM_GROUPS)))
            if group_sizes[group_num] > MAX_NETWORK_SIZE:
                group_num = np.random.choice(list(range(NUM_GROUPS)))
            group_id = np.zeros(NUM_GROUPS)
            group_id[group_num] = 1
            group_sizes[group_num] += 1

            self.agent_colors.append(COLORS.get(group_num))

            pos = np.array([np.random.uniform(0, WORLD_SIZE), np.random.uniform(0, WORLD_SIZE)])
            speed = np.random.uniform(1.0, MAX_SPEED)
            theta = np.random.uniform(-np.pi, np.pi)
            hunger = np.random.randint(MAX_HUNGER/2, MAX_HUNGER)
            attraction = np.random.uniform(0.25, 1.0)
            repulsion = np.random.uniform(0.25, 1.0)

            agents.append(Agent(i, pos, speed, theta, hunger, self, attr_factor=attraction, repulse_factor=repulsion, network=[], group_id=group_id))
            
            # Behavior Tree
            agents[i].bt = build_bt(agents[i])

            # simulation book-keeping
            self.prev_state.update({i: [pos, speed, np.array([np.cos(theta), np.sin(theta)])]})
            self.avg_hunger += hunger
        return agents

    def build_sites(self):
        sites = []
        for i in range(NUM_SITES):
            pos = np.array([np.random.uniform(0, WORLD_SIZE), np.random.uniform(0, WORLD_SIZE)])
            radius = np.random.randint(1, SITE_MAX_RADIUS)
            # resources = np.random.randint(SITE_MAX_RESOURCE//2, SITE_MAX_RESOURCE + 1)
            sites.append(Site(pos, radius, SITE_REGEN_TIME, SITE_MAX_RESOURCE))
            # print(f"Site {i}: {pos}")
        return sites

    def build_predators(self):
        predators = []
        for i in range(NUM_PREDS):
            pos = np.array([np.random.uniform(0, WORLD_SIZE), np.random.uniform(0, WORLD_SIZE)])
            theta = np.random.uniform(-np.pi, np.pi)
            predators.append(Predator(pos, theta, self, speed=MAX_SPEED))
            # print(f"Predator {i} starting pos: {pos}")
        return predators
    
    """
    Creates a matrix representation of the group networks 
    """
    def build_neighbor_matrix(self): # TODO: repurpose for sorting groups
        for i in range(0, NUM_AGENTS):
            for j in range(i, NUM_AGENTS):
                if i != j:
                    if len(self.agents[i].network) < MAX_NETWORK_SIZE and len(self.agents[j].network) < MAX_NETWORK_SIZE:
                        if np.random.choice([0, 1]) == 1:
                            self.agents[i].network.append(j)
                            self.agents[j].network.append(i)
    
    """
    Returns a list of sites that are within the agent's detection radius
    """
    def get_sites(self, agent):
        sites = []
        for site in self.sites:
            if site.is_available():
                if math.dist(site.pos, agent.pos) <= AGENT_SENSING_RADIUS + site.radius:
                    sites.append(site)
        return sites

    """
    Returns a list of predators that are within an agent's detection radius
    """
    def get_predators(self, agent):
        predators = []
        for predator in self.predators:
            if math.dist(agent.pos, predator.pos) <= PREDATOR_SENSING_RADIUS:
                predator.neighbors.append(agent)
                if math.dist(agent.pos, predator.pos) <= AGENT_SENSING_RADIUS:
                    predators.append(predator)
        return predators
    
    """
    Each method in the get_agent_x() section:
    takes the agent's id and returns some information regarding the agent.
    These assume that the agent_id correlates with the agent's index is simulation.agents.
    """
    def get_agent_pos(self, agent_id):
        return self.prev_state.get(agent_id)[0]
    
    def get_agent_speed(self, agent_id):
        return self.prev_state.get(agent_id)[1]
    
    def get_agent_heading(self, agent_id):
        return self.prev_state.get(agent_id)[2]
    
    def get_agent_group_id(self, agent_id):
        return self.agents[agent_id].group_id
    
    def get_agent_site(self, agent_id):
        return self.agents[agent_id].site
    
    """
    Ensures agents don't go out of bounds
    """
    def handle_boundaries(self, agent):
        out_of_bounds = False
        if math.isclose(agent.pos[0], PADDING) or agent.pos[0] < PADDING:
            agent.pos[0] = PADDING + DT
            out_of_bounds = True

        if math.isclose(agent.pos[1], PADDING) or agent.pos[1] < PADDING:
            agent.pos[1] = PADDING + DT
            out_of_bounds = True

        if math.isclose(agent.pos[0], WORLD_SIZE - PADDING) or agent.pos[0] > WORLD_SIZE - PADDING:
            agent.pos[0] = WORLD_SIZE - PADDING - DT
            out_of_bounds = True

        if math.isclose(agent.pos[1], WORLD_SIZE - PADDING) or agent.pos[1] > WORLD_SIZE - PADDING:
            agent.pos[1] = WORLD_SIZE - PADDING - DT
            out_of_bounds = True

        if out_of_bounds:
            agent.hunger += 1

    def print_states(self):
        # print out in a list the current state of each agent
        info = []
        for agent in self.agents:
            if agent.state.name.startswith("NETWORK_"):
                info.append(agent.state.name[len("NETWORK_"):])
            else:
                info.append(agent.state.name)
        print(info)
        
    """
    Updates the world conditions (agent positions, predator positions, site conditions, etc.)
    """
    def update(self):
        self.print_states()
        for agent in self.agents:
            self.prev_state.update({agent.id: [agent.pos, agent.speed, agent.heading()]})
            self.update_agent(agent)
        for site in self.sites:
            site.update()

    ### FUNCTIONS CHILD NEEDS TO OVERRIDE ###
    """
    Pass in the information needed for the agent to update.
    """
    def update_agent(self, agent):
        agent.hunger -= 1
        self.avg_hunger += agent.hunger
        self.handle_boundaries(agent)

    """
    Returns a list of integers representing the IDs of the agent's neighbors.
    NOTE: get_neighbor_ids assumes the IDs correspond to the index of the agent in self.agents.
    """
    def get_neighbor_ids(self, agent):
        pass

class BT_Simulation(Simulation):
    def __init__(self):
        super().__init__()

    def get_neighbor_ids(self, agent):
        neighbors = []
        group_neighbors = []
        for neighbor in self.agents:
            if neighbor.id != agent.id and math.dist(neighbor.pos, agent.pos) < AGENT_SENSING_RADIUS:
                neighbors.append(neighbor.id)
                if np.array_equal(self.get_agent_group_id(neighbor.id), self.get_agent_group_id(agent.id)):
                    group_neighbors.append(neighbor.id)
        return neighbors, group_neighbors
    
    """
    Updates what the agent can see then tick() the agent's behavior tree
    """
    def update_agent(self, agent):
        agent.neighbors, agent.group_neighbors = self.get_neighbor_ids(agent)
        agent.potential_sites = self.get_sites(agent)
        agent.bt.tick()
        super().update_agent(agent)
    
class FSM_Simulation(Simulation):
    def __init__(self):
        super().__init__()

    def get_neighbor_ids(self, agent):
        neighbors = []
        for neighbor in self.agents:
            if neighbor.id != agent.id and math.dist(neighbor.pos, agent.pos) < AGENT_SENSING_RADIUS:
                neighbors.append(neighbor.id)
        return neighbors

    def update_agent(self, agent):
        neighbors = self.get_neighbor_ids(agent)
        sites = self.get_sites(agent)
        predators = self.get_predators(agent)
        agent.update(neighbors, sites, predators)
        super().update_agent(agent)
