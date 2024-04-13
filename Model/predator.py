import numpy as np
import math
from Controllers.states import DT, PADDING
from World.config import *

class Predator:
    def __init__(self, pos, theta, sim, speed=1.0, target=None):
        self.pos = pos
        self.theta = theta
        self.sim = sim
        self.speed = speed
        self.target = target
        self.neighbors = []

    def update(self):
        if self.neighbors:
            # get target
            if self.target == None:
                self.target = self.neighbors[np.random.randint(0, len(self.neighbors))]
                self.speed *= HUNTING_MULTIPLIER
            
            # lose target if too many agents are there
            # else:
            #     if len(self.neighbors) > PREDATOR_NEIGHBOR_THRESHOLD:
            #         dx = self.target.pos - self.pos
            #         self.theta = -math.atan2(dx[1], dx[0])
            #         self.target = None

        if math.dist(self.pos, self.target.pos) > PREDATOR_SENSING_RADIUS:
                    self.target = None
                    self.speed = self.speed / HUNTING_MULTIPLIER
        self.move()
        self.neighbors = []

    def move(self):
        from World.simulation import WORLD_SIZE
        if self.target:
            # orient towards target
            dx = self.target.pos - self.pos
            self.theta = math.atan2(dx[1], dx[0])
        else:
            self.theta += np.random.uniform(-np.pi/6, np.pi/6) # FIXME: predator just running in circles???
        self.theta = self.theta % (2*np.pi)
        # move according to orientation
        new_pos = np.array([self.speed * np.cos(self.theta), self.speed * np.sin(self.theta)])
        self.pos = self.pos + new_pos * DT # FIXME: predators jumping around... moving too fast

        # check for world boundaries
        if self.pos[0] <= PADDING:
            self.pos[0] = self.pos[0] + (self.speed * DT)
            self.theta = 0.0

        if self.pos[1] <= PADDING:
            self.pos[1] = self.pos[1] + (self.speed * DT)
            self.theta = np.pi/2

        if self.pos[0] >= WORLD_SIZE - PADDING:
            self.pos[0] = self.pos[0] - (self.speed * DT)
            self.theta = np.pi

        if self.pos[1] >= WORLD_SIZE - PADDING:
            self.pos[1] = self.pos[1] - (self.speed * DT)
            self.theta = 3*np.pi/2

    def heading(self):
        return np.array([np.cos(self.theta), np.sin(self.theta)])
