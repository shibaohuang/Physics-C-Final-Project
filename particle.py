Web VPython 3.2
from vpython import *

scene.background = color.black

tokamak = ring(
    pos=vector(0,0,0),
    axis=vector(0,1,0),
    radius=8,
    thickness=2,
    color=color.gray(0.5)
)

fusion_distance = 0.4
fusion_energy = 17.6 

collision_count = 0
total_energy = 0

p1 = sphere(
    pos=vector(-3,0,0),
    radius=0.2,
    color=color.cyan,
    make_trail=True
)

p2 = sphere(
    pos=vector(3,0,0),
    radius=0.2,
    color=color.red,
    make_trail=True
)

v1 = vector(1,1,0.5)
v2 = vector(-1,-1,-0.5)

mass = 1.0
charge = 1.0
B_field = vector(0, 0, 1)  
pos_init = vector(0, 0, 0)

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