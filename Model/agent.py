import numpy as np
import math
from Controllers.states import *
from World.config import *

"""
The Agent class provides most of the utility you need to manipulate the agent.
There are three movement options: move(), repulse_move(), and random_walk().
Currently, the agent can use either FSM or BT implementations, as the data
needed for both are initialized in its constructor.
NOTE: agent.neighbors is a list of int, each int corresponding to a neighbor's ID.
To query for a neighbor's info, call agent.sim.get_agent_x() (x being the info you want).
See simulation.py for what information can be retrieved.
"""
class Agent:
    def __init__(self, id, pos, speed, theta, hunger, sim, attr_factor=1.0, orient_factor=1.0, repulse_factor=1.0,
                 site=None, network=None, group_id=None, following=None, neighbors=None, group_neighbors=None):
        self.id = id # an int representing the agent's unique ID
        self.pos = pos # where the agent is in the world
        self.state = NetworkFlockState(NET_FLOCK_NAME, (0, 255, 0), self) # the state the agent is currently in; change here to determine starting state
        self.speed = speed # how fast the agent moves
        self.theta = theta # the angle the agent is facing
        self.angular_velocity = 0.0 # how fast the agent's theta can change
        self.hunger = hunger # represents how hungry the agent is (lower hunger = more hungry)
        self.sim = sim # the simulation the agent is in; used so the agent can query for simulation information
        self.attr_factor = attr_factor # determines how much the agent will attract toward its neighbors, range(0.5, 1]
        self.orient_factor = orient_factor # determines how much the agent will orient to be like its neighbors, range(0.5, 1]
        self.rpls_factor = repulse_factor # determines how much the agent will space itself from its neighbors, range(0.5, 1]
        self.site = site # the site the agent is currently trying to get to
        self.last_known_sites = [] # the sites the agent remembers
        if site != None:
            self.last_known_sites.append(site)
        self.network = network # the matrix representation of the agent's group network; currently unused
        self.group_id = group_id # a binary vector determining which group an agent belongs to
        self.following = following # the neighbor that the agent is currently following
        # FOR BEHAVIOR TREE IMPLEMENTATION
        self.neighbors = neighbors # an agent's neighbors
        self.group_neighbors = group_neighbors # the agent's neighbors that also belong to the agent's group
        self.potential_sites = None # a list of sites the agent can choose from to go to, updated every tick()
        self.bt = None # the behavior tree that controls the agent
        self.timer = 0 # a timer used for several behaviors

    """
    Performs state actions
    """
    def update(self, neighbors, sites, predators):
        # get reading (neighbors, sites)
        # calculate neighbor task densities
        # do state actions
        self.state.update(neighbors, sites, predators)
        self.state.move(neighbors, predators)
    
    """
    Move like Boids with group detection.
    If toggled, agents will have greater range of movement, but not group as well.
    See Brown et. al in References.
    """
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
    
    """
    Move agent using graph laplacian.
    If toggled, agents will self sort into groups better, but not spread out as much
    """
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

    """
    Randomly walk in a direction
    """
    def random_walk(self, potency=1.0):
        self.theta += np.random.uniform(-np.pi/12, np.pi/12) % (2*np.pi)
        self.pos += np.array([np.cos(self.theta), np.sin(self.theta)]) * DT * 10 * potency

    ### UTILS ###

    """
    Returns a direction vector toward where the agent is facing
    """
    def heading(self):
        return np.array([np.cos(self.theta), np.sin(self.theta)])

    """
    Returns a bool stating whether or not an agent reached a site
    """
    def at_site(self, site=None):
        if site != None:
            if math.dist(site.pos, self.pos) <= site.radius:
                return True
        return False

    """
    Adds a site to memory; handles removing previous sites from memory
    SHOULD BE CALLED WHENEVER A NEW SITE IS DISCOVERED i.e. when agent.site is set
    """
    def add_site(self, site):
        self.last_known_sites.append(site)
        if len(self.last_known_sites) > MAX_SITE_MEMORY:
            self.last_known_sites.pop(0)

