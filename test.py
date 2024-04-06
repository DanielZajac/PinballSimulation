def line_intersection(point1, point2, shape1, shape2):

    #find slope of our travel path line
    point_line_slope = (point2[1]-point1[1])/(point2[0]-point1[0]) if point2[0] - point1[0] != 0 else float('inf')
    #find slope of shape line
    shape_line_slope = (shape1[1]-shape2[1])/(shape1[0]-shape2[0]) if shape1[0] - shape2[0] != 0 else float('inf')

    if point_line_slope == float('inf'): #point line (travel path) is vertical
        x_intersect = point1[0]
        y_intersect = shape_line_slope * (x_intersect - shape1[0]) + shape1[1]
    elif shape_line_slope == float('inf'): #line between shape vertices is vertical
        x_intersect = shape1[0]
        y_intersect = point_line_slope * (x_intersect - point1[0]) + point1[1]
    else:
        if (point_line_slope - shape_line_slope) == 0:
            x_intersect = float('inf')
            y_intersect = float('inf')
        else:
            x_intersect = (point_line_slope * point1[0] - shape_line_slope * shape1[0] + shape1[1] - point1[1]) / (point_line_slope - shape_line_slope)
            y_intersect = point_line_slope * (x_intersect - point1[0]) + point1[1]

    return x_intersect, y_intersect

import numpy as np
potential_lines = []
shape = [[0, 0], [2, 6], [10, 0], [0,0]]

ball_velocity = [1, 0]
ball_radius = 1.1
ball_pos_start = [-3, 3.5]
ball_pos_end = [0.5, 3.5]
error = 0.005

for i in range(len(shape) - 1):
    shape_line_vector = [shape[i+1][0] - shape[i][0], shape[i+1][1] - shape[i][1]]

    #finding unit vector of shape line
    shape_line_vector_length = np.sqrt((shape_line_vector[0])**2 + (shape_line_vector[1])**2)
    shape_line_vector_unit = [shape_line_vector[0]/shape_line_vector_length, shape_line_vector[1]/shape_line_vector_length]

    #finding the two perpindicular vectors to our shape_line_vector
    perpindicular_collision_line1 = [-shape_line_vector_unit[1], shape_line_vector_unit[0]]
    perpindicular_collision_line2 = [shape_line_vector_unit[1], -shape_line_vector_unit[0]]

    if np.dot(perpindicular_collision_line1, ball_velocity) < 0:
        response_direction = perpindicular_collision_line1

        #will use this value to find the collision point and then collision time
        ball_collision_direction_from_radius = perpindicular_collision_line2
    else:
        response_direction = perpindicular_collision_line2
        ball_collision_direction_from_radius = perpindicular_collision_line1


    #finding the point on the ball which makes contact with the platform
    ball_collision_direction_from_radius = np.array(ball_collision_direction_from_radius)
    ball_collision_point_start = ball_pos_start + ball_radius*(ball_collision_direction_from_radius)
    ball_collision_point_end = ball_pos_end + ball_radius*(ball_collision_direction_from_radius)

    print(ball_collision_point_start)

    #this point will be the closest point on the shape line to the ball
    x_intersect, y_intersect = line_intersection(ball_pos_end, ball_collision_point_end, shape[i], shape[i+1])
    print("Intersect:", x_intersect, y_intersect)

    #now we want to check if that closest point on the line is within 'radius' units of the center of the ball at the end of its path
    distance_to_line = np.sqrt((x_intersect - ball_pos_end[0])**2 + (y_intersect - ball_pos_end[1])**2)

    #if it is within radius, we have a collision and add it to potential lines
    if distance_to_line <= ball_radius + error:
        if (x_intersect >= min(ball_collision_point_end[0], ball_pos_end[0])-error and x_intersect <= max(ball_collision_point_end[0], ball_pos_end[0])+error and
            y_intersect >= min(ball_collision_point_end[1], ball_pos_end[1])-error and y_intersect <= max(ball_collision_point_end[1], ball_pos_end[1])+error and
            x_intersect >= min(shape[i][0], shape[i+1][0])-error and x_intersect <= max(shape[i][0], shape[i+1][0])+error and
            y_intersect >= min(shape[i][1], shape[i+1][1])-error and y_intersect <= max(shape[i][1], shape[i+1][1])+error):
            potential_lines.append([shape[i], shape[i+1], x_intersect, y_intersect, distance_to_line, [response_direction[0], response_direction[1]], [ball_collision_point_start[0], ball_collision_point_start[1]]])

        print("Potential collision with shape ", "with vertices" ,i ,i+1, ".\n Here is the response direction: ", response_direction, "ball collision end", ball_collision_point_end)