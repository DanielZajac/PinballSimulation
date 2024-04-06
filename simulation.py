# Simple pygame program

# Import and initialize the pygame library
import pygame
import pinball
import numpy as np
import math
import copy
import os

# Define constants for the screen width and height
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 1000
WALL_WIDTH = 10

PINB_LEFT = 35
PINB_RIGHT = 0
PINB_TOP = 50
PINB_BOTTOM = 0

shapes = [] #List with all shape coords
total_Frames = 0

#Background Frames
pygame.init()
# Create the screen object
# The size is determined by the constant SCREEN_WIDTH and SCREEN_HEIGHT
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

imp = [] #List of all background frames

# Set up Background frames
imp.append(pygame.image.load("Pinball_Background\Pinball_1.png").convert())
imp.append(pygame.image.load("Pinball_Background\Pinball_2.png").convert())
imp.append(pygame.image.load("Pinball_Background\Pinball_3.png").convert())
 
i = 0 #index for which background frame used


#Debugging Flag - if true all collision shapes appear
is_Debug = False

#Left Flipper properties
l_rotated_point = (201, 910)
L_angle_start = 45
L_angle = L_angle_start

#Right Flipper properties
r_rotated_point = (549, 907)
R_angle_start = -45
R_angle = R_angle_start

#Import sound mixer
pygame.mixer.init()

sound_file = "samplesound.wav"  # Change this to the path of your sound file
sound = pygame.mixer.Sound(sound_file)

#Ball properties
vel = [0,-150]
pos = [762, 691]
g = 0.005 # gamma (Drag Coeff)
m = 1
radius = 10

#L Bumper properties
l_x_offset = 0
l_y_offset = -80

#Square Bumper Properties
sq_x_offset = 25
sq_y_offset = 0
 
#World properties
dt = 0.05
G = 9.8

#sometimes we want to prevent collisions temporarily, like if the ball jumps really far in one step and clips into a platform, we need to get out
#so while we are getting out we do not detect collisions from within the block
collision_buffer = 0

def ball_update():
    global collision_buffer
    global sound

    #every frame decrease the buffer length remaining if the buffer is active
    if collision_buffer > 0:
        collision_buffer -= 1

    #so that the old position remains to be used in collision calculations
    prev_pos = copy.deepcopy(pos)
    
    #position update just to send where it would go to the collision function
    pos[0] += (dt * vel[0])
    pos[1] += (dt * vel[1])

    isCollision, new_velocity, time_to_collision, barrier_type = pinball.better_collision(prev_pos, pos, vel, radius, shapes)
    
    #if we are allowed to have a collision right now
    if isCollision and collision_buffer == 0:
        #playing sound on collision
        if sound:
            sound.play()

        collision_buffer = 2

        #we move in the old velocity direction until the collision would happen
        pos[0] = prev_pos[0] + (time_to_collision * vel[0])
        pos[1] = prev_pos[1] + (time_to_collision * vel[1])

        #now set up the new velocity for next time
        vel[0] = new_velocity[0]
        vel[1] = new_velocity[1]

    else:
        #default velocity update
        vel[0] += (dt * (-(g/m) * vel[0]))
        vel[1] += (dt * (-((g/m) * vel[1]) + G))

def rotated_points(point, angle, r_point):
    # Calculate the relative coordinates of the original point with respect to the reference point
    Org_point = (point[0] - r_point[0], point[1] - r_point[1])
    
    # Calculate the rotated coordinates using correct trigonometric functions
    x_ = Org_point[0] * math.cos(math.radians(angle)) - Org_point[1] * math.sin(math.radians(angle))
    y_ = Org_point[0] * math.sin(math.radians(angle)) + Org_point[1] * math.cos(math.radians(angle))
    
    # Add the coordinates of the reference point back to get the final rotated coordinates
    rotated_x = x_ + r_point[0]
    rotated_y = y_ + r_point[1]
    
    return (rotated_x, rotated_y)
    
def Rect_coords(top, left, width, height):
    return  [[top,left],[top+width,left],[top+width,left+height],[top,left+height]] #rect coords switched
    
from pygame.locals import (
    K_LEFT,
    K_RIGHT,
    KEYDOWN,
    K_ESCAPE,
)

def init():
    # Order of List: Inner wall, R wall, L wall, Bottom wall, top wall, 
    # Top r tri, top l tri, bot l tri, bot r tri, diamond bumper, L bumper
    # [-2] left bumper, [-1] right bumper
    
    shapes.append(Rect_coords(730, 250, WALL_WIDTH, 700)) #inner wall
    shapes.append(Rect_coords(780, PINB_TOP, WALL_WIDTH, 900)) #right wall
    shapes.append(Rect_coords(PINB_LEFT, PINB_TOP, WALL_WIDTH, 900)) #left wall
    shapes.append(Rect_coords(730, 940, 60, WALL_WIDTH)) # bottom wall
    shapes.append(Rect_coords(PINB_LEFT, PINB_TOP, 750, WALL_WIDTH)) #top wall
    
    shapes.append([[785, 50],[785, 150],[675, 50]]) #top right triangle
    shapes.append([[35, 50],[35, 150],[145, 50]]) #top left triangle
    shapes.append([[35, 950],[35, 770],[255, 950]]) #bottom left triangle
    shapes.append([[730, 949],[730, 770],[510, 949]]) #bottom right triangle
    
    shapes.append([[164, 243],[140, 264], [190, 310], [241, 264], [217, 243]]) #diamond bumper
    shapes.append([list(rotated_points((530 + l_x_offset, 345 + l_y_offset), 45, (530, 345))),list(rotated_points((570+ l_x_offset, 345+ l_y_offset), 45, (530, 345))), list(rotated_points((570+ l_x_offset, 515+ l_y_offset), 45, (530, 345))), list(rotated_points((670+ l_x_offset, 515+ l_y_offset), 45, (530, 345))),  list(rotated_points((670+ l_x_offset, 545+ l_y_offset), 45, (530, 345))),  list(rotated_points((530+ l_x_offset, 545+ l_y_offset), 45, (530, 345))), list(rotated_points((530+ l_x_offset,345+ l_y_offset), 45, (530, 345)))]) #L bumper
    shapes.append([[340 + sq_x_offset, 180 + sq_y_offset], [340 + sq_x_offset, 260 + sq_y_offset], [420 + sq_x_offset, 260 + sq_y_offset], [420 + sq_x_offset, 180 + sq_y_offset]]) #square bumper
    shapes.append([[115,726],[115, 519],[210,726]]) #Left Tri Bumper
    shapes.append([[560,726],[665, 520],[665,726]]) #Right Tri Bumper
    
    shapes.append([list(rotated_points((200, 930), L_angle, l_rotated_point)),list(rotated_points((200, 890), L_angle, l_rotated_point)),list(rotated_points((320, 910), L_angle, l_rotated_point))]) #left Flipper (moving)
    shapes.append([list(rotated_points((550, 890), R_angle, r_rotated_point)),list(rotated_points((550, 930), R_angle, r_rotated_point)),list(rotated_points((435, 910), R_angle, r_rotated_point))]) #Right Flipper (moving)

# Run until the user asks to quit
running = True
init()
while running:
    
    # Left Flipper Movement
    keys = pygame.key.get_pressed()
    if keys[K_LEFT]:
        if L_angle > L_angle_start - 45:
            L_angle -= 3
        elif L_angle == L_angle_start:
            L_angle = L_angle_start
    
    if L_angle <= L_angle_start and not keys[K_LEFT]: #falls back to resting position
        L_angle += 2
        
    if keys[K_RIGHT]:
        if R_angle < R_angle_start + 45:
            R_angle += 3
        elif R_angle == R_angle_start:
            R_angle = R_angle_start
    
    if R_angle >= R_angle_start and not keys[K_RIGHT]: #falls back to resting position
        R_angle -= 2
    
    

    # Did the user click the window close button?
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                running = False
        if event.type == pygame.QUIT:
            running = False


        if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                print(f'Mouse clicked at ({x}, {y})')
                
    # Set up Background frames
    imp[0] = pygame.image.load("Pinball_Background\Pinball_1.png").convert()
    imp[1] = pygame.image.load("Pinball_Background\Pinball_2.png").convert()
    imp[2] = pygame.image.load("Pinball_Background\Pinball_3.png").convert()
    
# Using blit to copy content from one surface to other
    screen.blit(imp[i], (0, 0))
    if i == 2: i = 0
    elif total_Frames % 10 == 0: i += 1
    

    if is_Debug:
        #Boarder prints
        pygame.draw.rect(screen, (255,0,0), pygame.Rect(730, 250, WALL_WIDTH, 700)) #inner wall
        pygame.draw.rect(screen, (255,0,0), pygame.Rect(780, PINB_TOP, WALL_WIDTH, 900)) #right wall
        pygame.draw.rect(screen, (255,0,0), pygame.Rect(PINB_LEFT, PINB_TOP, WALL_WIDTH, 900)) #left wall
        pygame.draw.rect(screen, (255,0,0), pygame.Rect(730, 940, 60, WALL_WIDTH)) # bottom wall
        pygame.draw.rect(screen, (255,0,0), pygame.Rect(PINB_LEFT, PINB_TOP, 750, WALL_WIDTH)) #top wall
        pygame.draw.polygon(screen, (255,0,0), ((785, 50),(785, 150),(675, 50))) #top right triangle
        pygame.draw.polygon(screen, (255,0,0), ((35, 50),(35, 150),(145, 50))) #top left triangle
        pygame.draw.polygon(screen, (255,0,0), ((35, 950),(35, 770),(255, 950))) #bottom left triangle
        pygame.draw.polygon(screen, (255,0,0), ((730, 949),(730, 770),(510, 949))) #bottom right triangle
        
        #Bumpers
        pygame.draw.polygon(screen, (0,255,0), ((164 , 243),(140, 264), (190, 310), (241, 264), (217, 243))) #diamond bumper
        pygame.draw.polygon(screen, (0,255,0), ((340 + sq_x_offset, 180 + sq_y_offset), (340 + sq_x_offset, 260 + sq_y_offset), (420 + sq_x_offset, 260 + sq_y_offset), (420 + sq_x_offset, 180 + sq_y_offset))) #square bumper
        pygame.draw.polygon(screen, (255,0,0), ((113,726),(113, 519),(210,726))) #Left Tri Bumper
        pygame.draw.polygon(screen, (255,0,0), ((560,726),(665, 520),(665,726))) #Right Tri Bumper
        #L Bumper
        pygame.draw.polygon(screen, (0,255,0), (rotated_points((530 + l_x_offset, 345 + l_y_offset), 45, (530, 345)), rotated_points((570+ l_x_offset, 345+ l_y_offset), 45, (530, 345)),  rotated_points((570+ l_x_offset, 515+ l_y_offset), 45, (530, 345)),  rotated_points((670+ l_x_offset, 515+ l_y_offset), 45, (530, 345)),  rotated_points((670+ l_x_offset, 545+ l_y_offset), 45, (530, 345)),  rotated_points((530+ l_x_offset, 545+ l_y_offset), 45, (530, 345)),  rotated_points((530+ l_x_offset,345+ l_y_offset), 45, (530, 345)))) #l bumper


    #Flipper prints
    #Left
    pygame.draw.polygon(screen, (0,0,0), (rotated_points((200, 930), L_angle, l_rotated_point), rotated_points((200, 890), L_angle, l_rotated_point), rotated_points((320, 910), L_angle, l_rotated_point))) #left Flipper
    shapes[-2] = ([list(rotated_points((200, 930), L_angle, l_rotated_point)),list(rotated_points((200, 890), L_angle, l_rotated_point)),list(rotated_points((320, 910), L_angle, l_rotated_point))]) #left Flipper (moving)
    
    #Right
    pygame.draw.polygon(screen, (0,0,0), (rotated_points((550, 890), R_angle, r_rotated_point), rotated_points((550, 930),  R_angle, r_rotated_point), rotated_points((435, 910), R_angle, r_rotated_point))) #Right Flipper
    shapes[-1] = ([list(rotated_points((550, 890), R_angle, r_rotated_point)),list(rotated_points((550, 930), R_angle, r_rotated_point)),list(rotated_points((435, 910), R_angle, r_rotated_point))]) #Right Flipper (moving)

    
    pygame.draw.circle(screen, (0, 0, 255), (pos[0], pos[1]), radius)
    ball_update()
    
    #print(pos)
    

    # Flip the display
    pygame.display.flip()
    total_Frames += 1


pygame.quit()