import bpy
#from mathutils import Vector


def NewSpline( fcurve):
    spline = fcurve.splines.new(type='NURBS')
    return spline

def FixSpline(spline):
    spline.use_endpoint_u = True
    L = len(spline.points)
    if L >= 4:
        spline.order_u = 2
    else:
        spline.order_u = 2


def AddSplinePoint(spline,co,radius):
    spline.points.add()
    spline.points[-1].co = co
    spline.points[-1].radius = radius