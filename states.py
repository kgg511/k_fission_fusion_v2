REST_COLOR = (255, 255, 255)
EXPLORE_COLOR = (0, 0, 0)
FLEE_COLOR = (255, 0, 0)
EXPLORE_NAME = "EXPLORE"
LOW_DENSE_NAME = "LOW_DENSE_EXPLORE"
HIGH_DENSE_NAME = "HIGH_DENSE_EXPLORE"
REST_NAME = "REST"
FLEE_NAME = "FLEE"

import numpy as np
import math
from config import *

class State:
    def __init__(self, name, color, agent):
        self.name = name
        self.color = color
        self.agent = agent

    def update(self, neighbors, sites, predators):
        # leave as abstract method
        # transition to the state with the highest concentration of agents also performing the task
        # UNLESS it goes over the threshold
        self.agent.sim.prev_state.update({self.agent.id: [self.agent.pos, self.agent.speed, self.agent.heading()]})

    def move(self, neighbors, predators):
        if math.isclose(self.agent.pos[0], PADDING): # check if these conditions are ever being satisfied with agents at the various positions
            self.agent.pos[0] = self.agent.pos[0] + self.agent.speed

        if math.isclose(self.agent.pos[1], PADDING):
            self.agent.pos[1] = self.agent.pos[1] + self.agent.speed

        if math.isclose(self.agent.pos[0], WORLD_SIZE - PADDING):
            self.agent.pos[0] = self.agent.pos[0] - self.agent.speed

        if math.isclose(self.agent.pos[1], WORLD_SIZE - PADDING):
            self.agent.pos[1] = self.agent.pos[1] - self.agent.speed

class RestState(State):
    def __init__(self, agent):
        super().__init__(REST_NAME, REST_COLOR, agent)
        agent.speed = 0.0

    def update(self, neighbors, sites, predators):
        super().update(neighbors, sites, predators)
        self.agent.hunger += 1
        if predators:
            self.agent.state = FleeingState(self.agent)
            # we won't include the pos here to reflect having a negative experience
            return
        if self.agent.site.resource_count <= 0 or self.agent.hunger >= MAX_HUNGER:
            self.agent.last_known_site_pos = self.agent.site.pos
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

# BASE EXPLORE STATE; TODO: split into low-density and high-density explore states
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
        if hasattr(self.agent.last_known_site_pos, 'shape'):
            self.agent.pos += (self.agent.last_known_site_pos - self.agent.pos) * DT * 3.0
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

