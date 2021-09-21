#!/usr/bin/env python
from cairo_renderer import *
from geometry_handler import *

HORIZONTAL = 8
VERTICAL = 8

#create surface, context and clear screen
cairo_size, surface, context = cairo_new_surface_and_context(800, 800)
cairo_clear_screen(context, (1.0, 1.0, 1.0))

#create polygon, adjust size, position and angles
polygon = new_convex_polygon(10)
polygon = set_width_and_height(polygon, 0.4, 0.4)
polygon = translate_to_center(polygon, -0.25, -0.25)

################################################################################################
#save polygon copy
polygon_copy = deepcopy(polygon)
################################################################################################

#get coordinates of the vertical lines
lines = get_vertical_lines_coordinates(polygon)
#draw everything about polygon
cairo_draw_polygon_default(context, polygon, lines, 0.0, 0.5)

#translate polygon to the second location
polygon = translate_to_center(polygon, 0.25, -0.25)

################################################################################################
#decompose polygon vertically
lines = get_vertical_lines_coordinates(polygon)
polygon = vertical_decomposition(polygon, lines)
################################################################################################

#get coordinates of the vertical lines
lines = get_vertical_lines_coordinates(polygon)
#draw everything about polygon
cairo_draw_polygon_default(context, polygon, lines, 0.0, 0.5)

#translate polygon and copy to the third location
polygon = translate_to_center(polygon, -0.25, 0.25)
polygon_copy = translate_to_center(polygon_copy, -0.25, 0.25)

################################################################################################
#generate data structure better suited for the calculations
lines = get_vertical_lines_coordinates(polygon)
trapezoid_structure = get_trapezoid_structure(polygon, lines)

#find the vertical lines that divide the polygon into equal areas
equal_lines = get_equal_area_vertical_lines(trapezoid_structure, HORIZONTAL)
#decompose polygon copy vertically
polygon_copy = vertical_decomposition(polygon_copy, equal_lines)
################################################################################################

#draw everything about polygon
cairo_draw_vertical_lines(context, equal_lines, (1.0, 0.0, 0.0), 0.0025, 0.5, 1.0)
#cairo_draw_polygon_default(context, polygon_copy, equal_lines, 0.5, 1.0)

#break polygon into vertical sub polygons
vertical_polygons = get_vertical_sub_polygons(polygon_copy, equal_lines)

#draw all the sub polygons
cairo_draw_colored_polygons_default(context, vertical_polygons)

all_sub_polygons = [[] for _ in range(len(vertical_polygons))]
for poly in vertical_polygons:
    poly = rotate_points_90_counterclockwise(poly)
    poly, eq_lines = equal_area_decomposition(poly, VERTICAL)
    polys = get_vertical_sub_polygons(poly, eq_lines)
    all_sub_polygons.append(polys)

for column in all_sub_polygons:
    for i in range(len(column)):
        column[i] = rotate_points_90_clockwise(column[i])
        column[i] = translate_points(column[i], 0.5, 0.0)

cairo_draw_colored_polygon_matrix_default(context, all_sub_polygons)
    
#draw separating lines in middle of image
cairo_draw_line(context, (0.5, 0), (0.5, 1), (0.0, 0.0, 0.0), 0.005)
cairo_draw_line(context, (0, 0.5), (1, 0.5), (0.0, 0.0, 0.0), 0.005)

surface.write_to_png("area.png")