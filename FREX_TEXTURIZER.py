import numpy as np
import bpy

def remap(a, minOut, maxOut):
    return np.interp(a, (a.min(), a.max()), (minOut, maxOut))

def RemapTo1(a):
    return np.interp(a, (0,255), (0, 1) )

def RemapTo255(a):
    return np.interp(a, (0,1) , (0, 255) )

def RemapColor(a):
    a = np.array(a)
    a = np.interp(a, (0, 1), (0, 255) )
    return (int(a[0]), int(a[1]), int(a[2]), int(a[3]) )

def ColorToFloat(a):
    a = np.array(a)
    a = np.interp(a, (0,255), (0, 1) )
    return (a[0], a[1], a[2], a[3] )

def write_BIMG(name,w,h):
    if name in bpy.data.images:
        BIMG = bpy.data.images[name]
    else:
        BIMG = bpy.data.images.new(name,w,h)

    return BIMG

class PilBimage():


    def __init__(self,name,W,H):
        self.grid = np.zeros( (H,W,4) , dtype=int)
        self.W = W
        self.H = H
        self.name = name
        self.BIMG = None
        from PIL import Image
        self.PIL_IMG = Image.new('RGBA', (W, H))
        self.pixels = None
        self.drawing = None

        
    def WriteToBIMG(self):
        self.BIMG.pixels = RemapTo1(self.grid.flatten()) #remap( self.grid.flatten(), 0, 1) 

    def SetBIMGData(self):
        if self.name in bpy.data.images:
            bpy.data.images.remove(bpy.data.images[self.name])

        self.BIMG = bpy.data.images.new( self.name, self.W, self.H )

    def GridFromData(self,tex_name):
        if tex_name in bpy.data.images:
            pixel_data = np.array(bpy.data.images[tex_name].pixels).reshape((self.H,self.W,4))
            self.grid = RemapTo255(pixel_data) #remap( pixel_data, 0, 255)
            
    def BimgToPilImg(self, tex_name):
        if tex_name in bpy.data.images:
            pixel_data = np.array(bpy.data.images[tex_name].pixels).reshape((self.H,self.W,4))
            pixel_data = RemapTo255(pixel_data) #remap( pixel_data, 0, 255)
            pixel_data = pixel_data.astype(int)
            self.UpdatePixels()
            for row in range(self.H):
                for x in range(self.W):
                   rgba = tuple(pixel_data[row][x])
                   self.pixels[x,row] = ( rgba )
            self.grid = np.asarray(self.PIL_IMG)

    def StartDraw(self):
        from PIL import ImageDraw
        self.drawing = ImageDraw.Draw(self.PIL_IMG)
                  
    def DrawText(self,txt, font="impact", size = 20, pos=(0,0), color=(0,0,255,200) ):
        from PIL import ImageFont
        fnt = ImageFont.truetype(font+".ttf", size)
        self.drawing.text( pos, txt, font = fnt, fill = color )          

    def UpdatePixels(self):
        self.pixels = self.PIL_IMG.load() 

    def PilImgToGrid(self):
        self.grid = np.asarray(self.PIL_IMG)[::-1]

    def DrawLine(self, A, B, fill=None, width=1, caps=False):
        #fill (R G B A)
        self.drawing.line( (A,B), fill, width, joint = "curve")
        if caps == 1:
            self.circle(A,width,fill); self.circle(B,width,fill)
        elif caps > 1:
            self.circle(A,width*caps,fill); self.circle(B,width*caps,fill)

            
    def Blur(self,val):
        from PIL import ImageFilter
        self.PIL_IMG = self.PIL_IMG.filter(ImageFilter.BoxBlur(val))
        self.UpdatePixels()

    def circle(self, cen, r, fill):
        r*=0.5
        self.drawing.ellipse((cen[0]-r+1, cen[1]-r+1, cen[0]+r-1, cen[1]+r-1), fill=fill, outline=None)

class ImageEditor():

    def LoadImage(self,name):
        for area in bpy.context.screen.areas:
            if area.type == 'IMAGE_EDITOR':
                area.spaces.active.image = bpy.data.images[name]


    def GetActiveImage(self):
        for area in bpy.context.screen.areas:
            if area.type == 'IMAGE_EDITOR':
                if 'LSYS' in area.spaces.active.image.name:
                    return area.spaces.active.image

'''
class FrexTex():

    def __init__(self,name,W,H):
        self.PIL_IMG = Image.new('RGBA', (W, H))

    def DrawLine(self):
        pass

    def WriteToBIMG(self):
        pass

'''