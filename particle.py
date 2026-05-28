Web VPython 3.2

from vpython import *

mass = 1.0
charge = 1.0
B_field = vector(0, 0, 1)  
pos_init = vector(0, 0, 0)
v_init = vector(1, 0, 1)

particle = sphere(pos=pos_init, radius=0.2, color=color.cyan, make_trail=True)
trail = curve(color=color.magenta, radius=0.05)

dt = 0.01
t = 0

while t < 10:
    rate(100) 
    F = charge * cross(v_init, B_field)
    v_init = v_init + (F / mass) * dt
    particle.pos = particle.pos + v_init * dt
    t = t + dt