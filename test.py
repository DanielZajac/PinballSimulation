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

x_intersect, y_intersect, = line_intersection([5,5],[7,7],[1,6],[5,6])
point1, point2, shape1, shape2 = [5,5],[7,7],[1,6],[5,6]

if (x_intersect >= min(point1[0], point2[0]) and x_intersect <= max(point1[0], point2[0]) and
                    y_intersect >= min(point1[1], point2[1]) and y_intersect <= max(point1[1], point2[1]) and
                    x_intersect >= min(shape1[0], shape2[0]) and x_intersect <= max(shape1[0], shape2[0]) and
                    y_intersect >= min(shape1[1], shape2[1]) and y_intersect <= max(shape1[1], shape2[1])):
    print("HI")