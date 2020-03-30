#pandemic_config.py
HEALTHY_NODES = 300
INFECTED_NODES = 1
PERCENTAGE_SOCIAL_DISTANCING = 0
PERCENTAGE_VACCINATED = 0
PERCENTAGE_HYGIENE = 0
TOTAL_NODES = HEALTHY_NODES + INFECTED_NODES

HEALTHY_SPEED = [1, 10]
INFECTED_SPEED = [1, 5]
IMMUNE_SPEED = [0, 0]
DEAD_SPEED = [0, 0]
IN_TREATMENT_SPEED = [0, 0]
SERIOUS_SPEED = [0, 0]
SOCIAL_DISTANCING_SPEED = [0, 1]
QUARANTINED_SPEED = [0, 0]

HEALTHY_COLOR = [0, 255, 255]
INFECTED_COLOR = [255, 220, 0]
SERIOUSLY_INFECTED_COLOR = [255, 128, 0]
IN_TREATMENT_COLOR = [0, 255, 60]
IMMUNE_COLOR = [100, 0, 255]
DEAD_COLOR = [255, 0, 0]
QUARANTINED_COLOR = [122, 122, 122]

HEALTHY_RADIUS = 10
INFECTED_RADIUS = 10
IMMUNE_RADIUS = 10
DEAD_RADIUS = 10
QUARANTINED_RADIUS = 10
NODE_RES = 6

#Per loop
QUARANTINE_CHANCE_PERCENT = 0.05
INFECTION_CHANCE = 0.1
QUARNATINE_INFECTION_RATIO = 0.05
HYGIENE_FACTOR = 3
SERIOUS_LETHALITY_WITHOUT_TREATMENT = 0.0005
SERIOUS_LETHALITY_WITHOUT_TREATMENT_RISK_GROUP = 0.001
LETHALITY = 0.000025
RISK_GROUP_LETHALITY = 0.0005


TIME_TILL_IMMUNE = 20
SERIOUSLY_SICK_CHANCE = 0.001
RISK_GROUP_PORTION = 0.1
SERIOUSLY_SICK_CHANCE_RISK_GROUP = 0.005
TREATMENT_SPOTS = TOTAL_NODES/10
TREATMENT_DAYS = 12

WIN_WIDTH = 1800
WIN_HEIGHT = 900
WIN_FPS = 30

COLLISIONS = False
DRAW_COLLISIONS = False
STATUS_TEXT = True

GRAPH_FILE_NAME = "\\simulations\\simulation_run"
GRAPH_FILE_EXT = ".png"
GRAPH_MARGINS = ((300, 50), (1500, 600))
GRAPH_DIM = (1800, 650)