import numpy as np
import math
from Controllers.states import *
from World.config import *

# note to self: future planning, factors will be floats from 0.5 to 1.0
class Agent:
    def __init__(self, id, pos, speed, theta, hunger, sim, attr_factor=1.0, orient_factor=1.0, repulse_factor=1.0,
                 site=None, network=None, group_id=None, following=None, neighbors=None, group_neighbors=None):
        self.id = id
        self.pos = pos
        self.state = NetworkFlockState(NET_FLOCK_NAME, (0, 255, 0), self)
        self.speed = speed
        self.theta = theta
        self.angular_velocity = 0.0
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
        # FOR BEHAVIOR TREE IMPLEMENTATION
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
    
    # move like Boids with group detection
    def move(self, neighbors, predators, attr_factor=1.0, rpls_factor=1.0):
        if neighbors:
            repulsion = np.zeros_like(self.pos)
            attraction = np.zeros_like(self.pos)
            orientation = self.heading()

            # calculate repulsion, attraction, and orientation
            for neighbor in neighbors:
                neighbor_pos = self.sim.get_agent_pos(neighbor)
                # repulsion
                if math.dist(neighbor_pos, self.pos) <= AGENT_REPL_RADIUS:
                    dist_vect = neighbor_pos - self.pos
                    if dist_vect @ dist_vect > 0:
                        repulsion += dist_vect / (dist_vect @ dist_vect)
                    else:
                        repulsion += dist_vect
                # orient and attract only with neighbors within group
                if np.array_equal(self.sim.get_agent_group_id(neighbor), self.group_id):
                    # orientation
                    if math.dist(neighbor_pos, self.pos) <= AGENT_ORIENT_RADIUS:
                        orientation += self.sim.get_agent_heading(neighbor)

                    # attraction
                    attraction += neighbor_pos - self.pos

            repulsion = -repulsion
            norm_u_o = np.linalg.norm(orientation)
            orientation = orientation / norm_u_o if norm_u_o > 0 else np.array([np.cos(self.theta + np.pi/2),
                                                                                np.sin(self.theta + np.pi/2)])
            if (np.linalg.norm(attraction) > 0):
                attraction = attraction / np.linalg.norm(attraction)

            # get desired direction
            desired_dir = repulsion + orientation + attraction
            x, y = desired_dir

            # get desired heading
            desired_heading = np.arctan2(y, x)
            difference_in_heading = (((desired_heading - self.theta) + np.pi) % (2*np.pi)) - np.pi

            # calculate new heading and update
            angular_vel = K * difference_in_heading
            new_pos = self.pos + self.speed * self.heading() * DT
            new_theta = (((self.theta + (angular_vel * DT)) + np.pi) % (2*np.pi)) + np.pi

            self.pos = new_pos
            self.theta = new_theta
    
    # movement modeled more like particle diffusion via graph laplacian
    def repulse_move(self, neighbors, predators, attr_factor=1.0, diff_factor=1.0):
        # use a repulsion equation to space (boids-like repulsion)
        # use another repulsion equation to separate from other groups (diffusion)
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

    def at_site(self, site=None):
        if site != None:
            if math.dist(site.pos, self.pos) <= site.radius:
                return True
        return False

    def add_site(self, site):
        self.last_known_sites.append(site)
        if len(self.last_known_sites) > MAX_SITE_MEMORY:
            self.last_known_sites.pop(0)

