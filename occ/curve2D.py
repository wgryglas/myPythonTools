
from OCC.STEPControl import STEPControl_Reader
from OCC.IGESControl import IGESControl_Reader
from OCC.IFSelect import IFSelect_RetDone, IFSelect_ItemsByEntity
from OCC.TopExp import TopExp_Explorer
from OCC.TopoDS import topods, TopoDS_Shape
from OCC.TopAbs import TopAbs_EDGE
from OCC.gp import gp_Trsf, gp_Vec, gp_Ax1, gp_Ax2, gp_Dir
from OCC.Bnd import Bnd_Box
from OCC.GeomAdaptor import GeomAdaptor_Curve
from OCC.BRep import BRep_Tool
from OCC.BRepBndLib import brepbndlib_Add
from OCC.GCPnts import GCPnts_UniformDeflection
from OCC.BRepTools import breptools_Read
from OCC.BRep import BRep_Builder
from OCC.TopLoc import TopLoc_Location
from OCC.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCC.GProp import GProp_GProps
from OCC import BRepGProp
from OCC.gp import gp_Pnt
from wg.tools.function import assert_arg_iterable
import numpy as np
import os

class Bounds:
    def __init__(self, **kwargs):
        self.min = np.zeros(3)
        self.max = np.zeros_like(self.min)

        if 'min' in kwargs:
            self.min = np.array(kwargs['min'])

        if 'max' in kwargs:
            self.max = np.array(kwargs['max'])

    def size(self):
        return self.max - self.min

    def set_from_data(self, x, y, *args):
        if not args:
            self.min = np.array([min(x), min(y), 0])
            self.max = np.array([max(x), max(y), 0])
        else:
            self.min = np.array([min(x), min(y), min(args[0])])
            self.max = np.array([max(x), max(y), max(args[0])])
        return self

    def center(self):
        return self.min + 0.5*self.size()

    def __str__(self):
        return "Bounds ("+str(self.min[0])+", "+str(self.min[1])+", "+str(self.min[2])+"), ("+str(self.max[0])+", "+str(self.max[1])+", "+str(self.max[2])+"):\nsize="+str(self.size())



STEP = 'step'
IGES = 'iges'
BREP = 'brep'

def __import_step_iges__(fname, reader):
    status = reader.ReadFile(fname)
    if status == IFSelect_RetDone:  # check status
        ok = reader.TransferRoot(1)
        _nbs = reader.NbShapes()
        return reader.Shape(1)
    elif not os.path.isfile(fname):
        IOError("File "+fname+" does not exist")
    else:
        raise IOError("Can't import file "+fname)

def __import__brep__(fname):
    s = TopoDS_Shape()
    if breptools_Read(s, fname, BRep_Builder()):
        return s
    else:
        raise IOError("Can't import file "+fname)

__readers__ = {STEP: lambda name: __import_step_iges__(name,STEPControl_Reader()),
               IGES: lambda name: __import_step_iges__(name,IGESControl_Reader()),
               BREP: __import__brep__ }

def gp_Pnt2array(pnts):
    return np.array([pnts.X(), pnts.Y(), pnts.Z()])


def array2gp_Pnt(pnt):
    return gp_Pnt(pnt[0], pnt[1], pnt[2])

class Curves:
    def __init__(self, fname, type=STEP):
        self.valid = False
        try:
            self.shape=__readers__[type](fname)
            self.valid = True
        except KeyError:
            raise Exception("There is no "+type+" reader available, couldn't read geometry")

        self.__extract_curves()

    def __extract_curves(self):
        explorer = TopExp_Explorer()
        done = set()
        explorer.Init(self.shape, TopAbs_EDGE)
        self.curves = []
        while explorer.More():
            edge = topods.Edge(explorer.Current())

            if edge in done:
                continue
            else:
                done.add(edge)

            s_range = BRep_Tool.Range(edge)
            gc = BRep_Tool().Curve(edge)
            if gc:
                curve = GeomAdaptor_Curve(gc[0])
                self.curves.append(curve)
            else:
                raise Exception("Can't get curve from shape")

            explorer.Next()

    def translate(self, vec):
        tr = gp_Trsf()
        tr.SetTranslation(gp_Vec(*vec))
        loc = TopLoc_Location(tr)
        self.shape.Move(loc)
        self.__extract_curves()
        return self

    def rotate(self, angle, axis):
        ax = gp_Ax1(gp_Pnt(*axis[:3]), gp_Dir(*axis[3:]))
        tr = gp_Trsf()
        tr.SetRotation(ax, angle)
        loc = TopLoc_Location(tr)
        self.shape =  BRepBuilderAPI_Transform(self.shape, tr).Shape()
        self.__extract_curves()
        return self

    def scale(self, scale):
        tr = gp_Trsf()
        #tr.SetScale(gp_Pnt(*point), scale)
        tr.SetScaleFactor(scale)
        self.shape = BRepBuilderAPI_Transform(self.shape, tr).Shape()
        self.__extract_curves()
        return self


    def mirror(self, **kwargs):
        """
        params (one of):
           point  def. mirror about point
           axis
           plane
        """
        inValue=None

        if 'point' in kwargs:
            inValue = gp_Pnt(kwargs['point'])
        elif 'axis' in  kwargs:
            inValue = gp_Ax1(gp_Pnt(*kwargs['axis'][:3]), gp_Dir(*kwargs['axis'][3:]))
        elif 'plane' in kwargs:
            inValue = gp_Ax2(gp_Pnt(*kwargs['axis'][:3]), gp_Dir(*kwargs['axis'][3:]))
        else:
            print "Warning: mirror could not be done becase there was no parameters specified"
            return self

        tr = gp_Trsf()
        tr.SetMirror(inValue)
        self.shape = BRepBuilderAPI_Transform(self.shape, tr).Shape()
        self.__extract_curves()
        return self

    def isValid(self):
        return self.valid

    def center(self):
        props = GProp_GProps()
        BRepGProp.brepgprop_LinearProperties(self.shape, props)
        return gp_Pnt2array(props.CentreOfMass())

    def tesselatation(self, curveId=0, deflection=1e-3):
        curve = self.curves[curveId]
        deflector = GCPnts_UniformDeflection()
        deflector.Initialize(curve, deflection, 0., 1.)
        nbPts = deflector.NbPoints()
        x = np.zeros(nbPts)
        y = np.zeros(nbPts)
        z = np.zeros(nbPts)
        for i in range(1, nbPts+1):
            param = deflector.Parameter(i)
            pnt = gp_Pnt2array(curve.Value(param))
            x[i-1] = pnt[0]
            y[i-1] = pnt[1]
            z[i-1] = pnt[2]
        return (x, y, z)

    def nbCurves(self):
        return len(self.curves)

    def bounds(self):
        box = Bnd_Box()
        brepbndlib_Add(self.shape, box)
        coords=box.Get()
        return Bounds(min=coords[:3], max=coords[3:])


    @assert_arg_iterable(args=1, kwargs='parameter')
    def toPoint(self, parmeter, curveId=0):
        points = []
        curve = self.curves[curveId]
        for p in parmeter:
            points.append(gp_Pnt2array(curve.Value(parmeter)))
        return np.ravel(points)


    def toParameter(self, point, curveId=0):
        pass

    # def translate(self, pnt):
    #     #BRep_Tool.
    #     gp_Trsf()
    #     self.shape.Location(TopLoc_Location())
