Web VPython 3.2
from vpython import *

# Static Variables
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

# FIXED: these were missing in original, caused NameError on draw calls
tokamak_center = vector(0, 0, 0)
num_magnets = 8

# FIXED: fusion_energy was referenced but never defined
# Using simplified E = defect_fraction * (m1+m2) * c^2 for D-T reaction
# Hardcoded approximate value in MeV for now
fusion_energy = 17.6   # MeV, standard D-T fusion yield

R = 8        # major radius
r_tube = 2   # minor radius
toroidal_speed = 0.5

phi1 = 0
phi2 = pi
theta1 = 0
theta2 = 0

class FusingParticles:
    def __init__(self, name, mass, charge, v_initial, color):
        particles.append(self)
        self.element = name
        self.mass = mass
        self.charge = charge
        self.velocity = v_initial
        self.color = color

def draw_tokamak():
    global tokamak_objects
    for obj in tokamak_objects:
        obj.visible = False
    tokamak_objects = []
    inner = ring(pos=tokamak_center, axis=vector(0,1,0), radius=R,
                 thickness=r_tube, color=color.cyan, opacity=0.2)
    outer = ring(pos=tokamak_center, axis=vector(0,1,0), radius=R,
                 thickness=r_tube+0.5, color=color.gray(0.5), opacity=0.3)
    tokamak_objects = [inner, outer]

def draw_magnets():
    global magnet_objects
    for m in magnet_objects:
        m.visible = False
    magnet_objects = []
    for i in range(num_magnets):
        angle = 2*pi*i/num_magnets
        x = tokamak_center.x + (R + r_tube + 1) * cos(angle)
        z = tokamak_center.z + (R + r_tube + 1) * sin(angle)
        magnet = box(pos=vector(x, 0, z), size=vector(0.8, 4, 1.5), color=color.blue)
        magnet_objects.append(magnet)

# FIXED: draw_tokamak and draw_magnets are now actually called
draw_tokamak()
draw_magnets()

city_windows = []
building_positions = [vector(15,0,0), vector(18,0,0), vector(21,0,0), vector(24,0,0), vector(27,0,0)]
building_heights = [4, 6, 5, 8, 7]
for i in range(len(building_positions)):
    box(pos=building_positions[i], size=vector(2, building_heights[i], 2), color=color.gray(0.4))
    windss = box(pos=building_positions[i] + vector(0, 0.5, 1.1),
                 size=vector(1, 1, 0.2), color=color.black, emissive=True)
    city_windows.append(windss)

def update_city():
    for i in range(len(city_windows)):
        b = total_energy / energy_per_building - i
        if b < 0: b = 0
        if b > 1: b = 1
        city_windows[i].color = vector(b, b, 0.15*b)

# Elements
tritium   = FusingParticles(name="Tritium",   mass=5.008, charge=1.6, v_initial=vector(1, 0, 0.2),     color=color.red)
deuterium = FusingParticles(name="Deuterium", mass=3.344, charge=1.6, v_initial=vector(0.2, 0.2, 0),   color=color.cyan)
helium3   = FusingParticles(name="Helium-3",  mass=5.008, charge=3.2, v_initial=vector(0.5, 0.1, 0.3), color=color.orange)

# Making particles
particle1 = sphere(pos=vector(-8, 0, 0), radius=0.2, color=particles[0].color)
trail1 = curve(color=particles[0].color, radius=0.05)
mass1 = particles[0].mass
charge1 = particles[0].charge
v_init1 = -particles[0].velocity

particle2 = sphere(pos=vector(8, 0, 0), radius=0.2, color=particles[1].color)
trail2 = curve(color=particles[1].color, radius=0.05)
mass2 = particles[1].mass
charge2 = particles[1].charge
v_init2 = particles[1].velocity

def get_pos(phi, theta):
    x = (R + r_tube * cos(theta)) * cos(phi)
    y = r_tube * sin(theta)
    z = (R + r_tube * cos(theta)) * sin(phi)
    return vector(x, y, z) + tokamak_center

particle1.pos = get_pos(phi1, theta1)
particle2.pos = get_pos(phi2, theta2)

# Graphs
g1 = graph(title="Fusion Energy vs Time", xtitle="Time", ytitle="Energy (MeV)")
energy_curve = gcurve(color=color.yellow)

g2 = graph(title="Collision Count vs Time", xtitle="Time", ytitle="Collisions")
collision_curve = gcurve(color=color.green)

# Reset
def reset_sim():
    global v_init1, v_init2, t, running, phi1, phi2, theta1, theta2
    global total_energy, collision_count
    t = 0
    running = False
    play_button.text = "Start"
    phi1 = 0
    phi2 = pi
    theta1 = 0
    theta2 = 0
    total_energy = 0
    collision_count = 0
    trail1.clear()
    trail2.clear()
    v_init1 = -vector(find_particle(menu1.selected).velocity)
    v_init2 = vector(find_particle(menu2.selected).velocity)
    particle1.pos = get_pos(phi1, theta1)
    particle2.pos = get_pos(phi2, theta2)

def find_particle(name):
    for p in particles:
        if p.element == name:
            return p
    return None

def change_element1(i):
    global mass1, charge1, v_init1
    p = find_particle(i.selected)
    particle1.color = p.color
    trail1.color = p.color
    mass1 = p.mass
    charge1 = p.charge
    v_init1 = -vector(p.velocity)
    reset_sim()

def change_element2(i):
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
menu1 = menu(choices=element_names, selected=element_names[0], bind=change_element1)
scene.append_to_caption("  Particle 2: ")
menu2 = menu(choices=element_names, selected=element_names[1], bind=change_element2)
scene.append_to_caption("\n\n")

def toggle_sim(b):
    global running
    running = not running
    b.text = "Stop" if running else "Start"

play_button = button(text="Start", bind=toggle_sim)
scene.append_to_caption(" ")
button(text="Reset", bind=reset_sim)

dt = 0.01
t = 0

while True:
    rate(1000)
    if running:
        # Euler integration (unchanged from original)
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
            # FIXED: update_city is now actually called on fusion
            update_city()
            flash = sphere(pos=(particle1.pos + particle2.pos)/2,
                           radius=0.4, color=color.yellow, emissive=True)
            collisions.append(flash)

        energy_curve.plot(t, total_energy)
        collision_curve.plot(t, collision_count)
        t = t + dt

