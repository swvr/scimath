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

fig = plt.figure(figsize=(8, 5))
gs = gridspec.GridSpec(1, 2, width_ratios=[3, 1]) 
ax0 = plt.subplot(gs[0])
ax1 = plt.subplot(gs[1])

# ----------

# a is the radius along the x-axis (sometimes shown as h)
# b is the radius along the y-axis (sometimes shown as v)
# outside ellipse
a1=6.5
b1=6.0
# inner rotated ellipse
a2=6.0
b2=5.0
# angles
T=20  # inner ellipse rotation angle
lT=45 # line of intersection angle

# ----------

# check for obvious issues
def check_for_issues():
    if T == 90 and a2 == b1:
        sys.stderr.write("WARNING: " + 
            "The horizontal and vertical radii are equal and " +
            "will result in a divide by zero runtime error." + os.linesep)


check_for_issues()

# ----------

# plot a line at set angle
# return y
def fx(x, t):
    trad = math.radians(t)
    return math.tan(trad)*x

vectfx = np.vectorize(fx, excluded='x')

x1 = np.arange(-8.0, 9.0, 1.0)
ax0.plot(x1, fx(x1, lT), color='red')

# ----------

# rational representation: https://en.wikipedia.org/wiki/Ellipse
# Display the inner ellipse before it's rotated
# This method was used just for fun.
def rrx(u, a):
    x = a * (1 - u**2) / (u**2 + 1)
    return x

def rry(u, b):
    y = (2*b*u) / (u**2 + 1)
    return y

u = np.arange(-1000, 1000, 0.1)
ax0.plot(rrx(u, a2), rry(u, b2), color='lightgray')

# ----------

# Standard parametric representation: https://en.wikipedia.org/wiki/Ellipse
def prx(t, a):
    return a * (math.cos(math.radians(t)))

def pry(t, b):
    return b * (math.sin(math.radians(t)))

vectprx = np.vectorize(prx, excluded='a')
vectpry = np.vectorize(pry, excluded='b')

t = np.arange(0, 360, 0.1)
ax0.plot(vectprx(t, a1), vectpry(t, b1), color='orange')

# ----------

# rotate ellipse
def rotatex(t, a, b, r):
    trad = math.radians(t)
    rrad = math.radians(r)
    x = (a * math.cos(trad) * math.cos(rrad)) - (b * math.sin(trad) * math.sin(rrad))
    return x

def rotatey(t, a, b, r):
    trad = math.radians(t)
    rrad = math.radians(r)
    y = (a * math.cos(trad) * math.sin(rrad)) + (b * math.sin(trad) * math.cos(rrad))
    return y

vectrotx = np.vectorize(rotatex, excluded=['a', 'b', 'r'])
vectroty = np.vectorize(rotatey, excluded=['a', 'b', 'r'])

t = np.arange(0, 360, 0.1)
ax0.plot(vectrotx(t, a2, b2, T), vectroty(t, a2, b2, T), color='blue')


# plot 2 points along the line of intersection

# ----------

# The intersection of a line and an ellipse
def lex(t, a, b):
    trad = math.radians(t)
    n=a**2 * b**2
    d=b**2 + (a**2 * math.tan(trad)**2)
    x = math.sqrt(n/d)
    # make sure we're in the right quadrant
    if lT > 90 and lT < 270:
        x*=-1
    return x

vectlex = np.vectorize(lex, excluded=['a', 'b'])

x=lex(lT, a1, b1)
y=fx(x, lT)
# should be a green dot on the orange ellipse intersecting the red line
ax0.plot(x, y, 'ro', color='green')

# ----------

# The intersection of line and rotated ellipse
# http://quickcalcbasic.com/ellipse%20line%20intersection.pdf
def lrex(t, a, b, r):
    trad = math.radians(t)
    rrad = math.radians(r)
    m = math.tan(trad)

    A = b**2 * (math.cos(rrad)**2 + 2 * m * math.cos(rrad) * math.sin(rrad) + m**2 * math.sin(rrad)**2) \
        + a**2 * (m**2 * math.cos(rrad)**2 - 2 * m * math.cos(rrad) * math.sin(rrad) + math.sin(rrad)**2)
    B = 0 # all drops out b/c b1=0 in y=mx+b1                                                                                                      
    C = -1 * a**2 * b**2
    # quadratic eq.
    x = (-1 * B + math.sqrt(B**2 - 4 * A * C)) / (2 * A)
    # make sure we're in the right quadrant
    if lT > 90 and lT < 270:
        x*=-1
    return x


    
vectlrex = np.vectorize(lrex, excluded=['a', 'b', 'r'])

x=lrex(lT, a2, b2, T)
y=fx(x, lT)
print ("%d,%d" % (x,y))
ax0.plot(x, y, 'ro', color='black')

# ----------

# calculate the difference between the two ellipses
t = np.arange(0, 360, 0.1)

xnorm=vectlex(t, a1, b1)
ynorm=vectfx(xnorm, t)

xrot=vectlrex(t, a2, b2, T)
yrot=vectfx(xrot, t)

# find the diff and when the inner is outside the outer ellipse preserve the sign
# (divide by zero is possible and should be caught)
vecthypot = np.vectorize(math.hypot)
diff = vecthypot(xnorm-xrot, ynorm-yrot) * ((xnorm-xrot) / abs(xnorm-xrot))

ax1.plot(t, diff, color='pink')

# ----------

ax0.set_aspect('equal', 'box')

plt.tight_layout()
plt.show()


#if __name__ == "__main__":
#    main()
