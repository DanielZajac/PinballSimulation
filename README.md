# Pinball Simulation
#### Physics simulation of a playable pinball machine using pygame

Made by Daniel Zajac and Heisn Nithysingha

To test out this simulation, clone the repository and run the file pinball_simulation.py.

### About this simulation:
In this pinball simulation, you start with three balls. Each time a ball falls through the middle or you reset the ball, you lose a remaining ball. Once you lost all of your balls, your run is over. During the run, each time you hit a bumper your points will increase, so you can try to set a higher score each time!

This simulation is mainly focused on creating an accurate collision detection and response system. Try it out for yourself!

##### Note:
If you run the file and the pygame window is partially cut off, then you can either change your display zoom in your computer's settings - 
##### Windows: Settings->System->Display->Scale and Layout
##### Mac: System Settings->Displays->More Space
or you can find the following line in pinball_simulation.py:

##### screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

and change this line to:

##### screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)

This command will fit the display to your screen, although the dimensions will be distorted, so lowering zoom on your computer is preferred.