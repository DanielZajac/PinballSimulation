# Simple pygame program

# Import and initialize the pygame library
import pygame
import pinball

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
                print(f'Mouse clicked at {x}, {y}')
    
    # Fill the background with white
    screen.fill((255, 255, 255))


    pygame.draw.rect(screen, (255,0,0), pygame.Rect(730, 100, WALL_WIDTH, 850))
    pygame.draw.rect(screen, (255,0,0), pygame.Rect(780, 100, WALL_WIDTH, 850))
    
    
    
    #pygame.draw.circle(screen, (0, 0, 255), (250, 250), 75)

    # Flip the display
    pygame.display.flip()


pygame.quit()