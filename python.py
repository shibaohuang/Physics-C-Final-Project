Web VPython 3.2
from vpython import *

#Static Variables
B_field = vector(0, 0, 4)
particles = []
running = False
fusion_distance = 0.4
fusion_energy = 17.6 
collision_count = 0
total_energy = 0

class FusingParticles:
    def __init__(self, name, mass, charge, v_initial, color):
        particles.append(self)
        self.element = name
        self.mass = mass
        self.charge = charge
        self.velocity = v_initial
        self.color = color

tokamak = ring(
    pos=vector(0,0,0),
    axis=vector(0,1,0),
    radius=8,
    thickness=2,
    color=color.gray(0.5)
)

#Different Elements
tritium = FusingParticles(name = "Tritium", mass = 1, charge = 1, v_initial = vector(1, 1, 0.5), color = color.red)
deuterium = FusingParticles(name = "Deuterium", mass = 1, charge = 1, v_initial = vector(1, 1, 0.5), color = color.cyan)

#Making Particles
particle1 = sphere(pos = vector(-3, 0, 0), radius = 0.2, color = particles[0].color)
trail1 = curve(color = particles[0].color, radius = 0.05)
mass1 = particles[0].mass
charge1 = particles[0].charge
v_init1 = -particles[0].velocity

particle2 = sphere(pos = vector(3, 0, 0), radius = 0.2, color = particles[1].color)
trail2 = curve(color = particles[1].color, radius = 0.05)
mass2 = particles[1].mass
charge2 = particles[1].charge
v_init2 = particles[1].velocity

#Graphs
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

#Reset
def reset_sim():
    global v_init1, v_init2, t, running
    # Reset time
    t = 0
    # Reset velocities to current particle's initial velocity
    v_init1 = vector(find_particle(menu1.selected).velocity)
    v_init2 = vector(find_particle(menu2.selected).velocity)
    # Clear trails
    trail1.clear()
    trail2.clear()

#Element Selection Box
def find_particle (name):
    for p in particles:
        if p.element == name:
            return p
    return None

def change_element1 (i):
    global mass1, charge1, v_init1
    p = find_particle(i.selected)
    particle1.color = p.color
    trail1.color = p.color
    mass1 = p.mass
    charge1 = p.charge
    v_init1 = -vector(p.velocity)
    reset_sim()
    
def change_element2 (i):
    global mass2, charge2, v_init2
    p = find_particle(i.selected)
    particle2.color = p.color
    trail2.color = p.color
    mass2 = p.mass
    charge2 = p.charge
    v_init2 = vector(p.velocity)
    reset_sim()

element_names = [p.element for p in particles]
scene.caption = "Particle 1: "
menu(choices = element_names, selected = element_names[0], bind=change_element1)
scene.append_to_caption(" Particle 2: ")
menu(choices = element_names, selected = element_names[1], bind=change_element2)

#Simulation Loop
def toggle_sim(b):
    global running
    running = not running
    if running:
        b.text = "Stop"
    else:
        b.text = "Start"

scene.append_to_caption("\n\n")
button(text = "Start", bind = toggle_sim)

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
        if mag(particle1.pos) > 8:
            particle1.pos = vector(-3,0,0)
        if mag(particle2.pos) > 8:
            particle2.pos = vector(3,0,0)
        if mag(particle1.pos - particle2.pos) < fusion_distance:
            collision_count += 1
            total_energy += fusion_energy
            flash = sphere(pos=(particle1.pos+particle2.pos)/2, radius=0.4, color=color.yellow, emissive=True)
        energy_curve.plot(t,total_energy)
        collision_curve.plot(t,collision_count)
        t = t + dt