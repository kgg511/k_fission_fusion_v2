import pygame
from World.config import AGENT_SENSING_RADIUS, WORLD_SIZE

class AgentSprite(pygame.sprite.Sprite):
    def __init__(self, agent, agent_color):
        super().__init__()
        self.agent = agent
        # create surface to draw, set transparent color
        self.surface = pygame.Surface((10, 10))
        self.surface.set_colorkey((0, 0, 0))
        # set self.rect then inflate() by SENSING_RADIUS
        self.rect = self.surface.get_rect()
        self.rect = self.rect.inflate(AGENT_SENSING_RADIUS, AGENT_SENSING_RADIUS)
        # draw itself; NOTE: if displaying incorrectly, change center
        self.circle = pygame.draw.circle(self.surface, agent_color, (0, 0), 5)
        # get from world space to display space
        x,y = self.agent.pos
        x += WORLD_SIZE
        y = WORLD_SIZE - y
        self.rect.center = (x, y)
