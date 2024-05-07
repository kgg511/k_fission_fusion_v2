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
            self.draw_shape(agent, agent_color)

        for predator in self.simulation.predators:
            if self.should_scale:
                pygame.draw.circle(self.screen, "red", predator.pos*self.scale, 5)
            else:
                pygame.draw.circle(self.screen, "red", predator.pos, 5)

    def draw_shape(self, agent, color):
        """Update the shape of the visual representation with the given color."""
        new_pos = agent.pos*self.scale if self.should_scale else agent.pos
        stateName = agent.state.name[len("NETWORK_"):] if agent.state.name.startswith("NETWORK_") else agent.state.name
        if stateName == "REST": # replace with a state
            pygame.draw.circle(self.screen, color, new_pos, 5)
        elif stateName == "EXP": # Triangle
            triangle_vertices = [
            (new_pos[0], new_pos[1] - 5),  # Top vertex
            (new_pos[0] - 5, new_pos[1] + 5),  # Bottom-left vertex
            (new_pos[0] + 5, new_pos[1] + 5)   # Bottom-right vertex
            ]
            pygame.draw.polygon(self.screen, color, triangle_vertices)

        elif stateName == "FLOCK": # diamond
            diamond_vertices = [
            (new_pos[0], new_pos[1] - 5),  # Top vertex
            (new_pos[0] - 5, new_pos[1]),  # Left vertex
            (new_pos[0], new_pos[1] + 5),  # Bottom vertex
            (new_pos[0] + 5, new_pos[1])   # Right vertex
                ]
            pygame.draw.polygon(self.screen, color, diamond_vertices)
        
        elif stateName == "HUB": # star
            star_vertices = [
            (new_pos[0], new_pos[1] - 5),              # Top vertex
            (new_pos[0] - 2, new_pos[1] + 1),          # Top-left vertex
            (new_pos[0] - 5, new_pos[1] + 3),          # Left vertex
            (new_pos[0] - 2, new_pos[1] + 5),          # Bottom-left vertex
            (new_pos[0], new_pos[1] + 7),              # Bottom vertex
            (new_pos[0] + 2, new_pos[1] + 5),          # Bottom-right vertex
            (new_pos[0] + 5, new_pos[1] + 3),          # Right vertex
            (new_pos[0] + 2, new_pos[1] + 1)           # Top-right vertex
        ]
            pygame.draw.polygon(self.screen, color, star_vertices)
            
        elif stateName == "FOLLOW":
            hexagon_vertices = [
            (new_pos[0] - 4, new_pos[1] - 5),  # Top-left vertex
            (new_pos[0] - 4, new_pos[1] + 5),  # Bottom-left vertex
            (new_pos[0], new_pos[1] + 9),      # Bottom vertex
            (new_pos[0] + 4, new_pos[1] + 5),  # Bottom-right vertex
            (new_pos[0] + 4, new_pos[1] - 5),  # Top-right vertex
            (new_pos[0], new_pos[1] - 9)       # Top vertex
            ]
            pygame.draw.polygon(self.screen, color, hexagon_vertices)
            
        elif stateName == "LEAD":
            square_rect = pygame.Rect(new_pos[0] - 5, new_pos[1] - 5, 10, 10)  # Create a rectangle for the square
            pygame.draw.rect(self.screen, color, square_rect)
            
# Run Simulation
if USE_BT:
    sim = BT_Simulation()
else:
    sim = FSM_Simulation()
display = PygameDisplay(sim)
display.run()