#Node.py
import pyglet
import math
from GraphResources import *

class Node:


    def __init__(self, radius, color):
        self.data = {"radius" : radius, "color" : color, "speed" : (0, 0), "pos" : [0, 0]}
    
    def newframe(self, v_points, batch):
        data = self.data
        sp = data["speed"]
        #an = data["angle"]
        x, y = data["pos"]
        #nx = x + sp * math.cos(an)
        #ny = y + sp * math.sin(an)
        nx = x + sp[0]
        ny = y + sp[1]
        data["pos"] = nx, ny
        make_circle(nx, ny, data["radius"], data["color"], v_points, batch)
        #graph.draw(pyglet.gl.GL_POLYGON)

