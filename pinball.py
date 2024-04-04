"""
author 1: Daniel Zajac - 100820183
author 2s: Heisn Nithysingha - 100817036
"""

import pygame
import sys
import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import ode
import random
from datetime import datetime

# set up the colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# constants
G = 6.674e-11 # N kg-2 m^2
Earth_Mass = 5.972e24 # kg
Moon_Mass = 7.34767309e22 # kg
Distance = 384400000. # m


# clock object that ensure that animation has the same speed
# on all machines, regardless of the actual machine speed.
clock = pygame.time.Clock()

# in case we need to load an image
def load_image(name):
    image = pygame.image.load(name)
    return image

class HeavenlyBody(pygame.sprite.Sprite):
    
    def __init__(self, name, mass, color=WHITE, radius=0, imagefile=None):
        pygame.sprite.Sprite.__init__(self)

        if imagefile:
            self.image = load_image(imagefile)
        else:
            self.image = pygame.Surface([radius*2, radius*2])
            self.image.fill(BLACK)
            pygame.draw.circle(self.image, color, (radius, radius), radius, radius)

        self.rect = self.image.get_rect()
        self.pos = np.array([0,0])
        self.vel = np.array([0,0])
        self.mass = mass
        self.radius = radius
        self.name = name
        self.G = G
        self.distances = []

        self.solver = ode(self.f)
        self.solver.set_integrator('dopri5')

    def f(self, t, state, arg1, arg2, arg3, arg4):

        dxdt = state[2]
        dydt = state[3]

        if self.name == 'earth':
            mass = arg2
            other_mass = arg3
        else:
            mass = arg3
            other_mass = arg2

        # Formulas for Gravitational Force
        G, mass, other_mass = arg1, arg2, arg3
        d = np.array([arg4[0] - state[0], arg4[1] - state[1]])
        r = np.linalg.norm(d)
        u = d / r
        force = (G * mass * other_mass / (r**2)) * u

        dvxdt = force[0] / mass
        dvydt = force[1] / mass

        return [dxdt, dydt, dvxdt, dvydt]

    def setup(self, pos, vel):
        self.pos = np.array(pos)
        self.vel = np.array(vel)
        self.solver.set_initial_value([self.pos[0], self.pos[1], self.vel[0], self.vel[1]], 0) #initial states and time


    def update1(self, objects, dt, cur_time):
        force = np.array([0,0])
        for o in objects:
            if o != self.name:
                other = objects[o]

                if False: # Set this to True to print the following values
                    print ('Force on', self.name, ' from', other.name, '=', f)
                    print ('Mass-1', self.mass, 'mass-2', other.mass)
                    print ('G', self.G)
                    print ('Distance', r)
                    print ('Vel', self.vel)

                self.solver.set_f_params(self.G, self.mass, other.mass, other.pos)
                self.solver.integrate(cur_time)
                self.state = self.solver.y

                self.pos = self.state[:2]
                self.vel = self.state[2:]

                if self.name == 'earth':
                    self.distances.append(np.linalg.norm(other.pos - self.pos))

class Universe:
    def __init__(self):
        self.w, self.h = 2.6*Distance, 2.6*Distance 
        self.objects_dict = {}
        self.objects = pygame.sprite.Group()
        self.dt = 10.0
        self.cur_time = 0

    def add_body(self, body):
        self.objects_dict[body.name] = body
        self.objects.add(body)

    def to_screen(self, pos):
        return [int((pos[0] + 1.3*Distance)*640//self.w), int((pos[1] + 1.3*Distance)*640.//self.h)]

    def update(self):
        for o in self.objects_dict:
            # Compute positions for screen
            obj = self.objects_dict[o]
            obj.update1(self.objects_dict, self.dt, self.cur_time)
            p = self.to_screen(obj.pos)

            if False: # Set this to True to print the following values
                print ('Name', obj.name)
                print ('Position in simulation space', obj.pos)
                print ('Position on screen', p)

            # Update sprite locations
            obj.rect.x, obj.rect.y = p[0]-obj.radius, p[1]-obj.radius
        self.objects.update()
        self.cur_time += self.dt

    def draw(self, screen):
        self.objects.draw(screen)

def main():

    print ('Press q to quit')

    random.seed(0)
    
    # Initializing pygame
    pygame.init()
    win_width = 640
    win_height = 640
    screen = pygame.display.set_mode((win_width, win_height))  # Top left corner is (0,0)
    pygame.display.set_caption('Heavenly Bodies')

    # Create a Universe object, which will hold our heavenly bodies (planets, stars, moons, etc.)
    universe = Universe()

    earth = HeavenlyBody('earth', Earth_Mass, radius=32, imagefile='earth-northpole.jpg')
    earth.setup([0,0], [0,0])
    moon = HeavenlyBody('moon', Moon_Mass, WHITE, radius=10)
    moon.setup([int(Distance), 0], [0, 1000])

    universe.add_body(earth)
    universe.add_body(moon)

    total_frames = 500000
    iter_per_frame = 50

    frame = 0
    while frame < total_frames:
        if False:
            print ('Frame number', frame)        

        event = pygame.event.poll()
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit(0)
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_q:
            pygame.quit()
            sys.exit(0)
        else:
            pass

        universe.update()
        if frame % iter_per_frame == 0:
            screen.fill(BLACK) # clear the background
            universe.draw(screen)
            pygame.display.flip()
        frame += 1

    pygame.quit()

    plt.figure(1)
    plt.plot(earth.distances)
    plt.xlabel('frame')
    plt.ylabel('distance')
    plt.title('Distance between the earth and the moon')
    plt.show()


if __name__ == '__main__':
    main()