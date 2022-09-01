#!/usr/bin/env python3

# Draw SVG templates of EVA foam cutouts to cover Hammond aluminum cases.
# Copyright 2022 Jason Pepas.
# Released under the terms of the MIT license.
# See https://opensource.org/licenses/MIT

import sys
import subprocess

# This uses drawSvg, see https://github.com/cduck/drawSvg
# brew install cairo
# pip3 install drawSvg
import drawSvg


# Global config:

g_cases = {
    # Tuple format: (name, top_len, top_width, bottom_len, bottom_width, height, notch)
    "1590B": ("Hammond 1590B", 112.4, 60.5, 110.7, 58.7, 31.1, 10),
    "1590B-tayda": ("Hammond 1590B (Tayda clone)", 112.4, 60.4, 110.4, 58.7, 31.1, 10),
    "1590BB": ("Hammond 1590BB", 119.9, 94.3, 117.0, 91.5, 34.1, 10),
    "1590BB-tayda": ("Hammond 1590BB (Tayda clone)", 120.2, 95.0, 118.9, 93.7, 37.3, 10),
    "1590Y": ("Hammond 1590Y", 92.2, 92.2, 90.0, 90.0, 41.8, 10),
    "1550P": ("Hammond 1550P", 80.2, 55.0, 79.4, 54.4, 25.4, 10),
    "1590A-tayda": ("Hammond 1590A (Tayda clone)", 92.4, 38.3, 91.4, 37.3, 31.1, 10),
}

g_foam_thick = 6  # "Hobby EVA foam" on Amazon.com is 6mm thick.

g_dpi = 600  # The DPI which you will be printing at.
g_fudge = 1.0  # Global correction scaling factor.
# g_fudge = 1.0045  # Correction factor if you printer is lame like mine.


# Unit conversions:

def in_to_mm(inches):
    return inches * 25.4

def mm_to_in(mm):
    return mm / 25.4

def in_to_px(inches):
    return inches * g_dpi * g_fudge

def mm_to_px(mm):
    return in_to_px(mm_to_in(mm))

# Global state:
g_size_mm = (in_to_mm(7.5), in_to_mm(10))
g_position_mm = (0, 0)
g_pen_is_down = False

g_drawing = drawSvg.Drawing(
    mm_to_px(g_size_mm[0]),
    mm_to_px(g_size_mm[1])
)


# Coordinate translation:

def flip_y(y):
    return g_size_mm[1] - y

def flip_dy(dy):
    return -(dy)

def bottom():
    return g_size_mm[1]


# Low-level drawing functions:

def pen_down():
    global g_pen_is_down
    g_pen_is_down = True

def pen_up():
    global g_pen_is_down
    g_pen_is_down = False

def move(dx, dy):
    global g_pen_is_down
    global g_position_mm
    if g_pen_is_down:
        draw_line(g_position_mm[0], g_position_mm[1], dx, dy)
    g_position_mm = (g_position_mm[0] + dx, g_position_mm[1] + dy)

def warp(x, y):
    global g_position_mm
    g_position_mm = (x, y)

def text(content, align_right=False):
    font_size = 12
    if align_right:
        g_drawing.append(
            drawSvg.Text(
                content,
                font_size * g_dpi / 72 * g_fudge,
                mm_to_px(g_position_mm[0]),
                mm_to_px(flip_y(g_position_mm[1])),
                text_anchor="end"
            )
        )
    else:
        g_drawing.append(
            drawSvg.Text(
                content,
                font_size * g_dpi / 72 * g_fudge,
                mm_to_px(g_position_mm[0]),
                mm_to_px(flip_y(g_position_mm[1]))
            )
        )

# High-level drawing functions:

def draw_line(origin_x, origin_y, dx, dy):
    g_drawing.append(
        drawSvg.Line(
            mm_to_px(origin_x),
            mm_to_px(flip_y(origin_y)),
            mm_to_px(origin_x + dx),
            mm_to_px(flip_y(origin_y) + flip_dy(dy)),
            stroke='black',
            stroke_width=2,
            fill='none'
        )
    )

def draw_box(w, h):
    pen_down()
    move(w, 0)
    move(0, h)
    move(-w, 0)
    move(0, -h)
    pen_up()

def draw_ruler():
    warp(5, bottom() - 12)
    text("14cm Ruler")
    warp(5 + 140, bottom() - 12)
    text("github.com/hammond-foam", align_right=True)
    warp(5, bottom() - 10)
    for _ in range(14):
        draw_box(10, 5)
        move(10, 0)


# Top:

def get_top_bounds_h(case):
    (desc, top_len, top_width, bottom_len, bottom_width, height, notch) = g_cases[case]
    w = top_len + g_foam_thick * 2
    h = top_width + g_foam_thick * 2
    return (w, h)

def draw_top_h(x, y, case):
    (desc, top_len, top_width, bottom_len, bottom_width, height, notch) = g_cases[case]
    warp(x, y)
    move(g_foam_thick + notch, 0)
    pen_down()
    move(top_len - notch - notch, 0)
    move(0, g_foam_thick + notch)
    move(g_foam_thick + notch, 0)
    move(0, top_width - notch - notch)
    move(-(g_foam_thick + notch), 0)
    move(0, g_foam_thick + notch)
    move(-(top_len - notch - notch), 0)
    move(0, -(g_foam_thick + notch))
    move(-(g_foam_thick + notch), 0)
    move(0, -(top_width - notch - notch))
    move(g_foam_thick + notch, 0)
    move(0, -(g_foam_thick + notch))
    pen_up()


# End caps:

def get_end_bounds_h(case):
    (desc, top_len, top_width, bottom_len, bottom_width, height, notch) = g_cases[case]
    w = top_width + g_foam_thick * 2
    h = height
    return (w, h)

def draw_end_h(x, y, case):
    (desc, top_len, top_width, bottom_len, bottom_width, height, notch) = g_cases[case]
    warp(x, y)
    pen_down()
    move(top_width + g_foam_thick * 2, 0)
    move(-((top_width - bottom_width) / 2), height)
    move(-(bottom_width + g_foam_thick * 2), 0)
    move(-((top_width - bottom_width) / 2), -height)
    pen_up()


# Sides:

def get_side_bounds_h(case):
    (desc, top_len, top_width, bottom_len, bottom_width, height, notch) = g_cases[case]
    w = top_len + g_foam_thick * 2
    h = height
    return (w, h)

def draw_side_h(x, y, case):
    (desc, top_len, top_width, bottom_len, bottom_width, height, notch) = g_cases[case]
    warp(x, y)
    pen_down()
    move(top_len + g_foam_thick * 2, 0)
    move(-((top_len - bottom_len) / 2), height)
    move(-(bottom_len + g_foam_thick * 2), 0)
    move(-((top_len - bottom_len) / 2), -height)
    pen_up()


# Bottom:

def get_bottom_bounds_h(case):
    (desc, top_len, top_width, bottom_len, bottom_width, height, notch) = g_cases[case]
    w = bottom_len + g_foam_thick * 2
    h = bottom_width + g_foam_thick * 2
    return (w, h)

def draw_bottom_h(x, y, case, center_cutout=False):
    (desc, top_len, top_width, bottom_len, bottom_width, height, notch) = g_cases[case]
    warp(x, y)
    pen_down()
    move(bottom_len + g_foam_thick * 2, 0)
    move(0, bottom_width + g_foam_thick * 2)
    move(-(bottom_len + g_foam_thick * 2), 0)
    move(0, -(bottom_width + g_foam_thick * 2))
    if center_cutout:
        margin = 6  # additional inside margin
        warp(x + g_foam_thick + margin, y + g_foam_thick + margin)
        move(bottom_len - margin * 2, 0)
        move(0, bottom_width - margin * 2)
        move(-(bottom_len - margin * 2), 0)
        move(0, -(bottom_width - margin * 2))
    pen_up()


# Rendering to pages:

def start_drawing(case, page):
    global g_drawing
    g_drawing = drawSvg.Drawing(
        mm_to_px(g_size_mm[0]),
        mm_to_px(g_size_mm[1])
    )
    warp(5, 10)
    desc = g_cases[case][0]
    text("EVA 6mm foam templates for %s, pg %s" % (desc, page))

def render(basename):
    g_drawing.saveSvg("%s.svg" % basename)
    cmd = "rsvg-convert -f pdf --dpi-x 600 --dpi-y 600 -o %s.pdf %s.svg" % (basename, basename)
    subprocess.check_call(cmd, shell=True)

def end_drawing(case, page):
    draw_ruler()
    render("%s_p%s" % (case, page))

def next_drawing(case, page):
    end_drawing(case, page)
    start_drawing(case, page+1)


# Main:

if __name__ == "__main__":
    case = "1590A-tayda"
    if len(sys.argv) > 1:
        case = sys.argv[-1]

    page = 1
    start_drawing(case, page)
    x = 5; y = 15

    top_bounds = get_top_bounds_h(case)
    end_bounds = get_end_bounds_h(case)
    side_bounds = get_side_bounds_h(case)
    bottom_bounds = get_bottom_bounds_h(case)

    draw_top_h(x, y, case)
    y += top_bounds[1] + 5

    if y + end_bounds[1] >= bottom() - 20:
        next_drawing(case, page); page += 1; y = 15
    draw_end_h(x, y, case)
    y += end_bounds[1] + 5

    if y + end_bounds[1] >= bottom() - 20:
        next_drawing(case, page); page += 1; y = 15
    draw_end_h(x, y, case)
    y += end_bounds[1] + 5

    if y + side_bounds[1] >= bottom() - 20:
        next_drawing(case, page); page += 1; y = 15
    draw_side_h(x, y, case)
    y += side_bounds[1] + 5

    if y + side_bounds[1] >= bottom() - 20:
        next_drawing(case, page); page += 1; y = 15
    draw_side_h(x, y, case)
    y += side_bounds[1] + 5

    if y + bottom_bounds[1] >= bottom() - 20:
        next_drawing(case, page); page += 1; y = 15
    draw_bottom_h(x, y, case, center_cutout=True)
    y += bottom_bounds[1] + 5

    if y + bottom_bounds[1] >= bottom() - 20:
        next_drawing(case, page); page += 1; y = 15
    draw_bottom_h(x, y, case, center_cutout=True)
    y += bottom_bounds[1] + 5

    if y + bottom_bounds[1] >= bottom() - 20:
        next_drawing(case, page); page += 1; y = 15
    draw_bottom_h(x, y, case)
    y += bottom_bounds[1] + 5

    end_drawing(case, page)
