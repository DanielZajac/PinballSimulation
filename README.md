# PinballSimulation
Physics simulation of a playable pinball machine using pygame

The python file you want to run to play pinball is simulation.py
If you run the file and the window is getting cut off (computers may have different resolution and zoom), then you can either change the zoom in your settings (on windows settings->System->Display->Scale and Layout) (on Mac "temp"), or you can find the following line in simulation.py

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

and change this line to 

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)

This will normalize the display to fit your screen