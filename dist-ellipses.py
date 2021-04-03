#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (c) 2021 Scott Weaver

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

"""
Calculate the distance between two concentric ellipses, one of which has been rotated.
"""

import os
import sys
import math
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import gridspec

# ----------
# Default values

# a is the radius along the x-axis (sometimes shown as h)
# b is the radius along the y-axis (sometimes shown as v)
# first (the outside) ellipse
a1=6.5
b1=6.0
# second (inner) rotated ellipse
a2=6.0
b2=5.0
# angles
T=20  # inner ellipse rotation angle
lT=T  # line of intersection angle

# ----------

# check for obvious issues
def check_for_issues():
    if T == 90 and a2 == b1:
        sys.stderr.write("WARNING: " + 
            "The horizontal and vertical radii are equal and " +
            "will result in a divide by zero runtime error." + os.linesep)

# ----------

# Calculate y for a line passing through x at an angle t.
# This is for a line passing through the origin (0, 0).
# The angle t is in degrees.
def get_position_y_at_angle(x, t):
    trad = math.radians(t)
    return math.tan(trad)*x

def get_position_x_at_angle(y, t):
    trad = math.radians(t)
    return y / math.tan(trad)

# ----------

# rational representation: https://en.wikipedia.org/wiki/Ellipse
# This method was used just for fun.
# a: horizontal radius
def get_ellipse_x_rational(u, a):
    x = a * (1 - u**2) / (u**2 + 1)
    return x

# b: vertical radius
def get_ellipse_y_rational(u, b):
    y = (2*b*u) / (u**2 + 1)
    return y

# ----------

# Standard parametric representation: https://en.wikipedia.org/wiki/Ellipse
def get_ellipse_x_standard(t, a):
    return a * (math.cos(math.radians(t)))

def get_ellipse_y_standard(t, b):
    return b * (math.sin(math.radians(t)))

# ----------

# rotate ellipse
def get_ellipse_x_rotated(t, a, b, r):
    trad = math.radians(t)
    rrad = math.radians(r)
    x = (a * math.cos(trad) * math.cos(rrad)) - (b * math.sin(trad) * math.sin(rrad))
    return x

def get_ellipse_y_rotated(t, a, b, r):
    trad = math.radians(t)
    rrad = math.radians(r)
    y = (a * math.cos(trad) * math.sin(rrad)) + (b * math.sin(trad) * math.cos(rrad))
    return y

# ----------

# The intersection of a line and an ellipse
def get_line_ellipse_x_intercept_standard(t, a, b):
    # trad = math.radians(t)
    # n=a**2 * b**2
    # d=b**2 + (a**2 * math.tan(trad)**2)
    # x = math.sqrt(n/d)
    # # make sure we're in the right quadrant
    # if lT > 90 and lT < 270:
    #     x*=-1
    # return x
    return get_line_ellipse_x_intercept_rotated(t, a, b, 0)

# ----------

# The intersection of line and rotated ellipse (at the origin)
# http://quickcalcbasic.com/ellipse%20line%20intersection.pdf
def get_line_ellipse_x_intercept_rotated(t, a, b, r):
    trad = math.radians(t)
    rrad = math.radians(r)
    m = math.tan(trad)

    if t == 90 or r == 270:
        x = get_line_ellipse_y_intercept_rotated(t, a, b, r, 0)
    else:
        A = b**2 * (math.cos(rrad)**2 + 2 * m * math.cos(rrad) * math.sin(rrad) + m**2 * math.sin(rrad)**2) \
            + a**2 * (m**2 * math.cos(rrad)**2 - 2 * m * math.cos(rrad) * math.sin(rrad) + math.sin(rrad)**2)
        B = 0 # all drops out b/c b1=0 in y=mx+b1
        C = -1 * a**2 * b**2
        # quadratic eq.
        x = (-1 * B + math.sqrt(B**2 - 4 * A * C)) / (2 * A)

    # make sure we're in the correct quadrant
    if lT > 90 and lT <= 270:
        x*=-1
    return x

# ---------

def get_line_ellipse_y_intercept_rotated(t, a, b, r, x):
     rrad = math.radians(r)

     A = b**2 * math.sin(rrad)**2 + a**2 * math.cos(rrad)**2
     B = 2 * x * math.cos(rrad) * math.sin(b**2 - a**2)
     C = x**2 * (b**2 * math.cos(rrad)**2 + a**2 * math.sin(rrad)**2) - a**2 * b**2
     # quadratic eq.
     y = (-1 * B + math.sqrt(B**2 - 4 * A * C)) / (2 * A)
     return get_position_x_at_angle(y, t)

# --------

def main():
    
    check_for_issues()
    
    # setup the plot
    plt.figure(figsize=(8, 5))
    gs = gridspec.GridSpec(1, 2, width_ratios=[3, 1]) 
    ax0 = plt.subplot(gs[0])
    ax1 = plt.subplot(gs[1])
    
    ax0.set_title("Concentric Ellipses")
    ax1.set_title("Distance between Ellipses")
    ax1.set_xlabel("Degrees")

    ax0.set_xlim(-1*(a1+1), a1+1)
    ax0.set_ylim(-1*(b1+1), b1+1)

    # plot a line at set angle
    vect_get_position_y_at_angle = np.vectorize(get_position_y_at_angle, excluded='x')
    x1 = np.arange(-1*a1, a1+1, 1.0)
    ax0.plot(x1, vect_get_position_y_at_angle(x1, lT), color='red')
    
    # Display the second (inner) ellipse before it's rotated (just for fun)
    u = np.arange(-1000, 1000, 0.1)
    ax0.plot(get_ellipse_x_rational(u, a2), get_ellipse_y_rational(u, b2), color='lightgray')
    
    # plot the first ellipse (not rotated)
    vect_get_ellipse_x_standard = np.vectorize(get_ellipse_x_standard, excluded='a')
    vect_get_ellipse_y_standard = np.vectorize(get_ellipse_y_standard, excluded='b')
    t = np.arange(0, 360, 0.01)
    ax0.plot(vect_get_ellipse_x_standard(t, a1), vect_get_ellipse_y_standard(t, b1), color='orange')
    
    # plot the second ellipse, rotated
    vect_get_ellipse_x_rotated = np.vectorize(get_ellipse_x_rotated, excluded=['a', 'b', 'r'])
    vect_get_ellipse_y_rotated = np.vectorize(get_ellipse_y_rotated, excluded=['a', 'b', 'r'])
    t = np.arange(0, 360, 0.01)
    ax0.plot(vect_get_ellipse_x_rotated(t, a2, b2, T), vect_get_ellipse_y_rotated(t, a2, b2, T), color='blue')

    # plot 2 points along the line of intersection
    
    # plot the point of intersection with the first ellipse (not rotated)
    vect_get_line_ellipse_x_intercept_standard = np.vectorize(get_line_ellipse_x_intercept_standard, excluded=['a', 'b'])
    x=get_line_ellipse_x_intercept_standard(lT, a1, b1)
    y=get_position_y_at_angle(x, lT)
    print ("green: %f,%f" % (x,y))
    # should be a green dot on the orange ellipse intersecting the red line
    ax0.plot(x, y, 'ro', color='green')
    
    # plot the point of intersection with the second ellipse (rotated)
    vect_get_line_ellipse_x_intercept_rotated = np.vectorize(get_line_ellipse_x_intercept_rotated, excluded=['a', 'b', 'r'])
    x=get_line_ellipse_x_intercept_rotated(lT, a2, b2, T)
    y=get_position_y_at_angle(x, lT)
    print ("black: %f,%f" % (x,y))
    # should be a black dot on the blue ellipse intersecting the red line
    ax0.plot(x, y, 'ro', color='black')
    
    # ----------
    
    # calculate the difference between the two ellipses
    t = np.arange(0, 360, 0.1)
    
    xnorm=vect_get_line_ellipse_x_intercept_standard(t, a1, b1)
    ynorm=vect_get_position_y_at_angle(xnorm, t)
    
    xrot=vect_get_line_ellipse_x_intercept_rotated(t, a2, b2, T)
    yrot=vect_get_position_y_at_angle(xrot, t)
    
    # find the diff and when the inner is outside the outer ellipse preserve the sign
    # (divide by zero is possible and should be caught)
    vect_hypot = np.vectorize(math.hypot)
    diff = vect_hypot(xnorm-xrot, ynorm-yrot) * ((xnorm-xrot) / abs(xnorm-xrot))
    
    ax1.plot(t, diff, color='pink')
    
    # ----------
    
    ax0.set_aspect('equal', 'box')
    
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
