import pygame
from simulation import Simulation

# subclass of Simulation that relies on pygame collision detection instead to do neighbor calculations

class PygameSim(Simulation):
    # TODO: change init to use sub-class specific build tools
    def __init__(self):
        super().__init__()

    # TODO: override build methods to use sprites and sprite groups
    def build_agents(self):
        super().build_agents()
        for agent in self.agents:
            agent_sprite = pygame.sprite.Sprite() # not correct implementation; need to make sprite subclasses
        return
    
    def build_sites(self):
        return super().build_sites()
    
    def build_predators(self):
        return super().build_predators()
    
    # TODO: override detection methods to use pygame collisions
    def get_neighbor_ids(self, agent):
        return super().get_neighbor_ids(agent)
    
    def get_sites(self, agent):
        return super().get_sites(agent)
    
    def get_predators(self, agent):
        return super().get_predators(agent)
    