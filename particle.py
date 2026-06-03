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

g1 = graph(
    title="Fusion Energy vs Time",
    xtitle="Time",
    ytitle="Energy (MeV)"
)

energy_curve = gcurve(color=color.yellow)

g2 = graph(
    title="Collision Count vs Time",
    xtitle="Time",
    ytitle="Collisions"
)

collision_curve = gcurve(color=color.green)
while True:
    rate(500)
    F1 = charge * cross(v1,B_field)
    F2 = charge * cross(v2,B_field)
    v1 += (F1/mass)*dt
    v2 += (F2/mass)*dt
    p1.pos += v1*dt
    p2.pos += v2*dt
    if mag(p1.pos) > 8:
        p1.pos = vector(-3,0,0)
    if mag(p2.pos) > 8:
        p2.pos = vector(3,0,0)
    if mag(p1.pos - p2.pos) < fusion_distance:
        collision_count += 1
        total_energy += fusion_energy
        flash = sphere(
            pos=(p1.pos+p2.pos)/2,
            radius=0.4,
            color=color.yellow,
            emissive=True
        )
        p1.pos = vector(-3,0,0)
        p2.pos = vector(3,0,0)
        v1 = vector(1,1,0.5)
        v2 = vector(-1,-1,-0.5)
    energy_curve.plot(t,total_energy)
    collision_curve.plot(t,collision_count)
    t += dt