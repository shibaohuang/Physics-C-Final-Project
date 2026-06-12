Web VPython 3.2
from vpython import *

# ---------------- Static Variables ----------------
B_field = vector(0, 0, 4)
particles = []
collisions = []
running = False
shutdown = False
fusion_distance = 0.7
collision_count = 0
total_energy = 0

# stuff for the E = mc^2 calc
c_light = 3e8
defect_fraction = 0.00375   # D-T turns about 0.375% of the mass into energy
energy_per_building = 35.2  # MeV to light up one building

# Lawson: n * T * tau has to clear 3e21 keV*s/m^3 or the thing dies
lawson_threshold = 3e21
lawson_fail_time = 0
shutdown_grace = 2.0   # give it 2 sec under the line before shutting down

tokamak_center = vector(-15, 0, 0)
num_magnets = 8
magnet_objects = []
tokamak_objects = []
base_field_strength = 0.25

# ---------------- Tokamak Geometry ----------------
R = 8       # major radius, the big donut circle
r_tube = 4  # minor radius, particles loop around inside this
toroidal_speed = 0.5
phi1 = 0   # where particle 1 starts on the big circle
phi2 = 0
theta1 = 0  # where it starts inside the tube
theta2 = 0

class FusingParticles:
    def __init__(self, name, mass, charge, v_initial, color):
        particles.append(self)
        self.element = name
        self.mass = mass      # 10^-27 kg
        self.charge = charge  # 10^-19 C
        self.velocity = v_initial
        self.color = color

# ---------------- Drawing the Reactor ----------------
def draw_tokamak():
    global tokamak_objects
    # wipe the old rings first or they pile up every redraw
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
    # space the magnets evenly around the ring
    for i in range(num_magnets):
        angle = 2*pi*i/num_magnets
        x = tokamak_center.x + (R + r_tube + 1) * cos(angle)
        z = tokamak_center.z + (R + r_tube + 1) * sin(angle)
        magnet = box(pos=vector(x, 0, z), size=vector(0.8, 4, 1.5), color=color.blue)
        magnet_objects.append(magnet)

# ---------------- City ----------------
city_windows = []
building_positions = [vector(15,0,0), vector(18,0,0), vector(21,0,0), vector(24,0,0), vector(27,0,0)]
building_heights = [4,6,5,8,7]
for i in range(len(building_positions)):
    box(pos=building_positions[i], size=vector(2,building_heights[i],2), color=color.gray(0.4))
    # the glowy window on the front face
    windss = box(pos=building_positions[i] + vector(0, 0.5, 1.1),
                 size=vector(1, 1, 0.2), color=color.black, emissive=True)
    city_windows.append(windss)

def update_city():
    # each window brightens as we rack up energy, one building at a time
    for i in range(len(city_windows)):
        b = total_energy/energy_per_building - i
        if b < 0: b = 0
        if b > 1: b = 1
        city_windows[i].color = vector(b, b, 0.15*b)

# ---------------- Elements ----------------
# masses in 10^-27 kg, charges in 10^-19 C
tritium   = FusingParticles(name="Tritium",   mass=5.008, charge=1.6, v_initial=vector(1, 0, 0.2),   color=color.red)
deuterium = FusingParticles(name="Deuterium", mass=3.344, charge=1.6, v_initial=vector(0.2, 0.2, 0), color=color.cyan)
helium3   = FusingParticles(name="Helium-3",  mass=5.008, charge=3.2, v_initial=vector(0.5, 0.1, 0.3), color=color.orange)

# ---------------- Making Particles ----------------
particle1 = sphere(pos=vector(0,0,0), radius=0.2, color=particles[0].color)
trail1 = curve(color=particles[0].color, radius=0.05)
mass1 = particles[0].mass
charge1 = particles[0].charge
v_init1 = -particles[0].velocity

particle2 = sphere(pos=vector(0,0,0), radius=0.2, color=particles[1].color)
trail2 = curve(color=particles[1].color, radius=0.05)
mass2 = particles[1].mass
charge2 = particles[1].charge
v_init2 = particles[1].velocity

# map the two angles to an actual xyz point on the torus
def get_pos(phi, theta):
    x = (R + r_tube * cos(theta)) * cos(phi)
    y = r_tube * sin(theta)
    z = (R + r_tube * cos(theta)) * sin(phi)
    return vector(x, y, z) + tokamak_center

# ---------------- Physics ----------------
def lorentz_accel(v, q, m):
    # a = (q/m) v x B, straight off F = qv x B
    return (q/m) * cross(v, B_field)

def rk4_velocity(v, q, m, dt):
    # RK4 step instead of plain Euler, way less drift
    k1 = lorentz_accel(v, q, m)
    k2 = lorentz_accel(v + 0.5*dt*k1, q, m)
    k3 = lorentz_accel(v + 0.5*dt*k2, q, m)
    k4 = lorentz_accel(v + dt*k3, q, m)
    return v + (dt/6)*(k1 + 2*k2 + 2*k3 + k4)

def fusion_energy_mc2(m1, m2):
    # E = (delta m)c^2 from the mass defect, then convert J to MeV
    delta_m = defect_fraction * (m1 + m2) * 1e-27
    E_joules = delta_m * c_light**2
    return E_joules / 1.602e-13

def effective_density():
    # thinner tube = same plasma squeezed tighter, so n goes up like 1/r^2
    return density_slider.value * (4.0/r_tube)**2

def plasma_temperature():
    # fake a temperature off the mean kinetic energy (keV)
    return 8.0 * (mag2(v_init1) + mag2(v_init2)) / 2

def confinement_time():
    # stronger field holds the plasma longer
    return 0.5 * mag(B_field)

def lawson_product():
    return effective_density()*1e20 * plasma_temperature() * confinement_time()

def shutdown_reactor():
    global running, shutdown
    running = False
    shutdown = True
    for m in magnet_objects:
        m.color = color.red
    for w in city_windows:
        w.color = color.black
    status_text.text = "REACTOR SHUTDOWN: Lawson criterion not met. Press Reset."

# ---------------- Graphs ----------------
g1 = graph(title="Fusion Energy vs Time", xtitle="Time", ytitle="Energy (MeV)")
energy_curve = gcurve(color=color.yellow)
g2 = graph(title="Collision Count vs Time", xtitle="Time", ytitle="Collisions")
collision_curve = gcurve(color=color.green)
g3 = graph(title="Particle Speed vs Time", xtitle="Time", ytitle="Speed")
velocity1_curve = gcurve(color=color.red, label="Particle 1")
velocity2_curve = gcurve(color=color.blue, label="Particle 2")
g4 = graph(title="Particle Acceleration vs Time", xtitle="Time", ytitle="|a| = |qv x B|/m")
accel1_curve = gcurve(color=color.red, label="Particle 1")
accel2_curve = gcurve(color=color.blue, label="Particle 2")

# ---------------- Buttons ----------------
def toggle_sim(b):
    global running
    if shutdown:
        return   # once it's dead you have to reset
    running = not running
    b.text = "Pause" if running else "Play"

def reset_sim():
    # dump everything back to defaults
    menu1.selected = element_names[0]
    menu2.selected = element_names[1]
    bfield_slider.value = 2
    toroidal1_slider.value = 0.5
    magnet_slider.value = 8
    rtube_slider.value = 4
    density_slider.value = 5
    for c in collisions:
        c.visible = False
    change_sim()

def change_sim():
    global B_field, running, shutdown, v_init1, v_init2
    global total_energy, collision_count, lawson_fail_time
    global toroidal_speed
    global phi1, phi2, theta1, theta2, t, num_magnets, r_tube
    global mass1, mass2, charge1, charge2

    # pull all the current slider/menu values
    toroidal1_text.text = "{:.2f}".format(toroidal1_slider.value)
    bfield_text.text = "{:.2f}".format(bfield_slider.value)
    num_magnets = int(magnet_slider.value)
    magnet_text.text = str(num_magnets)
    r_tube = rtube_slider.value
    rtube_text.text = "{:.1f}".format(r_tube)
    density_text.text = "{:.1f}".format(density_slider.value)

    draw_tokamak()
    draw_magnets()

    running = False
    shutdown = False
    play_button.text = "Play"
    t = 0
    lawson_fail_time = 0

    trail1.clear()
    trail2.clear()
    p1 = find_particle(menu1.selected)
    p2 = find_particle(menu2.selected)
    particle1.color = p1.color
    particle2.color = p2.color
    trail1.color = p1.color
    trail2.color = p2.color
    mass1 = p1.mass
    charge1 = p1.charge
    mass2 = p2.mass
    charge2 = p2.charge

    # back to starting angles
    phi1 = 0
    phi2 = 0
    theta1 = 0
    theta2 = 0
    toroidal_speed = toroidal1_slider.value
    # external field plus a bit extra per magnet
    B_strength = bfield_slider.value + num_magnets * base_field_strength
    B_field = vector(0, 0, B_strength)

    particle1.pos = get_pos(phi1, theta1)
    particle2.pos = get_pos(phi2, theta2)

    # wipe the graphs
    velocity1_curve.delete()
    velocity2_curve.delete()
    accel1_curve.delete()
    accel2_curve.delete()
    energy_curve.delete()
    collision_curve.delete()

    v_init1 = -vector(p1.velocity)
    v_init2 = vector(p2.velocity)
    total_energy = 0
    collision_count = 0
    update_city()
    update_status()

def update_status():
    prod = lawson_product()
    lawson_text.text = "Lawson product: {:.2f}".format(prod/1e21) + " x10^21  (need >= 3.00 x10^21 keV*s/m^3)"
    if shutdown:
        return
    if prod >= lawson_threshold:
        status_text.text = "Lawson criterion MET - reactor stable."
    else:
        status_text.text = "WARNING: Lawson criterion NOT met - reactor will shut down!"
    # win condition: every building lit
    if total_energy >= energy_per_building * len(city_windows):
        status_text.text = "CITY FULLY POWERED! Total energy: {:.1f} MeV".format(total_energy)

def find_particle(name):
    for p in particles:
        if p.element == name:
            return p
    return None

def change_element1(i):
    change_sim()

def change_element2(i):
    change_sim()

element_names = [p.element for p in particles]

# ---------------- UI ----------------
scene.caption = "Press Play to Start Fusion \n\n"
play_button = button(text="Play", bind=toggle_sim)
scene.append_to_caption(" ")
button(text="Reset", bind=reset_sim)
scene.append_to_caption("\n\n")
scene.append_to_caption("Particle 1: ")
menu1 = menu(choices=element_names, selected=element_names[0], bind=change_element1)
scene.append_to_caption(" Particle 2: ")
menu2 = menu(choices=element_names, selected=element_names[1], bind=change_element2)
scene.append_to_caption("\n")

scene.append_to_caption("\n\nExternal B Field Strength: ")
bfield_text = wtext(text="2.00")
scene.append_to_caption("\n")
bfield_slider = slider(min=0, max=10, value=2, length=300, bind=change_sim)

scene.append_to_caption("\n\nParticle's Toroidal Speed: ")
toroidal1_text = wtext(text="0.50")
scene.append_to_caption("\n")
toroidal1_slider = slider(min=0.1, max=3.0, value=0.5, length=300, bind=change_sim)

scene.append_to_caption("\n\nNumber of Magnets: ")
magnet_text = wtext(text="8")
scene.append_to_caption("\n")
magnet_slider = slider(min=4, max=20, value=8, length=300, bind=change_sim)

scene.append_to_caption("\n\nReactor Tube Radius (cross-section): ")
rtube_text = wtext(text="4.0")
scene.append_to_caption("\n")
rtube_slider = slider(min=1.5, max=6, value=4, step=0.5, length=300, bind=change_sim)

scene.append_to_caption("\n\nPlasma Density (x10^20 per m^3): ")
density_text = wtext(text="5.0")
scene.append_to_caption("\n")
density_slider = slider(min=1, max=10, value=5, step=0.5, length=300, bind=change_sim)

scene.append_to_caption("\n\n")
status_text = wtext(text="")
scene.append_to_caption("\n")
lawson_text = wtext(text="")
scene.append_to_caption("\n")

# kick everything off now that the widgets exist
change_sim()

# ---------------- Simulation Loop ----------------
dt = 0.01
t = 0
frame = 0
old_pos1 = vector(particle1.pos)
old_pos2 = vector(particle2.pos)

while True:
    rate(1000)
    if running:
        frame += 1
        old_pos1 = vector(particle1.pos)
        old_pos2 = vector(particle2.pos)

        # RK4 velocity update under F = qv x B
        v_init1 = rk4_velocity(v_init1, charge1, mass1, dt)
        v_init2 = rk4_velocity(v_init2, charge2, mass2, dt)
        a1 = mag(lorentz_accel(v_init1, charge1, mass1))
        a2 = mag(lorentz_accel(v_init2, charge2, mass2))

        # helix = drift around the donut + spin inside the tube
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

        # reaction rate R12 = n1*n2*<sigma*v_rel>
        # grab the real velocities from how far they actually moved
        real_v1 = (particle1.pos - old_pos1) / dt
        real_v2 = (particle2.pos - old_pos2) / dt
        v_rel = mag(real_v1 - real_v2)
        n_eff = effective_density()
        # chance of fusing when they're close, scales with density^2 * v_rel
        p_fuse = 0.0008 * n_eff * n_eff * v_rel
        if p_fuse > 1: p_fuse = 1

        if mag(particle1.pos - particle2.pos) < fusion_distance and random() < p_fuse:
            collision_count += 1
            # E = mc^2 payout from the mass defect
            if collision_count > 0:
                E_released = fusion_energy_mc2(mass1, mass2)
                total_energy += E_released
                update_city()
            flash = sphere(pos=(particle1.pos+particle2.pos)/2, radius=0.4,
                               color=color.yellow, emissive=True, opacity=1)
            collisions.append(flash)

        # fade the old flashes out
        for c in collisions:
            if c.visible:
                c.opacity = c.opacity - 0.02
                if c.opacity <= 0.05:
                    c.visible = False

        # Lawson check: under the line too long and it shuts down
        if lawson_product() < lawson_threshold:
            lawson_fail_time += dt
            for m in magnet_objects:
                m.color = color.orange   # warning color
            if lawson_fail_time > shutdown_grace:
                shutdown_reactor()
        else:
            lawson_fail_time = 0
            for m in magnet_objects:
                m.color = color.blue

        # only plot every 5th frame so it doesn't lag
        if frame % 5 == 0:
            energy_curve.plot(t, total_energy)
            collision_curve.plot(t, collision_count)
            velocity1_curve.plot(t, mag(v_init1))
            velocity2_curve.plot(t, mag(v_init2))
            accel1_curve.plot(t, a1)
            accel2_curve.plot(t, a2)
        if frame % 25 == 0:
            update_status()

        t = t + dt