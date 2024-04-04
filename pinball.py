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

#we will store all of our shapes, and each shape will be a list of vertices (each with an x and y)
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