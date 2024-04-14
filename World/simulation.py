from Model.agent import Agent
from Model.feeding_site import Site
from Model.predator import Predator
from World.config import *
from Controllers.bt_construction import build_bt, build_ppa_bt

import numpy as np
import math

class Simulation:
    def __init__(self):
        self.avg_hunger = 0 # a metric for statistical purposes only haha
        self.prev_state = dict()
        self.agent_colors = []
        self.agents = self.build_agents()
        self.sites = self.build_sites()
        self.predators = self.build_predators()
        self.avg_hunger = float(self.avg_hunger / NUM_AGENTS)

    def build_agents(self):
        agents = []
        group_sizes = np.zeros(NUM_GROUPS)
        for i in range(NUM_AGENTS): # TODO: generate agent colors based on group
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
            self.prev_state.update({i: [pos, 1.0, np.array([np.cos(theta), np.sin(theta)])]})
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
    
    def build_neighbor_matrix(self): # for list representation of network, UNUSED
        for i in range(0, NUM_AGENTS):
            for j in range(i, NUM_AGENTS):
                if i != j:
                    if len(self.agents[i].network) < MAX_NETWORK_SIZE and len(self.agents[j].network) < MAX_NETWORK_SIZE:
                        if np.random.choice([0, 1]) == 1:
                            self.agents[i].network.append(j)
                            self.agents[j].network.append(i)
    
    def get_sites(self, agent):
        sites = []
        for site in self.sites:
            if site.is_available():
                if math.dist(site.pos, agent.pos) <= AGENT_SENSING_RADIUS + site.radius:
                    sites.append(site)
        return sites

    def get_predators(self, agent):
        predators = []
        for predator in self.predators:
            if math.dist(agent.pos, predator.pos) <= PREDATOR_SENSING_RADIUS:
                predator.neighbors.append(agent)
                if math.dist(agent.pos, predator.pos) <= AGENT_SENSING_RADIUS:
                    predators.append(predator)
        return predators
    
    def get_agent_pos(self, id):
        return self.prev_state.get(id)[0]
    
    def get_agent_speed(self, id):
        return self.prev_state.get(id)[1]
    
    def get_agent_heading(self, id):
        return self.prev_state.get(id)[2]
    
    def get_agent_group_id(self, agent_id):
        return self.agents[agent_id].group_id
    
    # TODO: technically works but is there a better way?
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

    def update(self):
        for agent in self.agents:
            self.update_agent(agent)
        for site in self.sites:
            site.update()

    ### FUNCTIONS CHILD NEEDS TO OVERRIDE ###
    def update_agent(self, agent):
        agent.hunger -= 1
        self.avg_hunger += agent.hunger
        self.handle_boundaries(agent)

    def get_neighbor_ids(self, agent):
        return

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
