REST_COLOR = (255, 255, 255)
EXPLORE_COLOR = (0, 0, 0)
FLEE_COLOR = (255, 0, 0)
EXPLORE_NAME = "EXPLORE"
REST_NAME = "REST"
FLEE_NAME = "FLEE"
DT = 0.01
MAX_HUNGER = 100
SPEED_THRESHOLD = 5.0

PADDING = 1

import numpy as np
import math

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
        from simulation import WORLD_SIZE
        if self.agent.pos[0] <= PADDING:
            self.agent.pos[0] = self.agent.pos[0] + (self.agent.speed * DT)
            self.agent.theta = 0.0

        if self.agent.pos[1] <= PADDING:
            self.agent.pos[1] = self.agent.pos[1] + (self.agent.speed * DT)
            self.agent.theta = np.pi/2

        if self.agent.pos[0] >= WORLD_SIZE - PADDING:
            self.agent.pos[0] = self.agent.pos[0] - (self.agent.speed * DT)
            self.agent.theta = np.pi

        if self.agent.pos[1] >= WORLD_SIZE - PADDING:
            self.agent.pos[1] = self.agent.pos[1] - (self.agent.speed * DT)
            self.agent.theta = 3*np.pi/2

class RestState(State):
    def __init__(self, agent):
        super().__init__(REST_NAME, REST_COLOR, agent)
        agent.speed = 0.0

    def update(self, neighbors, sites, predators):
        super().update(neighbors, sites, predators)
        self.agent.hunger += 1
        if predators:
            self.agent.state = FleeingState(self.agent)
            return
        if self.agent.site.resource_count <= 0:
            self.agent.state = ExploreState(self.agent)
            return
        elif self.agent.hunger >= MAX_HUNGER:
            self.agent.state = ExploreState(self.agent)
            return
        else:
            self.agent.site.resource_count -= 1

        # calculate avg neighbor speed
        avg_speed = 0
        for neighbor in neighbors:
            avg_speed += self.agent.sim.get_agent_speed(neighbor)
        if neighbors:
            avg_speed = float(avg_speed / len(neighbors))
        if avg_speed > SPEED_THRESHOLD:
            self.agent.state = self.agent.state = FleeingState(self.agent) # later when fleeing gets implemented

    def move(self, neighbors, predators):
        pass

class ExploreState(State): # maybe consider two different
    def __init__(self, agent):
        super().__init__(EXPLORE_NAME, EXPLORE_COLOR, agent)
        agent.site = None
        agent.speed = np.random.uniform(1.0, SPEED_THRESHOLD)

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
        # calculate repulsion + attraction + orientation towards neighbors
        direction = self.get_heading(neighbors)

        x, y = direction

        desired_heading = np.arctan2(y, x)
        difference_in_heading = (((desired_heading - self.agent.theta) + np.pi) % (2*np.pi)) - np.pi

        angular_velocity = 0.5 * (difference_in_heading) # k = 0.5, TODO: make k a constant
        self.agent.pos = self.agent.pos + self.agent.heading() * self.agent.speed * DT

        self.agent.theta = self.agent.theta + (angular_velocity * DT)
        # self.agent.theta = (((self.agent.theta + (angular_velocity * DT)) + np.pi) % (2*np.pi)) + np.pi
        super().move(neighbors=None, predators=None)

    def get_heading(self, neighbors):
        attraction = np.zeros(2)
        repulsion = np.zeros(2)
        orientation = self.agent.heading()
        new_speed = self.agent.speed

        for neighbor in neighbors:
            attraction += (self.agent.pos - self.agent.sim.get_agent_pos(neighbor))
            orientation += self.agent.sim.get_agent_heading(neighbor)
            new_speed += self.agent.sim.get_agent_speed(neighbor)
            c = self.agent.sim.get_agent_pos(neighbor) - self.agent.pos
            scaling_factor = c @ c
            if scaling_factor == 0:
                repulsion += c
            else:
                repulsion += c / scaling_factor
                    
        if self.agent.site != None:
            attraction += self.agent.pos - self.agent.site.pos # multiply by a constant to weight towards being more attracted to site?

        if neighbors:
            attraction = attraction / np.linalg.norm(attraction)
            orientation = orientation / np.linalg.norm(orientation) # add zero checks in case?
            new_speed = new_speed / len(neighbors)
                
        attraction *= self.agent.attr_factor
        repulsion *= self.agent.repulse_factor
        attraction = attraction - repulsion + orientation
        self.agent.speed = new_speed
        return attraction

class FleeingState(State):
    def __init__(self, agent):
        super().__init__(FLEE_NAME, FLEE_COLOR, agent)
        self.agent.speed = 5.0

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
                repulsion += c / scaling_factor

        if neighbors:
            attraction = attraction / np.linalg.norm(attraction)
            orientation = orientation / np.linalg.norm(orientation)

        attraction *= 2 * self.agent.attr_factor
        repulsion *= self.agent.repulse_factor
        attraction = attraction - repulsion + orientation
        return attraction
