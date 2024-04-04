"""
author 1: Daniel Zajac - 100820183
author 2s: Heisn Nithysingha - 100817036
"""

import pygame
import math
import sys
import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import ode
import random
from datetime import datetime

#we wil store all of our shapes, and each shape will be a list of vertices (each with an x and y)
shapes = []


def better_collision(ball_pos_start, ball_pos_end, ball_direction, ball_radius):
    #need to find out the 'left' and 'right' sides of the ball, if we consider the 'top' the point mostforward in the direction the ball is going
    #to do this, find the line perpindicular to the balls direction, and go 'radius' units in the positive and negative direction
    
    #make the ball direction unit vector
    length_ball_direction = np.sqrt(ball_direction[0]**2 + ball_direction[1]**2)
    ball_direction_unit = [ball_direction[0]/length_ball_direction, ball_direction[1]/length_ball_direction]

    #finding the right and left vector directions
    right_direction = [ball_direction_unit[1], -ball_direction_unit[0]]
    left_direction = [-ball_direction_unit[1], ball_direction_unit[0]]

    #now find the left and right points of the ball (relative to direction) at start and end (before and after time step)
    left_pos_increment = ball_radius * left_direction
    left_pos_start = ball_pos_start + left_pos_increment
    left_pos_end = ball_pos_end + left_pos_increment

    right_pos_increment = ball_radius * right_direction
    right_pos_start = ball_pos_start + right_pos_increment
    right_pos_end = ball_pos_end + right_pos_increment

    #now we want to check if any shape lines intersect these 'boundary lines' of our ball's travel path

    for i in range(2):
            if (i == 0):
                point1 = left_pos_start
                point2 = left_pos_end
            else:
                point1 = right_pos_start
                point2 = right_pos_end
            
            #find slope of our travel path line
            point_line_slope = (point2[1]-point1[1])/(point2[0]-point1[0]) if point2[0] - point1[0] != 0 else float('inf')

            #this will store the lines which intersect at least one of the ball's boundary lines on its travel path
            potential_lines = []

            #now we iterate through all shapes in our pinball machine
            for shape in shapes:
                #for each shape we will check each line (each adjacent pair of vertices), note that the last index is the first again (so that we don't miss the final line)
                for i in range(len(shape)-1):
                    shape_line_slope = (shape[i][1]-shape[i+1][1])/(shape[i][0]-shape[i+1][0]) if shape[i][0] - shape[i+1][0] != 0 else float('inf')
                    if point_line_slope == float('inf'): #point line (travel path) is vertical
                        x_intersect = point1[0]
                        y_intersect = shape_line_slope * (x_intersect - shape[i][0]) + shape[i][1]
                    elif shape_line_slope == float('inf'): #line between shape vertices is vertical
                        x_intersect = shape[i][0]
                        y_intersect = point_line_slope * (x_intersect - point1[0]) + point1[1]
                    else:
                        x_intersect = (point_line_slope * point1[0] - shape_line_slope * shape[i][0] + shape[i][1] - point1[1]) / (point_line_slope - shape_line_slope)
                        y_intersect = point_line_slope * (x_intersect - point1[0]) + point1[1]
                    
                    #checking if the intersection point is within the acutal line, not far off in the distance
                    if (x_intersect >= min(point1[0], point2[0]) and x_intersect <= max(point1[0], point2[0]) and
                        y_intersect >= min(point1[1], point2[1]) and y_intersect <= max(point1[1], point2[1]) and
                        x_intersect >= min(shape[i][0], shape[i+1][0]) and x_intersect <= max(shape[i][0], shape[i+1][0]) and
                        y_intersect >= min(shape[i][1], shape[i+1][1]) and y_intersect <= max(shape[i][1], shape[i+1][1])):
                        potential_lines.append(shape[i], shape[i+1], x_intersect, y_intersect)
                        #adding the two vertices line to the list of potential first contacts, and their intersect

            if len(potential_lines) != 0:
                min_distance_to_intersection = 10000000000
                for line in potential_lines:
                    #now we want to check which intersection point is closest to the center of the ball's starting position
                    distance_to_line = np.sqrt((line[2]-ball_pos_start[0])**2 + (line[3]-ball_pos_end[1])**2)

                    if distance_to_line < min_distance_to_intersection:
                        closest_line = line
                        min_distance_to_intersection = distance_to_line

    return True

#checks if there is a collision, and returns the line which was collided with
def iscollision(point1, point2):
    point_line_slope = (point2[1]-point1[1])/(point2[0]-point1[0]) if point2[0] - point1[0] != 0 else float('inf')

    potential_lines = []
    for shape in shapes:
        for i in range(len(shape)-1):
            shape_line_slope = (shape[i][1]-shape[i+1][1])/(shape[i][0]-shape[i+1][0]) if shape[i][0] - shape[i+1][0] != 0 else float('inf')
            if point_line_slope == float('inf'): #point line is vertical
                x_intersect = point1[0]
                y_intersect = shape_line_slope * (x_intersect - shape[i][0]) + shape[i][1]
            elif shape_line_slope == float('inf'): #line between shape vertices is vertical
                x_intersect = shape[i][0]
                y_intersect = point_line_slope * (x_intersect - point1[0]) + point1[1]
            else:
                x_intersect = (point_line_slope * point1[0] - shape_line_slope * shape[i][0] + shape[i][1] - point1[1]) / (point_line_slope - shape_line_slope)
                y_intersect = point_line_slope * (x_intersect - point1[0]) + point1[1]
            
            #checking if the intersection point is within the acutal line, not far off in the distance
            if (x_intersect >= min(point1[0], point2[0]) and x_intersect <= max(point1[0], point2[0]) and
                y_intersect >= min(point1[1], point2[1]) and y_intersect <= max(point1[1], point2[1]) and
                x_intersect >= min(shape[i][0], shape[i+1][0]) and x_intersect <= max(shape[i][0], shape[i+1][0]) and
                y_intersect >= min(shape[i][1], shape[i+1][1]) and y_intersect <= max(shape[i][1], shape[i+1][1])):
                potential_lines.append(shape[i], shape[i+1]) #adding the two vertices line to the list of potential first contacts
                
    #now we have a list of the collision lines which are intersected, and we want to find which line was collided with first
    if len(potential_lines) != 0:
        min_distance_to_line = 10000000000
        for line in potential_lines:
            #finding the distance from ball position to collision line
            a = line[1][1] - line[0][1]
            b = line[0][0] - line[1][0]
            c = line[1][0]*line[0][1] - line[0][0]*line[1][1]
            distance_to_line = abs(a*point1[0] + b*point1[1] + c) / math.sqrt(a**2 + b**2)

            #want to find what the ball collided with first
            if distance_to_line < min_distance_to_line:
                closest_line = line
                min_distance_to_line = distance_to_line

        return True, closest_line
    #if there are no lines collided with, return false, and a filler value
    else:
        return False, [[0, 0], [0, 0]]











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