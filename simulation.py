# Simple pygame program

# Import and initialize the pygame library
import pygame
import pinball
import numpy as np
import math

def rotated_points(point, angle, r_point):
    Org_point = (point[0] - r_point[0], point[1] - r_point[1]) #
    x_ = (Org_point[0]* math.cos(math.radians(angle))) - (Org_point[1]* math.cos(math.radians(angle)))
    y_ = (Org_point[0]* math.sin(math.radians(angle))) + (Org_point[1]* math.cos(math.radians(angle)))
    print(f'Mouse clicked at ({x_ + r_point[0]}, { y_ + r_point[1]})')
    return ((x_ + r_point[0], y_ + r_point[1]))
    

from pygame.locals import (
    K_LEFT,
    K_RIGHT,
    KEYDOWN,
    K_ESCAPE,
)


pygame.init()

# Define constants for the screen width and height
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 1000
WALL_WIDTH = 10

PINB_LEFT = 35
PINB_RIGHT = 0
PINB_TOP = 50
PINB_BOTTOM = 0

L_ANGLE = 0
# Create the screen object
# The size is determined by the constant SCREEN_WIDTH and SCREEN_HEIGHT
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Run until the user asks to quit
running = True
while running:

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
    
    # Fill the background with white
    screen.fill((255, 255, 255))


    pygame.draw.rect(screen, (255,0,0), pygame.Rect(730, 250, WALL_WIDTH, 700)) #inner wall
    pygame.draw.rect(screen, (255,0,0), pygame.Rect(780, PINB_TOP, WALL_WIDTH, 900)) #right wall
    pygame.draw.rect(screen, (255,0,0), pygame.Rect(PINB_LEFT, PINB_TOP, WALL_WIDTH, 900)) #left wall
    pygame.draw.rect(screen, (255,0,0), pygame.Rect(PINB_LEFT, 949, 755, WALL_WIDTH)) # bottom wall
    pygame.draw.rect(screen, (255,0,0), pygame.Rect(PINB_LEFT, PINB_TOP, 750, WALL_WIDTH)) #top wall
    pygame.draw.polygon(screen, (255,0,0), ((785, 50),(785, 150),(675, 50))) #top right triangle
    pygame.draw.polygon(screen, (255,0,0), ((35, 50),(35, 150),(145, 50))) #top left triangle
    pygame.draw.polygon(screen, (255,0,0), ((35, 950),(35, 770),(255, 950))) #bottom left triangle
    pygame.draw.polygon(screen, (255,0,0), ((730, 950),(730, 770),(510, 950))) #bottom right triangle
    l_rotated_point = (201, 906)
    pygame.draw.polygon(screen, (0,0,0), (rotated_points((200, 930), L_ANGLE, l_rotated_point), rotated_points((200, 890), L_ANGLE, l_rotated_point), rotated_points((320, 910), L_ANGLE, l_rotated_point))) #left bumper
    pygame.draw.polygon(screen, (0,0,0), ((550, 890),(550, 930),(435, 910))) #right bumper
    
    l_x_offset = 10
    l_y_offset = 20
    pygame.draw.polygon(screen, (0,255,0), ((164, 243),(140, 264), (190, 310), (241, 264), (217, 243))) #diamond bumper
    pygame.draw.polygon(screen, (0,255,0), (rotated_points((530 + l_x_offset, 345 + l_y_offset), 45, (530, 345)), rotated_points((570+ l_x_offset, 345+ l_y_offset), 45, (530, 345)),  rotated_points((570+ l_x_offset, 515+ l_y_offset), 45, (530, 345)),  rotated_points((670+ l_x_offset, 515+ l_y_offset), 45, (530, 345)),  rotated_points((670+ l_x_offset, 545+ l_y_offset), 45, (530, 345)),  rotated_points((530+ l_x_offset, 545+ l_y_offset), 45, (530, 345)),  rotated_points((530+ l_x_offset,345+ l_y_offset), 45, (530, 345)))) #l bumper
    
    rotated_points((530, 345), 45, (670, 545))
    
    
    
    #pygame.draw.circle(screen, (0, 0, 255), (250, 250), 75)

    # Flip the display
    pygame.display.flip()


pygame.quit()