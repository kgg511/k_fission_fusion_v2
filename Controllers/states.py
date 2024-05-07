REST_COLOR = (255, 255, 255)
EXPLORE_COLOR = (0, 0, 0)
FLEE_COLOR = (255, 0, 0)
EXPLORE_NAME = "EXPLORE"
LOW_DENSE_NAME = "LOW_DENSE_EXPLORE"
HIGH_DENSE_NAME = "HIGH_DENSE_EXPLORE"
REST_NAME = "REST"
FLEE_NAME = "FLEE"
NET_FLOCK_NAME = "NETWORK_FLOCK"
NET_EXPLORE_NAME = "NETWORK_EXP"
NET_REST_NAME = "NETWORK_REST"
NET_GOTOSITE_NAME = "NETWORK_LEAD"
NET_GOTOHUB_NAME = "NETWORK_HUB"
NET_FOLLOW_NAME = "NETWORK_FOLLOW"

import numpy as np
import math
from World.config import *

"""
The base class for all the states. When making a new state:
1. override all three base methods
2. call super().method() within the overridden methods
"""
class State:
    def __init__(self, name, color, agent):
        self.name = name
        self.color = color
        self.agent = agent

    """
    update() should contain all the logic to transition to and from the state.
    """
    def update(self, neighbors, sites, predators):
        pass

    """
    move() should contain all the logic for the agent to move. Agent has two built-in methods for movement, depending
    on whether USE_BOIDS_MOVEMENT is true or false. Use self.agent.move() if True, and self.agent.repulse_move() if False.
    You can directly modify self.agent's properties.
    """
    def move(self, neighbors, predators):
        # handle repulsion away from world borders
        # FIXME: current behavior just has agents crowding the edges

        if math.isclose(self.agent.pos[0], PADDING) or self.agent.pos[0] < PADDING:
            self.agent.pos[0] = PADDING + DT
            self.agent.hunger += 1

        if math.isclose(self.agent.pos[1], PADDING) or self.agent.pos[1] < PADDING:
            self.agent.pos[1] = PADDING + DT
            self.agent.hunger += 1

        if math.isclose(self.agent.pos[0], WORLD_SIZE - PADDING) or self.agent.pos[0] > WORLD_SIZE - PADDING:
            self.agent.pos[0] = WORLD_SIZE - PADDING - DT
            self.agent.hunger += 1

        if math.isclose(self.agent.pos[1], WORLD_SIZE - PADDING) or self.agent.pos[1] > WORLD_SIZE - PADDING:
            self.agent.pos[1] = WORLD_SIZE - PADDING - DT
            self.agent.hunger += 1 # this will make it so their hunger doesn't keep deprecating out of bounds to help with stats?

"""
The Network-based States take into account neighbors that are part of self.agent's group in
either movement, transitioning, or both. These states are all part of the same state machine.
"""
### NETWORK-BASED STATES ###

class NetworkFlockState(State):
    def __init__(self, name, color, agent):
        super().__init__(name, color, agent)
        self.agent.site = None
        self.timer = AGENT_BORED_THRESHOLD

    def update(self, neighbors, sites, predators):
        super().update(neighbors, sites, predators)
        if sites:
            # random chance to actually want to go to site (default set to 50%?)
            if np.random.random() > 0.5:
                # make sure we don't go back to last_known_site so agents can wander away
                viable_sites = list(filter(lambda i: i not in self.agent.last_known_sites, sites))
                if len(viable_sites) > 0:
                    self.agent.site = viable_sites[np.random.randint(0, len(viable_sites))]
                    self.agent.add_site(self.agent.site)
                    self.agent.state = GoToSiteState(NET_GOTOSITE_NAME, (0, 0, 255), self.agent)
                    return

        for neighbor in neighbors:
            if np.array_equal(self.agent.sim.get_agent_group_id(neighbor), self.agent.group_id):
                if isinstance(self.agent.sim.agents[neighbor].state, GoToSiteState):
                    # random chance to listen to neighbor
                    if np.random.random() > 0.2:
                        self.agent.following = neighbor
                        self.agent.state = FollowState(NET_FOLLOW_NAME, (0, 100, 255), self.agent)
                        return
        
        if self.timer == 0:
            self.agent.state = NetworkExploreState(NET_EXPLORE_NAME, (100, 255, 0), self.agent)

    def move(self, neighbors, predators):
        if USE_BOID_MOVE:
            self.agent.move(neighbors, predators)
        else:
            self.agent.repulse_move(neighbors, predators)
        self.agent.random_walk(potency=0.5) # turning on random walk causes some jitter, but also prevents stagnation when no neighbors
        super().move(neighbors, predators)

class NetworkExploreState(State):
    def __init__(self, name, color, agent):
        super().__init__(name, color, agent)
        self.agent.site = None
        self.timer = AGENT_BORED_THRESHOLD

    def update(self, neighbors, sites, predators):
        super().update(neighbors, sites, predators)
        if self.timer == 0: #if timer runs out choose to flock or go to the hub
            if self.agent.hub != None and np.random.random() > 0.5:
                self.agent.site = self.agent.hub
                self.agent.state = GoToHubState(NET_GOTOHUB_NAME, (0, 0, 255), self.agent)
                return
            else:
                self.agent.state = NetworkFlockState(NET_FLOCK_NAME, (0, 255, 0), self.agent)
                return

        self.timer -= 1

        if sites:
            # random chance to go to a new site (not recently visited)
            if  np.random.random() > 0.7: # go to site
                viable_sites = list(filter(lambda i: i not in self.agent.last_known_sites, sites))
                if len(viable_sites) > 0:
                    self.agent.site = viable_sites[np.random.randint(0, len(viable_sites))]
                    self.agent.add_site(self.agent.site)
                    self.agent.state = GoToSiteState(NET_GOTOSITE_NAME, (0, 0, 255), self.agent)
                    return
            
    def move(self, neighbors, predators):
        self.agent.random_walk(potency=1.0)
        self.agent.move(neighbors, predators)
        
class NetworkRestState(State):
    def __init__(self, name, color, agent):
        super().__init__(name, color, agent)
        self.timer = AGENT_BORED_THRESHOLD

    # TODO: have a better way to transition out haha
    def update(self, neighbors, sites, predators):
        super().update(neighbors, sites, predators)
        self.agent.hunger += 2
        self.agent.site.resource_count -= 1
        # calculate group-id densities to determine how much more time they'll stay on site
        num_group_neighbors = 0
        if neighbors:
            for neighbor in neighbors:
                if np.array_equal(self.agent.sim.get_agent_group_id(neighbor), self.agent.group_id):
                    num_group_neighbors += 1

        # will eventually leave site if no group members are present OR if no neighbors present either
        else:
            self.timer = 0
        
        # assess if it is a good site
        if self.agent.hub == None or self.agent.site.resource_count > self.agent.hub.resource_count:
            self.agent.hub = self.agent.site

        if self.timer == 0 or num_group_neighbors == 0 or self.agent.hunger >= MAX_HUNGER or not self.agent.site.is_available():
            self.agent.speed = np.random.uniform(1.0, MAX_SPEED) # reset speed
            self.agent.theta = np.random.uniform(-np.pi, np.pi)
            self.agent.state = NetworkExploreState(NET_EXPLORE_NAME, (100, 255, 0), self.agent)
        # *potentially* change group membership???

    def move(self, neighbors, predators):
        dx = self.agent.site.pos - self.agent.pos
        repulsion = np.zeros_like(self.agent.pos)
        for neighbor in neighbors:
            c = self.agent.sim.get_agent_pos(neighbor) - self.agent.pos
            scaling_factor = c @ c
            if scaling_factor == 0:
                scaling_factor = 1
            repulsion += c / scaling_factor
        self.agent.pos += (dx - repulsion) * DT
        super().move(neighbors, predators)

class GoToHubState(State): # move towards their hub
    def __init__(self, name, color, agent):
        super().__init__(name, color, agent)

    def update(self, neighbors, sites, predators):
        super().update(neighbors, sites, predators)
        if self.agent.at_hub():
            self.agent.state = NetworkRestState(NET_REST_NAME, (0, 255, 255), self.agent)
            return
        
    def move(self, neighbors, predators):
        # self.agent.repulse_move(neighbors, predators, attr_factor=0.0)
        self.agent.random_walk(potency=1.0)
        dx = self.agent.hub.pos - self.agent.pos
        self.agent.pos += (dx * DT)
        super().move(neighbors, predators)
    # 
class GoToSiteState(State):
    def __init__(self, name, color, agent):
        super().__init__(name, color, agent)

    def update(self, neighbors, sites, predators):
        super().update(neighbors, sites, predators)
        # changed so that agents can go to sites alone explore->gotosite->rest
        # if not neighbors: 
        #     self.agent.state = NetworkExploreState(NET_EXPLORE_NAME, (100, 255, 0), self.agent)
        #     return
        if self.agent.at_site(self.agent.site):
            self.agent.state = NetworkRestState(NET_REST_NAME, (0, 255, 255), self.agent)
            return
        
    def move(self, neighbors, predators):
        # self.agent.repulse_move(neighbors, predators, attr_factor=0.0)
        self.agent.random_walk(potency=1.0)
        
        dx = self.agent.site.pos - self.agent.pos

        self.agent.pos += (dx * DT)
        super().move(neighbors, predators)

class FollowState(State):
    def __init__(self, name, color, agent):
        super().__init__(name, color, agent)

    def update(self, neighbors, sites, predators):
        super().update(neighbors, sites, predators)
        
        if sites:
            if np.random.random() > 0.5:
                viable_sites = list(filter(lambda i: i not in self.agent.last_known_sites, sites))
                if len(viable_sites) > 0:
                    self.agent.following = None
                    self.agent.site = viable_sites[np.random.randint(0, len(viable_sites))]
                    self.agent.add_site(self.agent.site)
                    self.agent.state = GoToSiteState(NET_GOTOSITE_NAME, (0, 0, 255), self.agent)
                    return

        if not neighbors:
            self.agent.following = None
            self.agent.state = NetworkExploreState(NET_EXPLORE_NAME, (100, 255, 0), self.agent) # TODO: change to explore state
            return
        
        if self.agent.at_site(self.agent.sim.get_agent_site(self.agent.following)):
                self.agent.site = self.agent.sim.get_agent_site(self.agent.following)
                self.agent.add_site(self.agent.site)
                self.agent.state = NetworkRestState(NET_REST_NAME, (0, 255, 255), self.agent)
                return
        if not isinstance(self.agent.sim.agents[self.agent.following].state, GoToSiteState):
            self.agent.state = NetworkFlockState(NET_FLOCK_NAME, (0, 255, 0), self.agent)
    
    def move(self, neighbors, predators):
        dx = self.agent.sim.get_agent_pos(self.agent.following) - self.agent.pos

        # to prevent colliding
        repulsion = np.zeros_like(self.agent.pos)
        for neighbor in neighbors:
            c = self.agent.sim.get_agent_pos(neighbor) - self.agent.pos
            scaling_factor = c @ c
            if scaling_factor == 0:
                scaling_factor = 1
            repulsion += c / scaling_factor

        self.agent.pos += ((dx - repulsion) * DT)
        super().move(neighbors, predators)


"""
These states were used in the preliminary stages of developing the simulation. These can be safely ignored or deleted.
The only state you may want to keep is FleeingState, but since predators aren't implemented in the group-based simulation,
you can ignore it for now.
"""
### PROTOTYPE STATES ###
class RestState(State):
    def __init__(self, agent):
        super().__init__(REST_NAME, REST_COLOR, agent)
        agent.speed = 0.0

    def update(self, neighbors, sites, predators):
        super().update(neighbors, sites, predators)
        self.agent.hunger += 1

        if predators:
            self.agent.state = FleeingState(self.agent)
            # we won't include the site here to reflect having a negative experience
            return
        if self.agent.site.resource_count <= 0 or self.agent.hunger >= MAX_HUNGER:
            self.agent.last_known_site = self.agent.site
            if neighbors:
                if len(neighbors) > AGENT_NEIGHBOR_THRESHOLD:
                    self.agent.state = HighDensityExplore(self.agent)
            else:
                self.agent.state = LowDensityExplore(self.agent)
            return
        else:
            self.agent.site.resource_count -= 1

        # calculate avg neighbor speed
        avg_speed = 0
        for neighbor in neighbors:
            avg_speed += self.agent.sim.get_agent_speed(neighbor)
        if neighbors:
            avg_speed = float(avg_speed / len(neighbors))
        if avg_speed > MAX_SPEED / 2:
            self.agent.state = self.agent.state = FleeingState(self.agent) # later when fleeing gets implemented

    def move(self, neighbors, predators):
        pass

# BASE EXPLORE STATE
class ExploreState(State): # maybe consider two different
    def __init__(self, agent):
        super().__init__(EXPLORE_NAME, EXPLORE_COLOR, agent)
        agent.site = None
        agent.speed = np.random.uniform(1.0, MAX_SPEED)

    def update(self, neighbors, sites, predators):
        super().update(neighbors, sites, predators)
        if self.agent.hunger > 0:
            self.agent.hunger -= 1
        if sites and self.agent.site == None:
            self.agent.site = sites[np.random.randint(0, len(sites))]

        if predators:
            self.agent.state = FleeingState(self.agent)
        # else probabilistically transition to RestState based on hunger
        elif self.agent.site != None:
            if math.dist(self.agent.site.pos, self.agent.pos) <= self.agent.site.radius:
                # if np.random.default_rng().exponential(scale=MAX_HUNGER/4) < self.agent.hunger:
                self.agent.state = RestState(self.agent)

    def move(self, neighbors, predators):
        if neighbors:
            # repulsion factor has to be pumped up super big in order to actually affect movement, and even then, it doesn't do it that well...
            # attraction still is too powerful
            # repulsion just affects how far away the agents try to stay away from each other
            self.agent.move(neighbors, predators) 
        else:
            self.agent.random_walk()
        
        if self.agent.site:
            self.agent.pos += (self.agent.site.pos - self.agent.pos) * DT
        super().move(neighbors=None, predators=None)

class LowDensityExplore(State):
    def __init__(self, agent):
        super().__init__(LOW_DENSE_NAME, EXPLORE_COLOR, agent)
        self.agent.site = None
        self.agent.speed = agent.speed = np.random.uniform(1.0, MAX_SPEED)

    def update(self, neighbors, sites, predators):
        super().update(neighbors, sites, predators)
        if self.agent.hunger > 0:
            self.agent.hunger -= 1
        if sites and self.agent.site == None:
            self.agent.site = sites[np.random.randint(0, len(sites))]
        
        # transition to Flee
        if predators:
            self.agent.state = FleeingState(self.agent)

        # transition to Rest
        elif self.agent.site != None:
            if math.dist(self.agent.site.pos, self.agent.pos) <= self.agent.site.radius:
                # if np.random.default_rng().exponential(scale=MAX_HUNGER/4) < self.agent.hunger:
                self.agent.state = RestState(self.agent)

        # transition to High Density
        elif neighbors:
            if len(neighbors) > AGENT_NEIGHBOR_THRESHOLD:
                self.agent.state = HighDensityExplore(self.agent)

    def move(self, neighbors, predators):
        if neighbors:
            self.agent.move(neighbors, predators, attr_factor=3.0)
        else:
            self.agent.random_walk(2.0)
        # prioritize moving toward a known site
        if self.agent.site == None:
            if self.agent.last_known_sites:
                self.agent.pos += (self.agent.last_known_sites[0].pos - self.agent.pos) * DT * 3.0
        super().move(neighbors, predators)

class HighDensityExplore(State):
    def __init__(self, agent):
        super().__init__(HIGH_DENSE_NAME, EXPLORE_COLOR, agent)
        self.agent.site = None
        self.agent.speed = agent.speed = np.random.uniform(1.0, MAX_SPEED)

    def update(self, neighbors, sites, predators):
        super().update(neighbors, sites, predators)
        if self.agent.hunger > 0:
            self.agent.hunger -= 1
        if sites and self.agent.site == None:
            self.agent.site = sites[np.random.randint(0, len(sites))]
        
        # transition to Flee
        if predators:
            self.agent.state = FleeingState(self.agent)

        # transition to Rest
        elif self.agent.site != None:
            if math.dist(self.agent.site.pos, self.agent.pos) <= self.agent.site.radius:
                # if np.random.default_rng().exponential(scale=MAX_HUNGER/4) < self.agent.hunger:
                self.agent.state = RestState(self.agent)

        # transition to Low Density once len(neighbors) is below like... half the constant threshold???
        elif neighbors:
            if len(neighbors) / AGENT_NEIGHBOR_THRESHOLD:
                self.agent.state = LowDensityExplore(self.agent)

    def move(self, neighbors, predators):
        # prioritize repulsion from neighbors
        if neighbors:
            self.agent.move(neighbors, predators, attr_factor=0.5, rpls_factor=25.0)
            self.agent.random_walk(3.0)
        else:
            self.agent.random_walk()
        super().move(neighbors, predators)

class FleeingState(State):
    def __init__(self, agent):
        super().__init__(FLEE_NAME, FLEE_COLOR, agent)
        self.agent.speed = MAX_SPEED

    def update(self, neighbors, sites, predators):
        super().update(neighbors, sites, predators)
        if self.agent.hunger > 0:
            self.agent.hunger -= 1
        if not predators:
            if sites:
                self.agent.site = sites[np.random.randint(0, len(sites))]
                if math.dist(self.agent.site.pos, self.agent.pos) <= self.agent.site.radius:
                    self.agent.state = RestState(self.agent)
            else:
                self.agent.state = ExploreState(self.agent)

    def move(self, neighbors, predators):
        direction = self.get_heading(neighbors, predators)

        x, y = direction

        desired_heading = np.arctan2(y, x)
        difference_in_heading = (((desired_heading - self.agent.theta) + np.pi) % (2*np.pi)) - np.pi

        angular_velocity = 0.5 * (difference_in_heading) # k = 0.5, TODO: make k a constant
        self.agent.pos = self.agent.pos + self.agent.heading() * self.agent.speed * DT

        self.agent.theta = self.agent.theta + (angular_velocity * DT)
        # self.agent.theta = (((self.agent.theta + (angular_velocity * DT)) + np.pi) % (2*np.pi)) + np.pi
        super().move(neighbors=None, predators=None)

    def get_heading(self, neighbors, predators): # TODO: alter movement so they run away from predators faster
        attraction = np.zeros(2)
        orientation = self.agent.heading()
        repulsion = np.zeros(2)
        
        for predator in predators:
            orientation += predator.heading()
            repulsion += 2 * (predator.pos - self.agent.pos)

        for neighbor in neighbors:
            attraction += (self.agent.pos - self.agent.sim.get_agent_pos(neighbor))
            orientation += self.agent.sim.get_agent_heading(neighbor)
            c = self.agent.sim.get_agent_pos(neighbor) - self.agent.pos
            scaling_factor = c @ c
            if scaling_factor == 0:
                repulsion += c
            else:
                repulsion += c / scaling_factor # essentially normalizing it???

        if neighbors:
            attraction = attraction / np.linalg.norm(attraction)
            orientation = orientation / np.linalg.norm(orientation)

        attraction *= 2 * self.agent.attr_factor
        repulsion *= self.agent.rpls_factor
        attraction = attraction - repulsion + orientation
        return attraction
