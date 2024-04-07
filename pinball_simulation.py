#Daniel Zajac Heisn Nithysingha Pinball Program

# Import and initialize the pygame library
import pygame
import collision_detection_response
import numpy as np
import math
import copy
import time

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

#Game Properties
lives = 3
points = 0

left_flipper_moving = False
right_flipper_moving = False
spring_moving = False

#Background Frames
pygame.init()
# Create the screen object
# The size is determined by the constant SCREEN_WIDTH and SCREEN_HEIGHT
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
Game_Text = pygame.font.Font("DeterminationSansWebRegular-369X.ttf", 30)


imp = [] #List of all background frames

# Set up Background frames
imp.append(pygame.image.load("PinBall_1.png").convert())
imp.append(pygame.image.load("PinBall_2.png").convert())
imp.append(pygame.image.load("PinBall_3.png").convert())

#set up Options menu
option = pygame.image.load("PinBall_Option.jpg").convert()

imp_switch = 1 #A number switch to help switch from game to options
 
i = 0 #index for which background frame used


#Import sound mixer
pygame.mixer.init()

sound = [-1] * 4 #will hold all sound to then use later
sound[1] = pygame.mixer.Sound("samplesound.wav")
sound[2] = pygame.mixer.Sound("multifellovo.wav")
sound[3] = pygame.mixer.Sound("sproing.wav")

#Debugging Flag - if true all collision shapes appear
is_Debug = False

#Left Flipper properties
L_Flip_y = 25
L_rotated_point = (201, 910 + L_Flip_y)
L_angle_start = 30
L_angle = L_angle_start

#Right Flipper properties
R_Flip_y = 30
R_Flip_x = 10
R_rotated_point = (549+ R_Flip_x, 907 + R_Flip_y)
R_angle_start = -30
R_angle = R_angle_start

#Spring properties
d = 0
max_d = 80

#Ball properties
vel = [0, 1]
start_pos = [763, 800]
pos = copy.deepcopy(start_pos)
m = 10
radius = 15
g = 0.05 # gamma (Drag Coeff)

#L Bumper properties
l_x_offset = 0
l_y_offset = -80

#Square Bumper Properties
sq_x_offset = 25
sq_y_offset = 0
 
#World properties
dt = 0.05
G = 100

def draw_popup():
    popup_surface = pygame.Surface((200, 100))  # Create a surface for the pop-up
    popup_surface.fill((1,1,1))  # Fill the surface with white color
    popup_rect = popup_surface.get_rect()
    popup_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)  # Center the pop-up on the screen

    # Draw the outline of the pop-up
    pygame.draw.rect(popup_surface, (0,0,0), popup_rect, 2)

    # Add text to the pop-up
    font = pygame.font.Font(None, 24)
    text_surface = font.render("This is a pop-up!", True, (0,0,0))
    text_rect = text_surface.get_rect(center=popup_rect.center)
    popup_surface.blit(text_surface, text_rect)

    screen.blit(popup_surface, popup_rect)
    
#sometimes we want to prevent collisions temporarily, like if the ball jumps really far in one step and clips into a platform, we need to get out
#so while we are getting out we do not detect collisions from within the block
collision_buffer = 0

def ball_update():
    global collision_buffer
    global sound
    global left_flipper_moving
    global right_flipper_moving
    global spring_moving
    global points

    #every frame decrease the buffer length remaining if the buffer is active
    if collision_buffer > 0:
        collision_buffer -= 1

    #so that the old position remains to be used in collision calculations
    prev_pos = copy.deepcopy(pos)
    
    #position update just to send where it would go to the collision function
    pos[0] += (dt * vel[0])
    pos[1] += (dt * vel[1])

    isCollision, new_velocity, time_to_collision, barrier_type, object_number = collision_detection_response.better_collision(prev_pos, pos, vel, radius, shapes, left_flipper_moving, right_flipper_moving, spring_moving)

    #if we are allowed to have a collision right now
    if isCollision and collision_buffer == 0:
        
        if object_number == 10:
            points += 50
        elif object_number == 11:
            points += 10
        elif object_number == 12:
            points += 11
        elif object_number == 13 or object_number == 14:
            points += 5
    
        #playing sound on collision
        if sound:
            sound[barrier_type].play()

        collision_buffer = 0

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
    K_RETURN,
    K_r,
    K_s,
    K_c,
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
    
    shapes.append([[742, 840 + d],[782, 840 + d],[782, 865 + d], [742, 865 + d]]) #Spring
    
    shapes.append([[164, 243],[140, 264], [190, 310], [241, 264], [217, 243]]) #diamond bumper
    shapes.append([list(rotated_points((530 + l_x_offset, 345 + l_y_offset), 45, (530, 345))),list(rotated_points((570+ l_x_offset, 345+ l_y_offset), 45, (530, 345))), list(rotated_points((570+ l_x_offset, 515+ l_y_offset), 45, (530, 345))), list(rotated_points((670+ l_x_offset, 515+ l_y_offset), 45, (530, 345))),  list(rotated_points((670+ l_x_offset, 545+ l_y_offset), 45, (530, 345))),  list(rotated_points((530+ l_x_offset, 545+ l_y_offset), 45, (530, 345))), list(rotated_points((530+ l_x_offset,345+ l_y_offset), 45, (530, 345)))]) #L bumper
    shapes.append([[340 + sq_x_offset, 180 + sq_y_offset], [340 + sq_x_offset, 260 + sq_y_offset], [420 + sq_x_offset, 260 + sq_y_offset], [420 + sq_x_offset, 180 + sq_y_offset]]) #square bumper
    shapes.append([[115,726],[115, 519],[210,726]]) #Left Tri Bumper
    shapes.append([[560,726],[665, 520],[665,726]]) #Right Tri Bumper
    
    shapes.append([list(rotated_points((200, 930 + L_Flip_y), L_angle, L_rotated_point)),list(rotated_points((200, 890 + L_Flip_y), L_angle, L_rotated_point)),list(rotated_points((320, 910 + L_Flip_y), L_angle, L_rotated_point))]) #left Flipper (moving)
    shapes.append([list(rotated_points((550+ R_Flip_x, 890 + R_Flip_y), R_angle, R_rotated_point)),list(rotated_points((550+ R_Flip_x, 930 + R_Flip_y), R_angle, R_rotated_point)),list(rotated_points((435+ R_Flip_x, 910+ R_Flip_y), R_angle, R_rotated_point))]) #Right Flipper (moving)

# Run until the user asks to quit
running = True
init()
while running:
    
    # Left Flipper Movement
    keys = pygame.key.get_pressed()
    if keys[K_LEFT]:
        if L_angle > L_angle_start - 45:
            L_angle -= 3
            left_flipper_moving = True
    
    if L_angle <= L_angle_start and not keys[K_LEFT]: #falls back to resting position
        L_angle += 2
        left_flipper_moving = False
    
    # Right Flipper Movement    
    if keys[K_RIGHT]:
        if R_angle < R_angle_start + 45:
            R_angle += 3
            right_flipper_moving = True
    
    if R_angle >= R_angle_start and not keys[K_RIGHT]: #falls back to resting position
        R_angle -= 2
        right_flipper_moving = False
    
    # Spring Movement and d tracker
    if keys[K_s]:
        if d != max_d:
            d += 2
            spring_moving = False
    
    if d > 0 and not keys[K_s]:
        d -= 4
        spring_moving = True
    elif d < 0 and not keys[K_s]:
        spring_moving = False
        d = 0

    if pos[1] >= 1000: #if ball went down the hole run over
                pos = copy.deepcopy(start_pos)
                vel = [0,0]
                lives -= 1
                spring_moving = False
                if lives == 0:
                    running = False

    for event in pygame.event.get():
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                running = False
            if event.key == K_r: #if run reset
                draw_popup()
                pos = copy.deepcopy(start_pos)
                vel = [0,0]
                lives -= 1
                spring_moving = False
                if lives == 0:
                    running = False
            
            if event.key == K_c and imp_switch % 2 != 0:
                imp_switch += 1
            if event.key == K_RETURN and imp_switch % 2 == 0:
                imp_switch += 1     
                    
        if event.type == pygame.QUIT:
            running = False


        if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                print(f'Mouse clicked at ({x}, {y})')
    
# Using blit to copy content from one surface to other

    if imp_switch % 2 == 0:
        screen.blit(option, (-1, -3))
    else:
        screen.blit(imp[i], (-1, -3))
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
    pygame.draw.polygon(screen, (0,0,0), (rotated_points((200, 930 + L_Flip_y), L_angle, L_rotated_point), rotated_points((200, 890+ L_Flip_y), L_angle, L_rotated_point), rotated_points((320, 910+ L_Flip_y), L_angle, L_rotated_point))) #left Flipper
    shapes[-2] = ([list(rotated_points((200, 930+ L_Flip_y), L_angle, L_rotated_point)),list(rotated_points((200, 890+ L_Flip_y), L_angle, L_rotated_point)),list(rotated_points((320, 910+ L_Flip_y), L_angle, L_rotated_point))]) #left Flipper (moving)
    
    #Right
    pygame.draw.polygon(screen, (0,0,0), (rotated_points((550+ R_Flip_x, 890+ R_Flip_y), R_angle, R_rotated_point), rotated_points((550+ R_Flip_x, 930+ R_Flip_y),  R_angle, R_rotated_point), rotated_points((435+ R_Flip_x, 910+ R_Flip_y), R_angle, R_rotated_point))) #Right Flipper
    shapes[-1] = ([list(rotated_points((550+ R_Flip_x, 890+ R_Flip_y), R_angle, R_rotated_point)),list(rotated_points((550+ R_Flip_x, 930+ R_Flip_y), R_angle, R_rotated_point)),list(rotated_points((435+ R_Flip_x, 910+ R_Flip_y), R_angle, R_rotated_point))]) #Right Flipper (moving)

    #Spring
    pygame.draw.polygon(screen, (255,0,0), ((742, 840 + d),(782, 840 + d),(782, 865 + d), (742, 865 + d))) #Spring box

    shapes[9] = [[742, 840 + d],[782, 840 + d],[782, 865 + d], [742, 865 + d]]

    #print(f"D = {pos}")
    if imp_switch % 2 != 0:
        pygame.draw.circle(screen, (0, 0, 255), (pos[0], pos[1]), radius) #Ball Update
        ball_update()
    
    text_surface = Game_Text.render(f'Points = {points}        Balls Remaining = {lives}', False, (0, 0, 0))
    screen.blit(text_surface, (200,0))

    # Flip the display
    pygame.display.flip()
    total_Frames += 1

    #uncomment to debug frame by frame
    #time.sleep(5)

pygame.quit()