import pygame
from World.config import WORLD_SIZE, USE_BT
from World.pygame_sim import PygameSim
from World.simulation import Simulation, BT_Simulation, FSM_Simulation

# Helper: Code from https://stackoverflow.com/questions/214359/converting-hex-color-to-rgb-and-vice-versa by Jeremy Cantrell
def hex_to_rgb(value):
    """Return (red, green, blue) for the color given as #rrggbb."""
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

class PygameDisplay:
    def __init__(self, simulation):
        # pygame display stuff
        pygame.init()
        self.should_scale = False
        if WORLD_SIZE > 500:
            self.screen = pygame.display.set_mode((WORLD_SIZE, WORLD_SIZE))
        else:
            self.screen = pygame.display.set_mode((500, 500))
            self.should_scale = True
            self.scale = 500 / WORLD_SIZE
        self.clock = pygame.time.Clock()
        self.running = True

        # the simulation to display
        self.simulation = simulation

    # updates simulation state
    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    pygame.quit()

            self.screen.fill("white")
            self.simulation.update()
            self.update()
            # print(self.simulation.agents[0].at_site())
            # print(self.simulation.agents[0].neighbors)
            
            pygame.display.flip()
            
            self.clock.tick(60)

    # updates display
    def update(self):
        for site in self.simulation.sites:
            if self.should_scale:
                pygame.draw.circle(self.screen, (0, 255, 0, 100), site.pos*self.scale, site.radius*self.scale)
            else:
                pygame.draw.circle(self.screen, (0, 255, 0, 100), site.pos, site.radius)

        for agent in self.simulation.agents:
            agent_color_name = self.simulation.agent_colors[agent.id]
            agent_color = hex_to_rgb(agent_color_name)
            if self.should_scale:
                pygame.draw.circle(self.screen, agent_color, agent.pos*self.scale, 5)
            else:
                pygame.draw.circle(self.screen, agent_color, agent.pos, 5)
             
        for predator in self.simulation.predators:
            pygame.draw.circle(self.screen, "red", predator.pos, 5)


# Run Simulation
if USE_BT:
    sim = BT_Simulation()
else:
    sim = FSM_Simulation()
display = PygameDisplay(sim)
display.run()