import bpy
#import bmesh
from mathutils.geometry import intersect_line_line_2d as intersect

def GetCurveProf(samples):

    P=[]

    bpy.context.tool_settings.custom_bevel_profile_preset.initialize(samples)
    bpy.context.tool_settings.custom_bevel_profile_preset.update()
    bp = bpy.context.tool_settings.custom_bevel_profile_preset
    
    step = 1/(samples-1)

    segs = [ (s.location.x,s.location.y) for s in bp.segments ]
    Y = 0
    for i in range(samples):
        for j in range(samples):
            if j == samples-1 : break
            
            a = segs[j]; 
            b = segs[j+1]
            
            #print ( (0,Y), (1,Y), a, b )
            if j == 0:
                p = intersect( (0,Y+0.0001), (1,Y+0.0001), a, b )
            elif j == samples-2:
                p = intersect( (0,Y-0.0001), (1,Y-0.0001), a, b )
            else:
                p = intersect( (0,Y), (1,Y), a, b )

            if p != None:
                x = p[0]
                break
            else:
                x = 0.1
        P.append(round(x,2))
        
        Y+=step    

    #P.reverse()
    #P.insert(0,(0,0,1))
    return P

class BWProfManager():

    def __init__(self):

        self.profile = bpy.context.tool_settings.custom_bevel_profile_preset
        self.points = []

    def reset(self, n ):

        while len(self.profile.points) > 2:
            self.profile.points.remove(self.profile.points[1]) 
        
        self.profile.points[0].location = (1,0.0)
        self.profile.points[-1].location = (0.0,1)

        self.profile.update()
        
        for i in range(n):
            self.profile.points.add( 1-i*0.1, 0.1+i*0.1) #,'AUTO', 'AUTO')


    def store_to_obj_data(self, obj, prof_x):

        self.profile.update()

        points = []
        reversed_points = [p for p in self.profile.points]

        for p in reversed_points[1:-1]:
            points.append( ( (p.location.x,p.location.y) , p.handle_type_1 , p.handle_type_2 ) )
        
        
        points.append(str(prof_x))
        obj['FREX_PROFILE_DATA'] = points

        #print('WRITE: ', obj['FREX_PROFILE_DATA'])
        self.profile.update()

    def flatten(self):
        for p in self.profile.points:
            p.select=False

        for p in self.profile.points:
            state = 'VECTOR'
            p.select=True
            p.handle_type_1 = state#'VECTOR'
            p.handle_type_2 = state#'VECTOR'

    def load_from_obj_data(self,obj):
        if not 'FREX_PROFILE_DATA' in obj:
            return False

        else: 

            POINTS = obj['FREX_PROFILE_DATA']
            #print('LOAD :', obj['FREX_PROFILE_DATA'])
            PROF_X = float( POINTS.pop() )
            self.reset(len(POINTS))
            self.flatten()

            for i,p in enumerate(POINTS):
                self.profile.points[i+1].select=True
                self.profile.points[i+1].location = (p[0][0] , p[0][1])
                self.profile.points[i+1].handle_type_1 = p[1]
                self.profile.points[i+1].handle_type_2 = p[2]
                self.profile.points[i+1].select=False
            
            #self.flatten()
            self.profile.update()

            return PROF_X



