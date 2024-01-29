import pygame
import numpy as np
from World.simulation import Simulation
from World.Sprites.agent_sprite import AgentSprite
from World.Sprites.site_sprite import SiteSprite

# subclass of Simulation that relies on pygame collision detection instead to do agent sensing

class PygameSim(Simulation):
    def __init__(self):
        # initialize
        self.agent_sprites = pygame.sprite.Group()
        self.site_sprites = pygame.sprite.Group()
        super().__init__()

        self.build_agent_sprites()
        self.build_site_sprites()

    def build_agent_sprites(self):
        for agent in self.agents:
            agent_sprite = AgentSprite(agent, self.agent_colors[agent.id])
            self.agent_sprites.add(agent_sprite)
    
    def build_site_sprites(self):
        for site in self.sites:
            site_sprite = SiteSprite(site)
            self.site_sprites.add(site_sprite)
    
    # FIXME: not correctly sensing neighbors and sites; never really updates/changes
    # check collisions
    def get_neighbor_ids(self, agent):
        agent_rect = self.agent_sprites.sprites()[agent.id].rect
        neighbors = agent_rect.collidelistall(self.agent_sprites.sprites())
        group_neighbors = []
        for neighbor in neighbors:
            if np.array_equal(self.get_agent_group_id(neighbor), self.get_agent_group_id(agent.id)):
                    group_neighbors.append(neighbor)
        return neighbors, group_neighbors
    
    def get_sites(self, agent):
        agent_rect = self.agent_sprites.sprites()[agent.id].rect
        sites_indices = agent_rect.collidelistall(self.site_sprites.sprites())
        sites = [self.sites[i] for i in sites_indices]
        # TODO: implement checking if site is available; maybe have it checked by agent instead?
        return sites
    