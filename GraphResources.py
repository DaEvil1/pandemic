#GraphResources.py
import math
import pyglet

def make_circle(x, y, radius, color, v_points, batch):
    points = []
    pi = math.pi
    col = []
    for i in range(3*v_points):
        angle1 = 2 * pi * i / v_points
        nx1 = x + math.cos(angle1) * radius
        ny1 = y + math.sin(angle1) * radius
        angle2 = 2 * pi * (i + 1) / v_points
        nx2 = x + math.cos(angle2) * radius
        ny2 = y + math.sin(angle2) * radius
        points.append(nx1)
        points.append(ny1)
        points.append(nx2)
        points.append(ny2)
        points.append(x)
        points.append(y)
        points
        for _ in range(3):
            for k in color:
                col.append(k)
    l = int(len(points) / 2)
    points = tuple(points)
    col = tuple(col)
    batch.add(l, pyglet.gl.GL_TRIANGLES, None, ('v2f', points), ('c3B', col))
    #return pyglet.graphics.vertex_list(l, ('v2f', points), ('c3B', col))
