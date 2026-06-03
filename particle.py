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
B_field = vector(0, 0, 4)  
pos_init = vector(0, 0, 0)


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