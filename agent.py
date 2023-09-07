import numpy as np
import states

# note to self: future planning, factors will be floats from 0.5 to 1.0
class Agent:
    def __init__(self, id, pos, speed, theta, hunger, sim, attr_factor=1.0, orient_factor=1.0, repulse_factor=1.0, site=None):
        self.id = id
        self.pos = pos
        self.state = states.ExploreState(self)
        self.speed = speed
        self.theta = theta
        self.hunger = hunger
        self.sim = sim
        self.attr_factor = attr_factor
        self.orient_factor = orient_factor
        self.repulse_factor = repulse_factor
        self.site = site

    def update(self, neighbors, sites, predators):
        # get reading (neighbors, sites)
        # calculate neighbor task densities
        # do state actions
        self.state.update(neighbors, sites, predators)
        self.state.move(neighbors, predators)

    def heading(self):
        return np.array([np.cos(self.theta), np.sin(self.theta)])

    # def get_task_densities(self, neighbors):
    #     # get however many neighbors are doing which task
    #     # densities are num_neighbor_task/len(neighbors)
    #     pass
