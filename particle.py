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

pos_2 = vector(3, 0, 0)


particle[1] = sphere(pos=pos_2, radius=0.2, color=color.red, make_trail=True)


while t < 30:
    rate(1000) 
    F = charge * cross(v_init, B_field)
    v_init = v_init + (F / mass) * dt
    particle[0].pos = particle[0].pos + v_init * dt
    particle[1].pos = particle[1].pos + v_init * dt
    t = t + dt