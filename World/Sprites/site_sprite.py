import pygame
from config import WORLD_SIZE

class SiteSprite(pygame.sprite.Sprite):
    def __init__(self, site):
        self.site = site
        # make surface
        self.surface = pygame.Surface((site.radius*2, site.radius*2))
        self.surface.set_colorkey(0, 0, 0)
        # get rect
        self.rect = self.surface.get_rect()
        # draw stuff
        self.circle = pygame.draw.circle(self.surface, "green", (0, 0), site.radius)
        # put in display space
        x,y = self.site.pos
        x += WORLD_SIZE
        y = WORLD_SIZE - y
        self.rect.center = (x, y)
