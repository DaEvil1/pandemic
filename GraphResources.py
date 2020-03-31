#GraphResources.py
import math
import pyglet

def make_circle(x, y, radius, color, points, batch):
    l = int(len(points) / 2)
    batch.add(l, pyglet.gl.GL_TRIANGLES, None, ('v2f', points), ('c3B', color))
    #return pyglet.graphics.vertex_list(l, ('v2f', points), ('c3B', col))
