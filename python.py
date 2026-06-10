Web VPython 3.2
from vpython import *

#Static Variables
B_field = vector(0, 0, 2)
particles = []
collisions = []
running = False
fusion_distance = 0.7
fusion_energy = 17.6 
collision_count = 0
total_energy = 0

#Static Tokamak Variables
R = 8        # major radius (big circle)
r_tube = 4   # minor radius (particle orbits inside the tube)
toroidal1_speed = 0.5   # how fast particles go around the big circle
toroidal2_speed = 1
tokamak_center = vector(-15,0,0)

# Starting angles (radians)
phi1 = pi          # toroidal angle particle 1 (position on big circle)
phi2 = 0         # toroidal angle particle 2 (opposite side)
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

tokamak = ring(pos = tokamak_center, axis = vector (0, 1, 0), radius = R, thickness = R-r_tube + 0.5, color = color.cyan, opacity = 0.2)
tokamak = ring(pos = tokamak_center, axis = vector (0, 1, 0), radius = R + 0.5, thickness = R-r_tube + 1, color = color.gray(0.5), opacity = 0.3)

#City
city_windows = []
building_positions = [
    vector(15,0,0),
    vector(18,0,0),
    vector(21,0,0),
    vector(24,0,0),
    vector(27,0,0)
]

building_heights = [4,6,5,8,7]

for i in range(len(building_positions)):

    box(
        pos=building_positions[i],
        size=vector(2,building_heights[i],2),
        color=color.gray(0.4)
    )
    windss = box(
    pos=building_positions[i] + vector(0, 0.5, 1.1), 
    size=vector(1, 1, 0.2), 
    color=color.yellow,  # Changed from black so emissive works
    emissive=True
    )
    city_windows.append(windss)

#Different Elements
tritium = FusingParticles(name = "Tritium", mass = 5.007, charge = 1.6, v_initial = vector(1, 0, 0.2), color = color.red) #mass in 10^-27 and charge in 10^-19
deuterium = FusingParticles(name = "Deuterium", mass = 2.014, charge = 1.6, v_initial = vector(0.2, 0.2, 0), color = color.cyan)

#Making Particles
particle1 = sphere(pos = vector(0, 0, 0), radius = 0.2, color = particles[0].color)
trail1 = curve(color = particles[0].color, radius = 0.05)
mass1 = particles[0].mass
charge1 = particles[0].charge
v_init1 = -particles[0].velocity

particle2 = sphere(pos = vector (0, 0, 0), radius = 0.2, color = particles[1].color)
trail2 = curve(color = particles[1].color, radius = 0.05)
mass2 = particles[1].mass
charge2 = particles[1].charge
v_init2 = particles[1].velocity

def get_pos(phi, theta):
    x = (R + r_tube * cos(theta)) * cos(phi) - 15
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

g3 = graph(
    title="Velocity 1 vs Time",
    xtitle = "Time",
    ytitle="Velocity"
)
velocity1_curve = gcurve(color=color.red)

g4 = graph(
    title="Velocity 2 vs Time",
    xtitle = "Time",
    ytitle="Velocity"
)
velocity2_curve = gcurve(color=color.blue)

#Start/Stop
def toggle_sim(b):
    global running
    running = not running

#Reset
def reset_sim():
    menu1.selected = element_names[0]
    menu2.selected = element_names[1]
    bfield_slider.value = 2
    bfield_text.text = "2.00"
    toroidal1_slider.value = 0.5
    toroidal2_slider.value = 1
    toroidal1_text.text = "0.50"
    toroidal2_text.text = "1.00"
    for c in collisions:
        c.visible = False
    change_sim()

#Change
def change_sim():
    global B_field, running, trail1, trail2, v_init1, v_init2, total_energy, collision_count, toroidal1_speed, toroidal2_speed, phi1, phi2, theta1, theta2, t
    bfield_text.text = "{:.2f}".format(bfield_slider.value)
    toroidal1_text.text = "{:.2f}".format(toroidal1_slider.value)
    toroidal2_text.text = "{:.2f}".format(toroidal2_slider.value)
    
    running = False 
    t = 0

    # Reset particle properties back to defaults
    trail1.clear()
    trail2.clear()
    p1 = find_particle(menu1.selected)
    p2 = find_particle(menu2.selected)
    particle1.color = p1.color
    particle2.color = p2.color
    trail1.color = p1.color
    trail2.color = p2.color
    
    phi1 = pi
    phi2 = 0
    theta1 = 0
    theta2 = 0
    toroidal1_speed = toroidal1_slider.value
    toroidal2_speed = toroidal2_slider.value
    B_field = vector(0, 0, bfield_slider.value)

    # Reset positions
    particle1.pos = get_pos(phi1, theta1)
    particle2.pos = get_pos(phi2, theta2)

    # Clear graphs
    velocity1_curve.delete()
    velocity2_curve.delete()
    energy_curve.delete()
    collision_curve.delete()

    # Reset physics
    v_init1 = -vector(p1.velocity)
    v_init2 = vector(p2.velocity)
    total_energy = 0
    collision_count = 0

#Element Selection Box
def find_particle (name):
    for p in particles:
        if p.element == name:
            return p
    return None

def change_element1 (i):
    global mass1, charge1, v_init1, trail1, trail2
    p = find_particle(i.selected)
    particle1.color = p.color
    trail1.color = p.color
    mass1 = p.mass
    charge1 = p.charge
    change_sim()
    
def change_element2 (i):
    global mass2, charge2, v_init2, trail1, trail2
    p = find_particle(i.selected)
    particle2.color = p.color
    trail2.color = p.color
    mass2 = p.mass
    charge2 = p.charge
    change_sim()

element_names = [p.element for p in particles]
scene.caption = "Press Play to Start Fusion \n\n"
button(text = "Play", bind = toggle_sim)
scene.append_to_caption(" ")
button(text = "Reset", bind = reset_sim)
scene.append_to_caption("\n\n")
scene.append_to_caption("Particle 1: ")
menu1 = menu(choices = element_names, selected = element_names[0], bind=change_element1)
scene.append_to_caption(" Particle 2: ")
menu2 = menu(choices = element_names, selected = element_names[1], bind=change_element2)
scene.append_to_caption("\n")

# Sliders

scene.append_to_caption("\n\nB Field Strength: ")
bfield_text = wtext(text="2.00")
scene.append_to_caption("\n")
bfield_slider = slider(min=0, max=10, value=2, length=300, bind=change_sim)

scene.append_to_caption("\n\nParticle 1 Toroidal Speed: ")
toroidal1_text = wtext(text="0.50")
scene.append_to_caption("\n")
toroidal1_slider = slider(min=0.1, max=3.0, value=0.5, length=300, bind=change_sim)

scene.append_to_caption("\n\nParticle 2 Toroidal Speed: ")
toroidal2_text = wtext(text="1.00")
scene.append_to_caption("\n")
toroidal2_slider = slider(min=0.1, max=3.0, value=1.0, length=300, bind=change_sim)

#Simulation Loop
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
        phi1 += toroidal1_speed * dt
        phi2 += toroidal2_speed * dt
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
            collisions.append(flash)
            powered = min(collision_count, len(city_windows))
            for i in range(powered):
                city_windows[i].color=color.yellow
        energy_curve.plot(t,total_energy)
        collision_curve.plot(t,collision_count)
        velocity1_curve.plot(t, mag(v_init1))
        velocity2_curve.plot(t, mag(v_init2))
        t = t + dt