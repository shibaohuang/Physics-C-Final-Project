Web VPython 3.2
from vpython import *

#Static Variables
B_field = vector(0, 0, 2)
particles = []
collisions = []
running = False
shutdown = False
fusion_distance = 0.7
collision_count = 0
total_energy = 0
radius_orbit = 4
c_light = 3e8          
defect_fraction = 0.00375  
energy_per_building = 35.2 
lawson_threshold = 3e21
lawson_fail_time = 0
shutdown_grace = 2.0
magnet_objects = []
tokamak_objects = []
base_field_strength = 0.25

R = 8        # major radius (big circle)
r_tube = 2   # minor radius (particle orbits inside the tube)
toroidal_speed = 0.5    # how fast particles go around the big circle

# Starting angles (radians)
phi1 = 0          # toroidal angle particle 1 (position on big circle)
phi2 = pi         # toroidal angle particle 2 (opposite side)
theta1 = 0        # poloidal angle particle 1 (position in tube)
theta2 = 0        # poloidal angle particle 2

class FusingParticles:
    def __init__(self, name, mass, charge, v_initial, color):
        particles.append(self)
        self.element = name
        self.mass = mass
        self.charge = charge
        self.velocity = v_initial
        self.color = color

tokamak = ring(pos = vector (0, 0, 0), axis = vector (0, 1, 0), radius = 8, thickness = 4, color = color.gray(0.5), opacity = 0.5)

#Different Elements
tritium = FusingParticles(name = "Tritium", mass = 1, charge = 1, v_initial = vector(1, 1, 0.5), color = color.red)
deuterium = FusingParticles(name = "Deuterium", mass = 1, charge = 1, v_initial = vector(1, 1, 0.5), color = color.cyan)

#Making Particles
particle1 = sphere(pos = vector(-8, 0, 0), radius = 0.2, color = particles[0].color)
trail1 = curve(color = particles[0].color, radius = 0.05)
mass1 = particles[0].mass
charge1 = particles[0].charge
v_init1 = -particles[0].velocity

particle2 = sphere(pos = vector(8, 0, 0), radius = 0.2, color = particles[1].color)
trail2 = curve(color = particles[1].color, radius = 0.05)
mass2 = particles[1].mass
charge2 = particles[1].charge
v_init2 = particles[1].velocity

def get_pos(phi, theta):
    x = (R + r_tube * cos(theta)) * cos(phi)
    y = r_tube * sin(theta)
    z = (R + r_tube * cos(theta)) * sin(phi)
    return vector(x, y, z)

particle1.pos = get_pos(phi1, theta1)
particle2.pos = get_pos(phi2, theta2)

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
        poloidal1_speed = mag(v_init1)
        poloidal2_speed = mag(v_init2)
        phi1 += toroidal_speed * dt
        phi2 += toroidal_speed * dt
        theta1 += poloidal1_speed * dt
        theta2 -= poloidal2_speed * dt
        particle1.pos = get_pos(phi1, theta1)
        particle2.pos = get_pos(phi2, theta2)
        trail1.append(particle1.pos)
        trail2.append(particle2.pos)
        if mag(particle1.pos - particle2.pos) < fusion_distance:
            collision_count += 1
            total_energy += fusion_energy
            flash = sphere(pos=(particle1.pos+particle2.pos)/2, radius=0.4, color=color.yellow, emissive=True)
        energy_curve.plot(t,total_energy)
        collision_curve.plot(t,collision_count)
        t = t + dt