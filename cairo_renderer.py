import cairo
from random import random, shuffle

def cairo_new_surface_and_context(width, height):
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    context = cairo.Context(surface)
    context.scale(width, height)
    return (width, height), surface, context

def cairo_clear_screen(context, color):
    context.rectangle(0, 0, 1, 1)
    context.set_source_rgb(*color)
    context.fill()

def cairo_fill_and_stroke(context, points, fill_color, stroke_color, stroke_width):
    context.move_to(*points[0])
    for i in range(1, len(points)):
        context.line_to(*points[i])
    context.close_path()
    context.set_source_rgb(*fill_color)
    context.fill_preserve()
    context.set_source_rgb(*stroke_color)
    context.set_line_width(stroke_width)
    context.stroke()

def cairo_draw_vertical_lines(context, lines, color, width, limit1, limit2):
    context.set_source_rgb(*color)
    context.set_line_width(width)
    for line in lines:
        context.move_to(line, limit1)
        context.line_to(line, limit2)
        context.stroke()

def cairo_draw_crosses(context, points, color, size, width, x=False):
    context.set_source_rgb(*color)
    context.set_line_width(width)
    x = int(x)*size/2
    for point in points:
        context.move_to(point[0]-(size/2), point[1]-x)
        context.line_to(point[0]+(size/2), point[1]+x)
        context.stroke()
        context.move_to(point[0]+x, point[1]-(size/2))
        context.line_to(point[0]-x, point[1]+(size/2))
        context.stroke()

def cairo_draw_interior_vertical_segments(context, points, color, width):
    context.set_source_rgb(*color)
    context.set_line_width(width)
    for i in range(len(points)):
        for j in range(len(points)):
            if i != j and points[i][0] == points[j][0]:
                context.move_to(points[i][0], points[i][1])
                context.line_to(points[j][0], points[j][1])
                context.stroke()

def cairo_draw_line(context, point1, point2, color, width):
    context.set_source_rgb(*color)
    context.set_line_width(width)
    context.move_to(*point1)
    context.line_to(*point2)
    context.stroke()

def cairo_draw_polygon_default(context, polygon, lines, limit1, limit2):
    #draw vertical lines
    cairo_draw_vertical_lines(context, lines, (1.0, 0.0, 0.0), 0.0025, limit1, limit2)
    #draw polygon
    cairo_fill_and_stroke(context, polygon, (0.2, 0.5, 1.0), (0.1, 0.1, 0.7), 0.005)
    #draw interior vertical line segments of polygon
    cairo_draw_interior_vertical_segments(context, polygon, (0.1, 0.1, 0.7), 0.004)
    #draw vertices
    cairo_draw_crosses(context, polygon, (0.0, 1, 0.0), 0.02, 0.004, True)

def cairo_draw_polygon_color(context, polygon, color, limit1, limit2):
    #draw polygon
    cairo_fill_and_stroke(context, polygon, color, (1, 1, 1), 0.002)

def random_nice_color(brightness=1):
    color = [1, random(), 0]
    shuffle(color)
    return tuple(map(lambda a: a*brightness, color))

def hue_ordered_nice_color(number, brightness=1, x=0.0):
    number %= 6
    if number < 1:
        color = (1, number, x)
    elif number < 2:
        color = (2-number, 1, x)
    elif number < 3:
        color = (x, 1, number-2)
    elif number < 4:
        color = (x, 4-number, 1)
    elif number < 5:
        color = (number-4, x, 1)
    else:
        color = (1, x, 6-number)

    return tuple(map(lambda a: a*brightness, color))

def ordered_grayscale(number, mask=(1.0, 1.0, 1.0)):
    number %= 1
    return (number*mask[0], number*mask[1], number*mask[2])

def cairo_draw_colored_polygons_default(context, polygons, start=0.0, end=6.0, withBug=False):
    if withBug:
        bug = 0
    else:
        bug = start
    for poly in polygons:
        cairo_draw_polygon_color(context, poly, hue_ordered_nice_color(start, 0.9, 0.5), 0.5, 1)
        start += (end-bug)/(len(polygons))

def cairo_draw_colored_polygon_matrix_default(context, matrix):
    start = 0.0
    increment = 6.0/len(matrix)

    for column in matrix:
        cairo_draw_colored_polygons_default(context, column, start, start+increment, True)
        start += increment