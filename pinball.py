"""
author 1: Daniel Zajac - 100820183
author 2: Heisn Nithysingha - 100817036
"""

import numpy as np

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

#error here allows us us to account for rounding error
#for example if a collision line is flat, when we find the y_intersection with other lines it will round the value slightly so we need error to check it
error = 0.005
def better_collision(ball_pos_start, ball_pos_end, ball_velocity, ball_radius, shapes):
    #we will fetch our shapes from simulation, and each shape will be a list of vertices (each with an x and y)
    
    for shape in shapes:
        shape.append(shape[0])

    #used later
    num_shapes = len(shapes)

    #need to find out the 'left' and 'right' sides of the ball, if we consider the 'top' the point mostforward in the direction the ball is going
    #to do this, find the line perpindicular to the balls direction, and go 'radius' units in the positive and negative direction

    #make the ball direction unit vector
    length_ball_direction = np.sqrt(ball_velocity[0]**2 + ball_velocity[1]**2)
    ball_direction_unit = [ball_velocity[0]/length_ball_direction, ball_velocity[1]/length_ball_direction]

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

    #first (and main) part of the collision detection system
    #now if there was no collision on the path, we will check for collisions near the end of the ball's travel
    potential_lines = []
    count = 0
    for shape in shapes:
        for i in range(len(shape)-1):

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

            #this point will be the closest point on the shape line to the ball
            x_intersect, y_intersect = line_intersection(ball_pos_end, ball_collision_point_end, shape[i], shape[i+1])

            #now we want to check if that closest point on the line is within 'radius' units of the center of the ball at the end of its path
            distance_to_line = np.sqrt((x_intersect - ball_pos_end[0])**2 + (y_intersect - ball_pos_end[1])**2)

            #find actual point where they collide
            x_intersect, y_intersect = line_intersection(ball_collision_point_start, [ball_collision_point_start[0] + ball_velocity[0], ball_collision_point_start[1] + ball_velocity[1]], shape[i], shape[i+1])

            #if it is within radius, we have a collision and add it to potential lines
            if distance_to_line <= ball_radius + error:
                if (x_intersect >= min(ball_collision_point_end[0], ball_pos_end[0])-error and x_intersect <= max(ball_collision_point_end[0], ball_pos_end[0])+error and
                    y_intersect >= min(ball_collision_point_end[1], ball_pos_end[1])-error and y_intersect <= max(ball_collision_point_end[1], ball_pos_end[1])+error and
                    x_intersect >= min(shape[i][0], shape[i+1][0])-error and x_intersect <= max(shape[i][0], shape[i+1][0])+error and
                    y_intersect >= min(shape[i][1], shape[i+1][1])-error and y_intersect <= max(shape[i][1], shape[i+1][1])+error):
                    potential_lines.append([shape[i], shape[i+1], x_intersect, y_intersect, distance_to_line, count, [response_direction[0], response_direction[1]], [ball_collision_point_start[0], ball_collision_point_start[1]]])
        count += 1

    if len(potential_lines) != 0:
        min_distance_to_intersection = 10000000

        #now want to find the closest line if multiple intersect
        for line in potential_lines:
            if line[4] < min_distance_to_intersection:
                closest_line = line
                min_distance_to_intersection = line[4]

        #barrier types: 1 = wall, 2 = flipper, 3 = bumper
        barrier_type = 0
        if closest_line[5] < 10:
            barrier_type = 1
        elif closest_line[5] >= num_shapes-2:
            barrier_type = 2
        else:
            barrier_type = 3
        
        #calculting velocity after force is applied in direction of platform's normal vector
        force_strength = 15

        #if the contact was with our flippers, we increase the force applied (the flippers in our game have a greater applied force when something hits them)
        if barrier_type == 2:
            force_strength = 30
        elif barrier_type == 1:
            force_strength = 0

        response_direction = np.array(closest_line[6])
        ball_velocity = np.array(ball_velocity)

        #calculate the component of velocity parallel to the normal
        parallel_component = np.dot(ball_velocity, response_direction) * response_direction
        #calculate the component of velocity perpendicular to the normal
        perpendicular_component = ball_velocity - parallel_component

        #disregard the parallel component, replace it with a force in parallel direction and add it to the perpendicular component
        new_velocity = [(response_direction[0]*force_strength)+(-parallel_component[0])+perpendicular_component[0], (response_direction[1]*force_strength)+(-parallel_component[1])+perpendicular_component[1]]

        #finding distance to travel from ball contacat point start to intersection point (all in direction of velocity)
        distance_to_travel = np.sqrt((closest_line[7][0] - closest_line[2])**2 + (closest_line[7][1] - closest_line[3])**2)
        velocity_magnitude = np.sqrt((ball_velocity[0])**2 + (ball_velocity[1])**2)

        #distance/velocity to find time until collision
        collision_dt = distance_to_travel/velocity_magnitude

        print("Good collision")
        return True, new_velocity, collision_dt, barrier_type, closest_line[5]

    #this will store the lines which intersect at least one of the ball's boundary lines on its travel path
    potential_lines = []
    for i in range(2):
        if (i == 0):
            point1 = left_pos_start
            point2 = left_pos_end
        else:
            point1 = right_pos_start
            point2 = right_pos_end

        #now we iterate through all shapes in our pinball machine
        count = 0
        for shape in shapes:
            #for each shape we will check each line (each adjacent pair of vertices), note that the last index is the first again (so that we don't miss the final line)
            for i in range(len(shape)-1):

                shape_line_slope = (shape[i][1]-shape[i+1][1])/(shape[i][0]-shape[i+1][0]) if shape[i][0] - shape[i+1][0] != 0 else float('inf')
                #finding the intersection of the boundary line and shape line
                x_intersect, y_intersect = line_intersection(point1, point2, shape[i], shape[i+1])
                
                #checking if the intersection point is within the actual line, not far off in the distance
                if (x_intersect >= min(point1[0], point2[0])-error and x_intersect <= max(point1[0], point2[0])+error and
                    y_intersect >= min(point1[1], point2[1])-error and y_intersect <= max(point1[1], point2[1])+error and
                    x_intersect >= min(shape[i][0], shape[i+1][0])-error and x_intersect <= max(shape[i][0], shape[i+1][0])+error and
                    y_intersect >= min(shape[i][1], shape[i+1][1])-error and y_intersect <= max(shape[i][1], shape[i+1][1])+error):
                    potential_lines.append([shape[i], shape[i+1], x_intersect, y_intersect, shape_line_slope, count])
                    #adding the two vertices line to the list of potential first contacts, and their intersect
            count += 1
                

    if len(potential_lines) != 0:
        min_distance_to_intersection = 10000000000
        for line in potential_lines:

            #now we want to check which intersection point is closest to the center of the ball's starting position
            distance_to_line = np.sqrt((line[2]-ball_pos_start[0])**2 + (line[3]-ball_pos_end[1])**2)

            if distance_to_line < min_distance_to_intersection:
                closest_line = line
                min_distance_to_intersection = distance_to_line

        #now find which direction the response force is in
        #note that we only need to apply a force as a response since our collisions in the pinball machine are 'powered by the machine (not just static walls)'
        #also note that the force will therefore always be away and perpindicular from the wall

        #find unit vector in the direction of the wall (doesn't matter which way along the wall it is since we are just using it to find 2 perpindicular lines)
        collision_wall_line_vector = [closest_line[0][0] - closest_line[1][0], closest_line[0][1] - closest_line[1][1]]
        collision_wall_line_vector_length = np.sqrt((collision_wall_line_vector[0])**2 + (collision_wall_line_vector[1])**2)
        collision_wall_line_vector_unit = [collision_wall_line_vector[0]/collision_wall_line_vector_length, collision_wall_line_vector[1]/collision_wall_line_vector_length]

        #finding the two perpindicular lines to our wall (which are also unit vectors)
        perpindicular_collision_line1 = [-collision_wall_line_vector_unit[1], collision_wall_line_vector_unit[0]]
        perpindicular_collision_line2 = [collision_wall_line_vector_unit[1], -collision_wall_line_vector_unit[0]]

        #to find which perpindicular direction is correct, find the dot product between the line and the ball's velocity
        #whichever dot product is less than zero means that line (generally) opposes the ball's velocity (their angle between is >90 degrees)
        #we want to find that line because the ball cannot have a collision with a wall which is facing the same direction as velocity (shown in report)
        if np.dot(perpindicular_collision_line1, ball_velocity) < 0:
            response_direction = perpindicular_collision_line1

            #will use this value to find the collision point and then collision time
            ball_collision_direction_from_radius = perpindicular_collision_line2
        else:
            response_direction = perpindicular_collision_line2
            ball_collision_direction_from_radius = perpindicular_collision_line1
        
        response_direction = np.array(response_direction)
        ball_velocity = np.array(ball_velocity)

        #calculate the component of velocity parallel to the normal
        parallel_component = np.dot(ball_velocity, response_direction) * response_direction
        #calculate the component of velocity perpendicular to the normal
        perpendicular_component = ball_velocity - parallel_component


        #barrier types: 1 = wall, 2 = flipper, 3 = bumper
        barrier_type = 0
        if closest_line[5] < 10:
            barrier_type = 1
        elif closest_line[5] >= num_shapes-2:
            barrier_type = 2
        else:
            barrier_type = 3
        
        #calculting velocity after force is applied in direction of platform's normal vector
        force_strength = 15

        #if the contact was with our flippers, we increase the force applied (the flippers in our game have a greater applied force when something hits them)
        if barrier_type == 2:
            force_strength = 30
        elif barrier_type == 1:
            force_strength = 0

        #disregard the parallel component, replace it with a force in parallel direction and add it to the perpendicular component
        new_velocity = [(response_direction[0]*force_strength)+(-parallel_component[0])+perpendicular_component[0], (response_direction[1]*force_strength)+(-parallel_component[1])+perpendicular_component[1]]

        ball_collision_point_start = ball_pos_start + ball_radius*(ball_collision_direction_from_radius)

        #find where we make contact with the shape
        contact_point_x, contact_point_y = line_intersection(ball_collision_point_start, [ball_collision_point_start[0] + ball_velocity[0], ball_collision_point_start[1] + ball_velocity[1]], closest_line[0], closest_line[1])

        #finding distance to travel from start to contact point (all in direction of velocity)
        distance_to_travel = np.sqrt((ball_collision_point_start[0] - contact_point_x)**2 + (ball_collision_point_start[1] - contact_point_y)**2)
        velocity_magnitude = np.sqrt((ball_velocity[0])**2 + (ball_velocity[1])**2)

        #distance/velocity to find time until collision
        collision_dt = distance_to_travel/velocity_magnitude

        return True, new_velocity, collision_dt, barrier_type, closest_line[5]

    #now if no collisions ever happened, return default values which won't trigger updates in the ball update function
    return False, [0, 0], 0, 0, 0