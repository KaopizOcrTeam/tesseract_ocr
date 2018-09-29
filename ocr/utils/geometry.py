import sys
import numpy as np


def get_line_slope(line):
    """

    :param line: ((x1, y1), (x2, y2))
    :return:
    """

    if line[0][0] == line[1][0]:
        return sys.maxsize / 2

    slope = (line[0][1] - line[1][1]) / (line[0][0] - line[1][0])

    return slope


def get_cross_point(line_a, line_b):
    """

    :param line_a: ((xa1, ya1), (xa2, ya2))
    :param line_b: ((xb1, yb1), (xb2, yb2))
    :return: (cross_x, cross_y)
    """

    if line_a[0][0] == line_a[1][0] and line_b[0][0] == line_b[1][0]:
        return [None, None]

    if line_a[0][0] == line_a[1][0]:
        cross_x = line_a[0][0]
        slope_b = (line_b[0][1] - line_b[1][1]) / (line_b[0][0] - line_b[1][0])
        intercept_b = (line_b[1][1] * line_b[0][0] - line_b[0][1] * line_b[1][0]) / (line_b[0][0] - line_b[1][0])
        cross_y = int(slope_b * cross_x + intercept_b)

        return [cross_x, cross_y]

    if line_b[0][0] == line_b[1][0]:
        cross_x = line_b[0][0]
        slope_a = (line_a[0][1] - line_a[1][1]) / (line_a[0][0] - line_a[1][0])
        intercept_a = (line_a[1][1] * line_a[0][0] - line_a[0][1] * line_a[1][0]) / (line_a[0][0] - line_a[1][0])
        cross_y = int(slope_a * cross_x + intercept_a)

        return [cross_x, cross_y]

    # Line equation: y = slope * x + intercept
    slope_a = (line_a[0][1] - line_a[1][1]) / (line_a[0][0] - line_a[1][0])
    intercept_a = (line_a[1][1] * line_a[0][0] - line_a[0][1] * line_a[1][0]) / (line_a[0][0] - line_a[1][0])

    slope_b = (line_b[0][1] - line_b[1][1]) / (line_b[0][0] - line_b[1][0])
    intercept_b = (line_b[1][1] * line_b[0][0] - line_b[0][1] * line_b[1][0]) / (line_b[0][0] - line_b[1][0])

    if slope_a == slope_b:
        return [None, None]

    cross_x = int((intercept_b - intercept_a) / (slope_a - slope_b))
    cross_y = int((slope_a * intercept_b - slope_b * intercept_a) / (slope_a - slope_b))

    return [cross_x, cross_y]


def get_anchor_lines(pts, quantity=4):
    point_num = len(pts)
    square_dists = []

    for i in range(point_num):
        dist = np.sum(np.square(pts[i] - pts[(i + 1) % point_num]))
        square_dists.append(dist)

    sorted_dist_indexes = sorted(range(len(square_dists)), key=lambda k: square_dists[k], reverse=True)[:quantity]

    anchor_lines = []
    anchor_dists = []
    for i in range(point_num):
        if i in sorted_dist_indexes:
            point_A = (pts[i][0], pts[i][1])
            point_B = (pts[(i + 1) % point_num][0], pts[(i + 1) % point_num][1])

            anchor_lines.append((point_A, point_B))
            anchor_dists.append(square_dists[i])

    return anchor_lines, anchor_dists


