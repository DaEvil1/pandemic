#MultiNodes.py
import Node
import math
import random
import pyglet
import time
import numpy as np
from GraphResources import *

class MultiNodes:

    def __init__(self, win):
        self.batch = pyglet.graphics.Batch()
        self.coll_batch = pyglet.graphics.Batch()
        self.active_collisions = True
        self.collisions = []
        self.draw_collisions = False
        self.list_overlaps = False
        self.nodes = []
        self.done = False
        self.overlaps = []
        self.frame = 0
        self.data = {"resolution" : 12, "win" : win}
    
    def AddNode(self, speed, color, radius, pos):
        new_node = Node.Node(radius, color)
        new_node.data["pos"] = pos
        new_node.data["speed"] = (speed)
        new_node.data["radius"] = radius
        self.nodes.append(new_node)

    def _factor(self, n):
        if n < 0:
            return -1
        return 1

    def _boundary(self):
        w, h = self.data["win"]
        nodes = self.nodes
        for i in nodes:
            radius = i.data["radius"]
            xs, ys = i.data["speed"]
            if i.data["pos"][0] < 0 + radius:
                xs = -xs
                i.data["pos"] = (0 + radius, i.data["pos"][1])
                i.data["speed"] = (xs, ys)
            if i.data["pos"][0] > w - radius:
                xs = -xs
                i.data["pos"] = (w - radius, i.data["pos"][1])
                i.data["speed"] = (xs, ys)
            if i.data["pos"][1] < 0 + radius:
                ys = -ys
                i.data["pos"] = (i.data["pos"][0], 0 + radius)
                i.data["speed"] = (xs, ys)
            if i.data["pos"][1] > h - radius:
                ys = -ys
                i.data["pos"] = (i.data["pos"][0], h - radius)
                i.data["speed"] = (xs, ys)

    def _handleoverlaps(self):
        nodes = self.nodes
        new_overlaps = []
        for i in self.overlaps:
            r1 = nodes[i[0]].data["radius"]
            r2 = nodes[i[1]].data["radius"]
            n_1 = nodes[i[0]]
            n_2 = nodes[i[1]]
            dist_x = abs(n_1.data["pos"][0] - n_2.data["pos"][0])
            dist_y = abs(n_1.data["pos"][1] - n_2.data["pos"][1])
            v_dist = (dist_x**2 + dist_y**2)**0.5
            if v_dist < r1+r2:
                new_overlaps.append(i)
        self.overlaps = new_overlaps

    def _list_overlaps(self):
        nodes = self.nodes
        for i in range(len(nodes)):
            i_radius = nodes[i].data["radius"]
            for j in range(i + 1, len(nodes)):
                j_radius = nodes[j].data["radius"]
                dist_x = abs(nodes[i].data["pos"][0] - nodes[j].data["pos"][0])
                dist_y = abs(nodes[i].data["pos"][1] - nodes[j].data["pos"][1])
                if dist_x < i_radius+j_radius and dist_y < i_radius+j_radius:
                    v_dist = (dist_x**2 + dist_y**2)**0.5
                    if v_dist < i_radius+j_radius:
                        self.overlaps_listed.append((i, j))
    
    def _collision(self):
        nodes = self.nodes
        collisions = []
        for i in range(len(nodes)):
            i_radius = nodes[i].data["radius"]
            for j in range(i + 1, len(nodes)):
                j_radius = nodes[j].data["radius"]
                dist_x = abs(nodes[i].data["pos"][0] - nodes[j].data["pos"][0])
                dist_y = abs(nodes[i].data["pos"][1] - nodes[j].data["pos"][1])
                if dist_x < i_radius+j_radius and dist_y < i_radius+j_radius:
                    v_dist = (dist_x**2 + dist_y**2)**0.5
                    if v_dist < i_radius+j_radius:
                            if i not in collisions and (i, j) not in self.overlaps:
                                if (j, i) not in collisions and (j, i) not in self.overlaps:
                                    collisions.append((i, j))
                                    self.overlaps.append((i, j))
                        #dx = (i.data["pos"][0] + j.data["pos"][0])/2
                        #dy = (i.data["pos"][1] + j.data["pos"][1])/2
                        #self.collisions.append((dx, dy))
        for i in collisions:
            nodes = self.nodes
            o1 = nodes[i[0]]
            o2 = nodes[i[1]]
            v1, r1 = np.array((o1.data["speed"])), np.array((o1.data["pos"]))
            v2, r2 = np.array((o2.data["speed"])), np.array((o2.data["pos"]))
            d = np.linalg.norm(r1 - r2)**2
            u1 = v1 - np.dot(v1-v2, r1-r2) / d * (r1 - r2)
            u2 = v2 - np.dot(v2-v1, r2-r1) / d * (r2 - r1)
            nodes[i[0]].data["speed"] = (u1[0], u1[1])
            nodes[i[1]].data["speed"] = (u2[0], u2[1])
            self.collisions.append(o1.data["pos"])

    def _draw_collisions(self):
        for i in self.collisions:
            print("coll")
            make_circle(i[0], i[1], 3, [255, 255, 0], 4, self.coll_batch)

    def _drawbackgr(self):
        w, h = self.data["win"]
        sqr = (0, 0, w, 0, w, h, 0, h)
        col = tuple([0 for i in range(12)])
        backgr = pyglet.graphics.vertex_list(4, ('v2f', sqr ), ('c3B', col))
        backgr.draw(pyglet.gl.GL_POLYGON)

    def newframe(self):
        nodes = self.nodes
        data = self.data
        self.overlaps_listed = []
        #self._drawbackgr()
        self._boundary()
        if self.active_collisions:
            self._handleoverlaps()
            self._collision()
        if self.draw_collisions:
            self._draw_collisions()
            self.coll_batch.draw()
        for i in nodes:
            i.newframe(data["resolution"], self.batch)
        self.batch.draw()
        self.frame += 1
        self.batch = pyglet.graphics.Batch()
        if self.list_overlaps:
            self._list_overlaps()
            return self.overlaps_listed
    
#    def _last_frame(self):


    def on_mouse_press(self, x, y, button, modifiers):
        if button == 1:
            self.done = True
            #self._last_frame()