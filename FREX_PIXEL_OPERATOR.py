import bpy, bmesh
from mathutils import Vector
from . FREX_PIXEL_ENGINE import FRACTALEX
from . FREX_TEXTURIZER import ImageEditor, ColorToFloat

from bpy.props import ( 
                        BoolProperty,
                        EnumProperty,
                        IntProperty,
                        FloatProperty,
                        StringProperty,
                        FloatVectorProperty,
                        IntVectorProperty
                        )


class FREX_OT_fractal_painter(bpy.types.Operator):
    bl_idname = "frex.fractal_painter"
    bl_label = "Fractal Painter"
    bl_options = {'REGISTER', 'UNDO'}

    OPT : StringProperty(name="OPT", default='U')#U update R render
    multi : BoolProperty(name="multi", default=True)

    fractal_ID : StringProperty(name="ID", default='fractal_obj')

    axiom : StringProperty(name="AXIOM", default='FA')
    rule_1 : StringProperty(name="RULE", default="A:[&SFA]////[&SFA]////[&SFA]")
    rule_2 : StringProperty(name="RULE", default="")
    rule_3 : StringProperty(name="RULE", default="")
    rule_4 : StringProperty(name="RULE", default="")

    update : BoolProperty(name="UPDATE", default=True)
    resize : FloatProperty(name="resize", default=1,min=0.1)

    angle : FloatProperty(name="ANGLE", default=30.0)
    length : FloatProperty(name="LENGTH", default=1, min=0.00001)
    scale : FloatProperty(name="LENGTH_SCALE", default=0.8, min=0.01)
    area : FloatProperty(name="RADIUS", default=0.3, min=0.00001)
    radius_scale : FloatProperty(name="RADIUS_SCALE", default=0.5, min=0)
    min_angle : FloatProperty(name="MIN ANGLE -", default=0,min=0)
    max_angle : FloatProperty(name="MAX ANGLE +", default=0,min=0)
    min_len : FloatProperty(name="MIN LENGTH -", default=0,min=0)
    max_len : FloatProperty(name="MAX LENGTH +", default=0,min=0)
    iterations : IntProperty(name="iterations", default=3, min=1)
    prof_x : FloatProperty(name="prof_x", default=1, min=0.01)
    RandSeed : IntProperty(name="SEED", default=0, min=0)
    
    image_settings : IntVectorProperty(name="W H x y", size=4, default = [1024,1024,512,512])
    blur : IntProperty(name="blur", default=0, min=0)
    caps : FloatProperty(name="caps", default=0, min=0)
    
    C1 : bpy.props.FloatVectorProperty(
        name = "C1",
        subtype = "COLOR",
        size = 4,
        default = [1.0,1.0,1.0,1.0],
        min=0.0,
        max=1.0,
        precision=2
    )
    C2 : bpy.props.FloatVectorProperty(
        name = "C2",
        subtype = "COLOR",
        size = 4,
        default = [1.0,1.0,1.0,1.0],
        min=0.0,
        max=1.0
    )
    C3 : bpy.props.FloatVectorProperty(
        name = "C3",
        subtype = "COLOR",
        size = 4,
        default = [1.0,1.0,1.0,1.0],
        min=0.0,
        max=1.0
    )
    C4 : bpy.props.FloatVectorProperty(
        name = "C4",
        subtype = "COLOR",
        size = 4,
        default = [1.0,1.0,1.0,1.0],
        min=0.0,
        max=1.0
    )

    custom_input : FloatVectorProperty(name="g j k w", size=4, default = [1,1,1,1])
    
    show_rands : BoolProperty(name="random variables", default=False)
    show_curve : BoolProperty(name="use profile", default=False)
    
    extra_rules = []
    
    def __init__(self):
        self.imageName = None

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if ( 'LSYS_DATA' in obj ):
            return ( 'image_settings' in obj['LSYS_DATA'] )
        #return (obj and obj.type == 'MESH' and context.mode == 'EDIT_MESH')

    def draw(self, context):
        box = self.layout
        #box = layout.box()
        row = box.row()
        row.prop(self, "update", text="AUTO_UPDATE")
        row.prop(self, "resize", text="scale res")
        
        row = box.row()
        row.prop(self, "image_settings")
        row = box.row()
        row.prop(self, "blur")
        row.prop(self, "caps")
        row.prop(self,"RandSeed")
        row = box.row()
        row.prop(self, "C1")
        row.prop(self, "C2")
        row.prop(self, "C3")
        row.prop(self, "C4")

        box.prop(self, "axiom")
        box.prop(self, "rule_1")
        box.prop(self, "rule_2")
        box.prop(self, "rule_3")
        box.prop(self, "rule_4")
        #box.separator()
        box.prop(self, "iterations")
        box.prop(self, "angle")
        box.prop(self, "length")
        box.prop(self, "scale")
        box.prop(self, "area")
        box.prop(self, "radius_scale")
        #box.prop(self,"custom_input")
        row = box.row()
        row.prop(self,"custom_input")
        #box.separator()
        if not self.show_rands:
            box.prop(self, "show_rands", text="show random variables", icon="TRIA_DOWN")
        if self.show_rands:
            box.prop(self, "show_rands", text="hide random variables", icon="TRIA_UP")
            box.prop(self, "min_angle")
            box.prop(self, "max_angle")
            box.prop(self, "min_len")
            box.prop(self, "max_len")
        #box.separator()
        if not self.show_curve:
            box.prop(self, "show_curve", text="show profile", icon="TRIA_DOWN")
        if self.show_curve:
            box.prop(self, "show_curve", text="hide profile", icon="TRIA_UP")
            box.prop(self, "prof_x")
            tool_settings = context.tool_settings
            box.template_curveprofile(tool_settings,"custom_bevel_profile_preset")        
        
    def invoke(self, context, event):
        print ( 'FREX ENGINE INVOKED')
        try:
            import PIL
            print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
            print('PIL INSTALLED')
        except:
            print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
            print('PIL NOT INSTALLED')

        self.update = True if 'U' in self.OPT else False

        if 'R' in self.OPT:
            self.multi = True
            RENDER_PATH =  bpy.context.scene.fractal_extruder_props.renderPath
            RENDER_PATH = bpy.path.abspath(RENDER_PATH)
        else: 
            self.multi = False

        self.resize = 1
        fob = bpy.context.object
        self.imageName = fob.name
        MODE =  bpy.context.scene.fractal_extruder_props.MODE


        if MODE == 'clear fob':
            self.image_settings = (512,512,256,512)
            self.blur = 1
            self.caps = 3
            self.C1 = (0,0,0,255)
            self.C2 = (255,0,0,255)
            self.C3 = (0,255,0,255)
            self.C4 = (0,0,255,255)
            self.axiom ="FA"
            self.rule_1 = "A:[&V+2;SFA]////[&V+3;SFA]////[&V+4;SFA]"
            self.rule_2 =""
            self.rule_3 =""
            self.rule_4 = ""
            self.angle = 30.0
            self.length = 150
            self.scale = 0.8
            self.radius_scale = 0.6
            self.min_angle = 0
            self.max_angle = 0
            self.min_len = 0
            self.max_len = 0
            self.iterations = 4
            self.area = 24
            self.prof_x = 1

            if 'FREX_PROFILE_DATA' in fob:
                del fob['FREX_PROFILE_DATA']

            if 'FREX_CUSTOM_INPUT' in fob:
                del fob['FREX_CUSTOM_INPUT']   

        else:

            if 'FREX_PROFILE_DATA' in fob:
                from . utils_profile import BWProfManager
                bw_prof_data = BWProfManager()
                self.prof_x = bw_prof_data.load_from_obj_data(fob)
                
            if 'FREX_CUSTOM_INPUT' in fob:
                IN = fob['FREX_CUSTOM_INPUT']
                self.custom_input = [IN[0], IN[1], IN[2], IN[3]]

            if MODE == 'read fob': #LOAD FROM GLOBAL FOB
                LSD = eval( fob['LSYS_DATA'] )

            elif MODE == 'read txt':
                LSD = bpy.context.scene.fractal_extruder_props.LSYS_DATA
                LSD = "".join( [l.body for l in bpy.data.texts[LSD].lines] )
                LSD = eval( LSD )
                if 'image_settings' not in LSD:
                    LSD['image_settings'] = "(512,512,256,256)"
                    LSD['blur'] = 0
                    LSD['C1'] = "(255,255,255,255)"
                    LSD['C2'] = "(255,255,255,255)"
                    LSD['C3'] = "(255,255,255,255)"
                    LSD['C4'] = "(255,255,255,255)"  
                    LSD['caps'] = 0
            self.extra_rules = []

            for k in LSD:
                if "rule_" in k:
                    r_i = int(k.split('_')[1])
                    if r_i > 4:
                        self.extra_rules.append(LSD[k])
            
            self.image_settings = list(  map(int, LSD['image_settings'][1:-1].split(',')) )
            self.blur = LSD['blur']
            self.C1 = ColorToFloat( list(map(int,LSD['C1'][1:-1].split(','))) )
            self.C2 = ColorToFloat( list(map(int,LSD['C2'][1:-1].split(','))) )
            self.C3 = ColorToFloat( list(map(int,LSD['C3'][1:-1].split(','))) )
            self.C4 = ColorToFloat( list(map(int,LSD['C4'][1:-1].split(','))) )
            self.caps = LSD['caps']
            self.axiom = LSD['axiom']
            self.rule_1 = LSD['rule_1']
            if 'rule_2' in LSD: self.rule_2 = LSD['rule_2']
            else: self.rule_2 = ""
            if 'rule_3' in LSD:self.rule_3 = LSD['rule_3']
            else: self.rule_3 = ""
            if 'rule_4' in LSD:self.rule_4 = LSD['rule_4']
            else: self.rule_4 = ""
            self.angle = LSD['angle']
            self.length = LSD['length']
            self.scale = LSD['length_scale']
            self.radius_scale = LSD['radius_scale']
            self.min_angle = LSD['min_angle']
            self.max_angle = LSD['max_angle']
            self.min_len = LSD['min_len']
            self.max_len = LSD['max_len']
            self.iterations = LSD['iteration'] 
            self.area = LSD['radius']

        if self.multi:
            self.multiAction(context,True)
        else: 
            self.action(context,True)  
        
        return {'FINISHED'}

    def execute(self, context):
        
        if self.multi:
            self.multiAction(context,True)
        else: 
            self.action(context,True)  

        return {'FINISHED'}

    def action(self, context, invoked):
        if self.update:

            ROOT = 0

            FRACTALEX(
                ROOT, self.axiom, self.extra_rules,
                self.rule_1,self.rule_2,self.rule_3,self.rule_4,
                self.angle, self.length,self.scale, self.radius_scale, 
                self.min_angle, self.max_angle, self.min_len, self.max_len, 
                self.iterations, self.area, self.prof_x, self.multi, self.custom_input, invoked,
                self.imageName, self.blur, self.image_settings, self.caps,
                self.C1,self.C2,self.C3,self.C4,
                self.resize, self.OPT, self.RandSeed )


    def multiAction(self, context, invoked):

        ROOT = 1

        for i in range(self.iterations):

            FRACTALEX(
                ROOT, self.axiom, self.extra_rules,
                self.rule_1,self.rule_2,self.rule_3,self.rule_4,
                self.angle, self.length,self.scale, self.radius_scale, 
                self.min_angle, self.max_angle, self.min_len, self.max_len, 
                i+1, self.area, self.prof_x, self.multi, self.custom_input, invoked,
                self.imageName, self.blur, self.image_settings, self.caps,
                self.C1,self.C2,self.C3,self.C4,
                self.resize, self.OPT, self.RandSeed )
            
            ROOT += 1