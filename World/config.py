# WORLD SET UP
NUM_AGENTS = 10 # determines how many agents will be in the simulation
WORLD_SIZE = 30 # determines how large the (square) world will be
NUM_ITERS = 150 # determines how many iterations each simulation trial should be run in run_experiment.py
NUM_SITES = 3 # determines how many sites will be in the world
NUM_PREDS = 0 # determines how many predators will be in the world
SITE_REGEN_TIME = 10 # determines how many iterations it takes until a site completely regenerates resources
SITE_MAX_RESOURCE = 200 # determines the max number of resources a site may have
SITE_MAX_RADIUS = WORLD_SIZE * 0.25 # determines the maximum size of any given site
PADDING = 0.5 # determines how close the agents and predators can get to the world border
DT = 0.01 # used to smooth agent/predator movement between iterations (too high and it's jittery, too low and they barely move)
NUM_GROUPS = 3 # determines the number of groups agents are separated into
MAX_NETWORK_SIZE = (NUM_AGENTS // NUM_GROUPS) + 1 # determines the maximum size of each group
USE_BT = False # toggles between the behavior tree implementation of agents and the finite state machine implementation

"""If you wish to add more groups, please add the RGB hexadecimal value of the color
and add the (group number, color) key-value pair to COLORS """
# hard code some color constants for 3 groups
PINK = "#FF00FF"
CYAN = "#00FFFF"
GREEN = "#B0FF00"
COLORS = {0: PINK, 1: CYAN, 2: GREEN} # a map between group number and group color

# AGENT PROPERTIES
USE_BOID_MOVE = True # toggles between pure Boid-like movement, or graph laplacian diffusion based movement
AGENT_SENSING_RADIUS = 5 # determines how far the agent can "see" around itself, with the agent at the center
MAX_HUNGER = 100 # determines the max amount of hunger satiation an agent can have (i.e. how full it can be)
MAX_SPEED = 5.0 # determines the fastest an agent can go, used in movement
MAX_SITE_MEMORY = 2 # determines how many sites an agents can remember
AGENT_SITE_ATTRACTION = 5 # used to speed up an agent toward going to a site IN BT IMPLEMENTATION ONLY
AGENT_BORED_THRESHOLD = 20 # used as a timer: the number of iterations until an agent quits doing a task (i.e. gets bored)
AGENT_NEIGHBOR_THRESHOLD = NUM_AGENTS//10 # determines how many neighbors there should be to transition; USED IN PROTOTYPE STATES ONLY
# For boids movement
AGENT_ORIENT_RADIUS = AGENT_SENSING_RADIUS // 10 if AGENT_SENSING_RADIUS // 10 > 0 else 2 # determines which neighbors an agent will try to match orientation with; was originally 8
AGENT_REPL_RADIUS = 1 # determines the minimum spacing between each agent
K = 0.5 # used to calculate angular velocity

# PREDATOR PROPERTIES
PREDATOR_SENSING_RADIUS = 5 # determines how far a predator can "see", centered around the predator
HUNTING_MULTIPLIER = 3 # determines how much faster a predator will move when it has a target
PREDATOR_NEIGHBOR_THRESHOLD = 5 # determines how big a group of agents had to be before a predator would give up chasing an agent
