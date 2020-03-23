#PandemiSimulation.py
from PandemicLib import *
from Pandemic_config import WIN_WIDTH, WIN_HEIGHT


def main():
    w, h = WIN_WIDTH, WIN_HEIGHT
    cp = "Pandemic"
    #win = pyglet.window.Window(w, h, visible=False, caption=cp, vsync=0)
    pandemic = Pandemic(w, h, cp)
    pandemic.Start()
    #nodes = MultiNodes.MultiNodes((w, h), N_NODES, NODE_SPEED, NODE_COLOR, NODE_RADIUS)
    # print(win.double_buffer)


if __name__ == "__main__":
    main()