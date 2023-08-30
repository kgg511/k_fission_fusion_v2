import agent as ag
from states import MAX_HUNGER, SPEED_THRESHOLD
import feeding_site
import predator as pred
import numpy as np
import math

# SIMULATION SET UP
NUM_AGENTS = 50
WORLD_SIZE = 10
NUM_ITERS = 100
NUM_SITES = 3
NUM_PREDS = 2
SITE_REGEN_TIME = 10
SITE_MAX_RESOURCE = 200

class Simulation:
    def __init__(self):
        self.avg_hunger = 0 # a metric for statistical purposes only haha
        self.prev_state = dict()
        self.agents = self.build_agents()
        self.sites = self.build_sites()
        self.predators = self.build_predators()
        self.avg_hunger = float(self.avg_hunger / NUM_AGENTS)

    def build_agents(self):
        agents = []
        for i in range(NUM_AGENTS):
            pos = np.array([np.random.uniform(0, WORLD_SIZE), np.random.uniform(0, WORLD_SIZE)])
            speed = np.random.uniform(1.0, SPEED_THRESHOLD)
            theta = np.random.uniform(-np.pi, np.pi)
            hunger = np.random.randint(MAX_HUNGER/2, MAX_HUNGER)
            attraction = np.random.uniform(0.25, 1.0)
            repulsion = np.random.uniform(0.25, 1.0)
            agents.append(ag.Agent(i, pos, speed, theta, hunger, self, attr_factor=attraction, repulse_factor=repulsion))
            self.prev_state.update({i: [pos, 1.0, np.array([np.cos(theta), np.sin(theta)])]})
            self.avg_hunger += hunger
            # print(f"Agent {i}: attraction = {attraction}, repulsion = {repulsion}, speed = {speed}")
        return agents

    def build_sites(self):
        sites = []
        for i in range(NUM_SITES):
            pos = np.array([np.random.uniform(0, WORLD_SIZE), np.random.uniform(0, WORLD_SIZE)])
            radius = np.random.randint(1, WORLD_SIZE * 0.25)
            # resources = np.random.randint(SITE_MAX_RESOURCE//2, SITE_MAX_RESOURCE + 1)
            sites.append(feeding_site.Site(pos, radius, SITE_REGEN_TIME, SITE_MAX_RESOURCE))
            # print(f"Site {i}: {pos}")
        return sites

    def build_predators(self):
        predators = []
        for i in range(NUM_PREDS):
            pos = np.array([np.random.uniform(0, WORLD_SIZE), np.random.uniform(0, WORLD_SIZE)])
            theta = np.random.uniform(-np.pi, np.pi)
            predators.append(pred.Predator(pos, theta, self, speed=SPEED_THRESHOLD))
            # print(f"Predator {i} starting pos: {pos}")
        return predators
    
    def get_predators(self, agent):
        predators = []
        for predator in self.predators:
            if math.dist(agent.pos, predator.pos) <= pred.SENSING_RADIUS:
                predator.neighbors.append(agent)
                if math.dist(agent.pos, predator.pos) <= ag.SENSING_RADIUS:
                    predators.append(predator)
        return predators

    def get_neighbor_ids(self, agent):
        neighbors = []
        for neighbor in self.agents:
            if neighbor.id != agent.id and math.dist(neighbor.pos, agent.pos) < ag.SENSING_RADIUS:
                neighbors.append(neighbor.id)
        return neighbors
    
    def get_agent_pos(self, id):
        return self.prev_state.get(id)[0]
    
    def get_agent_speed(self, id):
        return self.prev_state.get(id)[1]
    
    def get_agent_heading(self, id):
        return self.prev_state.get(id)[2]

    def get_sites(self, agent):
        sites = []
        for site in self.sites:
            if site.is_available():
                if math.dist(site.pos, agent.pos) <= ag.SENSING_RADIUS + site.radius:
                    sites.append(site)
        return sites
    