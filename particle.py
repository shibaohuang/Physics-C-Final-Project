Web VPython 3.2
from vpython import *

particle = ['deuterium', 'tritium']

mass = 1.0
charge = 1.0
B_field = vector(0, 0, 1)  
pos_init = vector(0, 0, 0)
v_init = vector(1, 0, 1)

particle[0] = sphere(pos=pos_init, radius=0.2, color=color.cyan, make_trail=True)
trail = curve(color=color.magenta, radius=0.05)

dt = 0.01
t = 0
while True:
    rate(1000)
    if running:
        F1 = charge1 * cross(v_init1, B_field)
        F2 = charge2 * cross(v_init2, B_field)
        v_init1 = v_init1 + (F1 / mass1) * dt
        v_init2 = v_init2 + (F2 / mass2) * dt
        particle1.pos = particle1.pos + v_init1 * dt
        trail1.append(particle1.pos)
        particle2.pos = particle2.pos + v_init2 * dt
        trail2.append(particle2.pos)
        t = t + dt