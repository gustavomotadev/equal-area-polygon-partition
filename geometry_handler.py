import math
from random import random
from functools import reduce
from copy import deepcopy

def random_points(n):
    points = []
    for _ in range(n):
        points.append((random(), random()))
    return points

def translate_points(points, x, y):
    points = list(map(lambda a: (a[0]+x, a[1]+y), points))
    return points

def multiply_points(points, x, y):
    points = list(map(lambda a: (a[0]*x, a[1]*y), points))
    return points

def get_centroid(points):
    size = len(points)
    centroid = reduce(lambda a,b: (a[0]+b[0], a[1]+b[1]), points)
    centroid = (centroid[0]/size, centroid[1]/size)
    return centroid

def get_bounding_box(points):
    x, y = zip(*points)
    min_x, min_y, max_x, max_y = min(x), min(y), max(x), max(y)
    width = max_x-min_x
    height = max_y-min_y
    center_x = (min_x + max_x)/2
    center_y = (min_y + max_y)/2
    return (center_x, center_y), width, height

def vector_angle_to_x_axis(start_point, end_point):
    ang = math.atan2(end_point[1]-start_point[1], end_point[0]-start_point[0])
    if ang < 0:
        ang += 2*math.pi
    return ang

def vector_angle_to_vector(vector_start, vector1_end, vector2_end):
    ang1 = vector_angle_to_x_axis(vector_start, vector1_end)
    ang2 = vector_angle_to_x_axis(vector_start, vector2_end)
    ang = ang1 - ang2
    if ang < 0:
        ang += 2*math.pi
    return ang

def polygon_order(points, centroid):
    points.sort(key=lambda a: vector_angle_to_x_axis(centroid, a))
    return points

def new_polygon(sides):
    polygon = random_points(sides)
    centroid = get_centroid(polygon)
    polygon = polygon_order(polygon, centroid)
    return polygon

def remove_angles_threshold(points, low, high):
    old_size = len(points) + 1
    while len(points) > 3 and len(points) < old_size:
        old_size = len(points)
        more_points = [points[-1]] + points + [points[0]]
        to_remove = []
        for i in range(1, len(more_points)-1):
            angle = vector_angle_to_vector(more_points[i], more_points[i-1], more_points[i+1])
            if angle <= low or angle >= high:
                to_remove.append(points[i-1])
        diff = len(points) - len(to_remove)
        if diff < 3:
            to_remove = to_remove[3-diff:]
        points = list(filter(lambda a: not a in to_remove, points))
    return points

def set_width_and_height(points, new_width, new_height):
    center, width, height = get_bounding_box(points)
    points = multiply_points(points, new_width/width, new_height/height)
    return points

def translate_to_center(points, offset_x=0, offset_y=0):
    center, width, height = get_bounding_box(points)
    points = translate_points(points, 0.5-center[0]+offset_x, 0.5-center[1]+offset_y)
    return points

def get_vertical_lines_coordinates(points):
    coords = set()
    for point in points:
        coords.add(point[0])
    coords = list(coords)
    coords.sort()
    return coords

def get_minX_point_index(points):
    minX = points[0][0]
    minIndex = 0
    for i in range(len(points)):
        if points[i][0] < minX:
            minX = points[i][0]
            minIndex = i
    return minIndex

def shift_list(list_to_shift, rshifts):
    return list_to_shift[rshifts:] + list_to_shift[:rshifts]

def get_line_equation(point1, point2):
    m = (point2[1]-point1[1])/(point2[0]-point1[0])
    n = point1[1] - m*point1[0]
    return m, n

def get_angular_coefficient(point1, point2):
    return (point2[1]-point1[1])/(point2[0]-point1[0])

def apply_line_equation(m, n, x):
    return m*x + n

def vertical_decomposition(points, lines):
    #get leftmost vertex as the first
    points = shift_list(points, get_minX_point_index(points))
    vertexes_to_insert = []
    #for each line except first and last verify where it intercepts the polygon
    for x in lines[1:-1]:
        for i in range(len(points)):
            if (points[i][0] > x and points[i-1][0] < x):
                m, n = get_line_equation(points[i-1], points[i])
                y = apply_line_equation(m, n, x)
                vertexes_to_insert.append((points[i], (x, y)))
            elif (points[i][0] < x and points[i-1][0] > x):
                m, n = get_line_equation(points[i], points[i-1])
                y = apply_line_equation(m, n, x)
                vertexes_to_insert.append((points[i-1+1], (x, y)))
    #add the new vertexes to the polygon
    for vertex in list(filter(lambda a: not a[1] in points, vertexes_to_insert)):
        index = points.index(vertex[0])
        points.insert(index, vertex[1])

    return points

def x_order(points):
    return points.sort(key=lambda a: a[0])

def get_trapezoid_structure(points, lines):
    structure = [[] for _ in range(len(lines))]
    for point in points:
        structure[lines.index(point[0])].append(point)
    for line in structure:
        line.sort(key=lambda a: a[1])
    return structure

def get_trapezoid_area(sideA, sideB):
    a = sideA[-1][1] - sideA[0][1]
    b = sideB[-1][1] - sideB[0][1]
    h = sideB[0][0] - sideA[0][0]
    return ((a+b)*h)/2

def get_total_trapezoid_area(trapezoid_structure):
    sum = 0
    for i in range(len(trapezoid_structure)-1):
        area = get_trapezoid_area(trapezoid_structure[i], trapezoid_structure[i+1])
        sum += area
        #print('Area %d = %.6f' % (i, area))
    #print('Total Area = %.6f' % sum)
    return sum

def bisect_trapezoid_with_desired_area(sideA, sideB, area):
    a = abs(sideA[-1][1] - sideA[0][1])
    m, n = get_line_equation(sideA[-1], sideB[-1])
    k, l = get_line_equation(sideA[0], sideB[0])

    A = (m-k)/2

    if A != 0:

        B = n-l
        X0 = sideA[0][0]
        I = A*X0*X0 + B*X0
        C = -1*I -1*area
        D = B*B-4*A*C

        X1 = (-1*B + math.sqrt(D))/(2*A)
        #X2 = (-1*B - math.sqrt(D))/(2*A)

    else:

        X1 = sideA[0][0] + area/a

    return X1
    #return X1, X2

def get_equal_area_vertical_lines(trapezoid_structure, number_of_regions):
    desired_area = get_total_trapezoid_area(trapezoid_structure)/number_of_regions
    #print('Desired Subregion Count = %d' % number_of_regions)
    #print('Desired Subregion Area = %.6f' % desired_area)
    area_lines = []
    area_lines.append(trapezoid_structure[0][0][0])

    leftover = 0
    for structure_pointer in range(len(trapezoid_structure)-1):
        right_limit = trapezoid_structure[structure_pointer+1][0][0]
        #print('New Limit = %.6f' % right_limit)
        #print('New Area = %.6f' % get_trapezoid_area(trapezoid_structure[structure_pointer], trapezoid_structure[structure_pointer+1]))
        available_area = get_trapezoid_area(trapezoid_structure[structure_pointer], trapezoid_structure[structure_pointer+1]) + leftover
        #print('Available Area = %.6f' % available_area)
        multiplier = 1

        try:
            new_line = bisect_trapezoid_with_desired_area(trapezoid_structure[structure_pointer], trapezoid_structure[structure_pointer+1], desired_area*multiplier-leftover)
            #print('Try X = %.6f' % new_line)
            while new_line <= right_limit:
                area_lines.append(new_line)
                #print('New Division')
                available_area -= desired_area
                multiplier += 1
                new_line = bisect_trapezoid_with_desired_area(trapezoid_structure[structure_pointer], trapezoid_structure[structure_pointer+1], desired_area*multiplier-leftover)
                #print('Try X = %.6f' % new_line)
        except ValueError:
            #print('VALUE ERROR')
            pass

        leftover = available_area
        #print('Leftover = %.6f' % leftover)

    if len(area_lines) > number_of_regions:
        del area_lines[-1]
    area_lines.append(trapezoid_structure[-1][0][0])

    return area_lines

def equal_area_decomposition(polygon, number_of_regions):
    #save polygon copy
    polygon_copy = deepcopy(polygon)
    #get coordinates of vertical lines
    lines = get_vertical_lines_coordinates(polygon)
    #decompose polygon vertically
    polygon = vertical_decomposition(polygon, lines)
    #generate data structure better suited for the calculations
    trapezoid_structure = get_trapezoid_structure(polygon, lines)
    #find the vertical lines that divide the polygon into equal areas
    equal_lines = get_equal_area_vertical_lines(trapezoid_structure, number_of_regions)
    #decompose polygon copy vertically
    polygon_copy = vertical_decomposition(polygon_copy, equal_lines)

    return polygon_copy, equal_lines

def new_convex_polygon(sides):
    return remove_angles_threshold(new_polygon(sides), 0, math.pi)

def get_vertical_sub_polygons(polygon, equal_lines):
    polygons = [[] for _ in range(len(equal_lines)-1)]

    for i in range(len(equal_lines)-1):
        for point in polygon:
            #essa comparacao precisa ter margens de erro devido aos problemas de representacao de numeros reais em binario
            if point[0]-equal_lines[i] >= (0-(0.001*abs(point[0]))) and point[0]-equal_lines[i+1] <= (0+(0.001*abs(point[0]))):
                polygons[i].append(point)

    for i in range(len(polygons)):
        centroid = get_centroid(polygons[i])
        polygons[i] = polygon_order(polygons[i], centroid)
        
    return polygons

def rotate_points_90_counterclockwise(points):
    for i in range(len(points)):
        points[i] = (-1*points[i][1], points[i][0])
    return points

def rotate_points_90_clockwise(points):
    for i in range(len(points)):
        points[i] = (points[i][1], -1*points[i][0])
    return points