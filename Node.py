#Node.py
import pyglet
import math
from GraphResources import *

class Node:


    def __init__(self, radius, color, resolution):
        self.data = {"radius" : radius, "color" : color, "speed" : (0, 0), "pos" : [0, 0], "resolution" : resolution, 
                     "grid" : None}
        self.newResolution(resolution)
    
    def newResolution(self, resolution):
        self.points = []
        self.color = []
        radius = self.data["radius"]
        color = self.data["color"]
        pi = math.pi
        self.data["resolution"] = resolution
        x, y = 0, 0
        for i in range(resolution):
            angle1 = 2 * pi * i / resolution
            nx1 = x + math.cos(angle1) * radius
            ny1 = y + math.sin(angle1) * radius
            angle2 = 2 * pi * (i + 1) / resolution
            nx2 = x + math.cos(angle2) * radius
            ny2 = y + math.sin(angle2) * radius
            self.points.append(nx1)
            self.points.append(ny1)
            self.points.append(nx2)
            self.points.append(ny2)
            self.points.append(x)
            self.points.append(y)
            for _ in range(3):
                for j in color:
                    self.color.append(j)
    
    def newColor(self, color):
        self.color = []
        for _ in range(self.data["resolution"]):
            for _ in range(3):
                for j in color:
                    self.color.append(j)

    def newframe(self, batch):
        data = self.data
        sp = data["speed"]
        #an = data["angle"]
        x, y = data["pos"]
        #nx = x + sp * math.cos(an)
        #ny = y + sp * math.sin(an)
        nx = x + sp[0]
        ny = y + sp[1]
        data["pos"] = nx, ny
        rel_pos = []
        for i in range(self.data["resolution"]*3):
            rel_pos.append(nx)
            rel_pos.append(ny)
        v_points = [self.points[i] + rel_pos[i] for i in range(len(self.points))]
        make_circle(nx, ny, data["radius"], self.color, v_points, batch)
        #graph.draw(pyglet.gl.GL_POLYGON)

