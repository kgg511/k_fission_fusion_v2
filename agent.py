import numpy as np
import math
from states import *
from config import *

# note to self: future planning, factors will be floats from 0.5 to 1.0
class Agent:
    def __init__(self, id, pos, speed, theta, hunger, sim, attr_factor=1.0, orient_factor=1.0, repulse_factor=1.0,
                 site=None, network=None, group_id=None, following=None, neighbors=None, group_neighbors=None):
        self.id = id
        self.pos = pos
        self.state = NetworkRepulseState("NETWORK_EXP", (0, 255, 0), self)
        self.speed = speed
        self.theta = theta
        self.hunger = hunger
        self.sim = sim
        self.attr_factor = attr_factor
        self.orient_factor = orient_factor
        self.rpls_factor = repulse_factor
        self.site = site
        self.last_known_sites = []
        if site != None:
            self.last_known_sites.append(site)
        self.network = network # list representation
        self.group_id = group_id # binary vector representation
        self.following = following
        # FOR BEHAVIOR TREE IMPLEMENTATION temporary until blackboard is implemented
        self.neighbors = neighbors
        self.group_neighbors = group_neighbors
        self.potential_sites = None
        self.bt = None
        self.timer = 0

    def update(self, neighbors, sites, predators):
        # get reading (neighbors, sites)
        # calculate neighbor task densities
        # do state actions
        self.state.update(neighbors, sites, predators)
        self.state.move(neighbors, predators)

    def heading(self):
        return np.array([np.cos(self.theta), np.sin(self.theta)])
    
    # add random perturbations to theta DID NOT WORK AS WELL AS I THOUGHT
    # calculate repulsion + attraction + orientation towards neighbors
    # calculate speed as an observable stat rather than a settable property of the agent?
    # FIXME: fix world border handling
    # maybe using a repelling force based on distance to world border similar to how repulsion is calculated for neighbors?
    def move(self, neighbors, predators, attr_factor=1.0, rpls_factor=1.0):
        attraction = -len(neighbors) * self.pos
        repulsion = np.zeros(2)
        new_speed = self.speed

        for neighbor in neighbors:
            attraction += (self.pos - self.sim.get_agent_pos(neighbor))
            new_speed += self.sim.get_agent_speed(neighbor)
            c = self.sim.get_agent_pos(neighbor) - self.pos
            scaling_factor = c @ c
            if scaling_factor == 0:
                repulsion += c
            else:
                repulsion += c / scaling_factor

        attraction = attraction / len(neighbors)

        attraction *= self.attr_factor * attr_factor
        repulsion *= self.rpls_factor * rpls_factor
        self.theta += np.random.uniform(-np.pi/6, np.pi/6) % (2*np.pi)
        dx = attraction - repulsion + np.array([np.cos(self.theta), np.sin(self.theta)])
        self.pos = self.pos + dx * DT

        new_speed = new_speed / (len(neighbors) + 1)
        if new_speed > MAX_SPEED:
            new_speed = MAX_SPEED
        elif math.isclose(new_speed, 0.0):
            new_speed = 1.0
        self.speed = new_speed
        
    def repulse_move(self, neighbors, predators, attr_factor=1.0, diff_factor=1.0):
        # use a repulsion equation to space (boids-like repulsion)
        # use another repulsion equation to separate from other groups (original graph laplacian)
        if neighbors:
            repulsion = np.zeros_like(self.pos) # avoid collisions
            diffuse = np.zeros_like(self.pos) # separate from other groups
            attraction = np.zeros_like(self.pos)
            num_network_neighbors = 0
            num_outsider_neighbors = 0

            for neighbor in neighbors:
                # attract toward neighbors in network
                if np.array_equal(self.sim.get_agent_group_id(neighbor), self.group_id):
                    attraction += self.sim.get_agent_pos(neighbor)
                    num_network_neighbors += 1
                    pass

                # repel away from neighbors out of network
                else:
                    diffuse += self.sim.get_agent_pos(neighbor)
                    num_outsider_neighbors += 1

                # don't collide with other people
                c = self.sim.get_agent_pos(neighbor) - self.pos
                scaling_factor = c @ c
                if scaling_factor == 0:
                    scaling_factor = 1
                repulsion += c / scaling_factor

            attraction -= (self.pos * num_network_neighbors)
            diffuse = (num_outsider_neighbors * self.pos) - diffuse
            dx = (attraction * attr_factor) + (diffuse * diff_factor) - repulsion
            self.pos += (dx * DT)

    # general random walk
    def random_walk(self, potency=1.0):
        self.theta += np.random.uniform(-np.pi/12, np.pi/12) % (2*np.pi)
        self.pos += np.array([np.cos(self.theta), np.sin(self.theta)]) * DT * 10 * potency

    def at_site(self):
        if self.site != None:
            if math.dist(self.site.pos, self.pos) <= self.site.radius:
                return True
        return False

    def add_site(self, site):
        self.last_known_sites.append(site)
        if len(self.last_known_sites) > MAX_SITE_MEMORY:
            self.last_known_sites.pop(0)

    def set_bt(self, bt):
        self.bt = bt
        
    # def get_task_densities(self, neighbors):
    #     # get however many neighbors are doing which task
    #     # densities are num_neighbor_task/len(neighbors)
    #     pass
