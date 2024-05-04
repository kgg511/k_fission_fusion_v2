import pygame
from World.config import AGENT_SENSING_RADIUS, WORLD_SIZE
import math

BLUE= (0, 0, 255)

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

#     def update_shape(self, new_shape, color):
#         """Update the shape of the visual representation with the given color."""

#         if new_shape == "circle":
#             self.surface = pygame.Surface((10, 10), pygame.SRCALPHA)
#             self.surface.set_colorkey((0, 0, 0))

#             self.rect = self.surface.get_rect()
#             self.rect = self.rect.inflate(AGENT_SENSING_RADIUS, AGENT_SENSING_RADIUS)
#             self.circle = pygame.draw.circle(self.surface, color, (self.agent.pos[0], self.agent.pos[1]), 5)
#             self.rect.center = (self.agent.pos[0], self.agent.pos[1])

#         elif new_shape == "triangle":

#             triangle_vertices = [
#     (self.agent.pos[0], self.agent.pos[1] - 5),  # Top vertex
#     (self.agent.pos[0] - 5, self.agent.pos[1] + 5),  # Bottom-left vertex
#     (self.agent.pos[0] + 5, self.agent.pos[1] + 5)   # Bottom-right vertex
# ]
#             self.surface = pygame.Surface((10, 10), pygame.SRCALPHA)
#             self.surface.set_colorkey((0, 0, 0))

#             self.rect = self.surface.get_rect()
#             self.rect = self.rect.inflate(AGENT_SENSING_RADIUS, AGENT_SENSING_RADIUS)
#             self.circle = pygame.draw.polygon(self.surface, color, triangle_vertices)

#             self.rect.center = (self.agent.pos[0], self.agent.pos[1])

            

    
    # def change_shape(self, shape): # initial shape is 
    #     if shape == 'circle':
    #         self.image = pygame.Surface((50, 50), pygame.SRCALPHA)  # Transparent surface for circle
    #         pygame.draw.circle(self.image, BLUE, (25, 25), 25)  # Draw a blue circle
    #     elif shape == 'rectangle':
    #         self.image = pygame.Surface((50, 50))  # Regular rectangle
    #         self.image.fill(RED)
    #     elif shape == 'triangle':
    #         self.image = pygame.Surface((50, 50))  # Triangle
    #         pygame.draw.polygon(self.image, BLUE, [(25, 0), (0, 50), (50, 50)])
    #     elif shape == 'pentagon':
    #         self.image = pygame.Surface((50, 50))  # Pentagon
    #         points = [(25 + 25 * math.cos(2 * math.pi * i / 5), 25 + 25 * math.sin(2 * math.pi * i / 5)) for i in range(5)]
    #         pygame.draw.polygon(self.image, BLUE, points)
    #     elif shape == 'hexagon':
    #         self.image = pygame.Surface((50, 50))  # Hexagon
    #         points = [(25 + 25 * math.cos(2 * math.pi * i / 6), 25 + 25 * math.sin(2 * math.pi * i / 6)) for i in range(6)]
    #         pygame.draw.polygon(self.image, BLUE, points)
    #     elif shape == 'star':
    #         self.image = pygame.Surface((50, 50))  # Star
    #         points = []
    #         for i in range(5):
    #             angle = math.radians(90 + i * 72)
    #             points.append((25 + 25 * math.cos(angle), 25 + 25 * math.sin(angle)))
    #             angle = math.radians(126 + i * 72)
    #             points.append((25 + 12.5 * math.cos(angle), 25 + 12.5 * math.sin(angle)))
    #         pygame.draw.polygon(self.image, BLUE, points)
