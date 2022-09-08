from email import message
import bpy
from bpy.props import StringProperty
from . FREX_TEXTURIZER import *


class FREX_OT_WarningOperator(bpy.types.Operator):
    bl_idname = "frex.warning_operator"
    bl_label = "warning!"

    def execute(self,context):
        self.report({'ERROR'},'MESSAGE')
        return {'FINISHED'}


class FREX_OT_FobToText(bpy.types.Operator):
    """Fractal Object to text block"""
    bl_idname = "frex.fob_to_text"
    bl_label = "Fob to Text"
    bl_options = {'REGISTER', 'UNDO'}

    mode : StringProperty(name="mode", default='FobToText')

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        text_block = bpy.context.scene.fractal_extruder_props.LSYS_DATA
        text = bpy.data.texts[text_block]
        fob = context.object

        if not 'LSYS_DATA' in fob:
            self.report({'ERROR'}, "select the Fractal Object")
            return ['CANCELLED']

        if self.mode == 'FobToText':
            LSD = fob['LSYS_DATA'].replace(", '" , ",\n'")
            text.clear()
            text.write(LSD)
            self.report({'INFO'}, "Fob data written to "+text_block)

        elif self.mode == 'TextToFob':
            LSD = "".join( [l.body for l in text.lines] )
            LSD = eval(LSD)
            fob["LSYS_DATA"] = str(LSD)
            self.report({'INFO'}, text_block+" written do Fob data")

        elif self.mode == 'RESET' and 'image_settings' not in fob['LSYS_DATA']:
            LSD = {} 
            LSD['axiom']="FA"
            LSD['rule_1'] = "A:[&FSA]////[&FSA]////[&FSA]"
            LSD['angle']=30.0
            LSD['length']=1.0
            LSD['length_scale']=0.8
            LSD['radius']=0.3  
            LSD['radius_scale']=0.5
            LSD['min_angle']=0
            LSD['max_angle']=0
            LSD['min_len']=0
            LSD['max_len']=0
            LSD['iteration']=3    
            fob["LSYS_DATA"] = str(LSD)
            self.report({'INFO'}, "Fob data reset")

        elif self.mode == 'RESET' and 'image_settings' in fob['LSYS_DATA']:
            LSD['image_settings']="(256,256,128,256)"
            LSD['blur']= 0
            LSD['caps']= 1
            LSD['C1'] = "(1,1,1,1)"    
            LSD['C2'] = "(1,1,1,1)"   
            LSD['C3'] = "(1,1,1,1)"   
            LSD['C4'] = "(1,1,1,1)"   
            LSD['axiom']="FA"
            LSD['rule_1'] = "A:[&FSA]////[&FSA]////[&FSA]"
            LSD['angle']=30.0
            LSD['length']=60
            LSD['length_scale']=0.8
            LSD['radius']=8  
            LSD['radius_scale']=0.6
            LSD['min_angle']=0
            LSD['max_angle']=0
            LSD['min_len']=0
            LSD['max_len']=0
            LSD['iteration']=3
            fob["LSYS_DATA"] = str(LSD)
            self.report({'INFO'}, "Fob data reset")

        return {'FINISHED'}

def find_LSYS(self, context):
    return ( (t.name,t.name,t.name) for t in bpy.data.texts if t.name[:4] == 'LSYS')

def find_FOBS(self, context):
    return ( (obj.name,obj.name,obj.name) for obj in bpy.data.objects if 'LSYS_DATA' in obj)

class FREX_OT_AddFob(bpy.types.Operator):
    """Add an empty Fractal Object"""
    bl_idname = "frex.add_fob"
    bl_label = "Add Fractal Obj"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        self.AddFob(context)
        return {'FINISHED'}


    def AddFob(self,context):
        mesh = bpy.data.meshes.new("mesh")
        fob = bpy.data.objects.new("fractal_obj", mesh)
        context.collection.objects.link(fob)  

        LSD = {}  #Lyndermayer System Data

        LSD['axiom']="FA"
        LSD['rule_1'] = "A:[&FSA]////[&FSA]////[&FSA]"
        LSD['angle']=30.0
        LSD['length']=1.0
        LSD['length_scale']=0.8
        LSD['radius']=0.3  
        LSD['radius_scale']=0.5
        LSD['min_angle']=0
        LSD['max_angle']=0
        LSD['min_len']=0
        LSD['max_len']=0
        LSD['iteration']=3    
    
        fob["LSYS_DATA"] = str(LSD)


class FREX_OT_AddTexFob(bpy.types.Operator):
    """Add an empty Fractal Texture Generator"""
    bl_idname = "frex.add_tex_fob"
    bl_label = "Add Fractal Image Generator"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        self.AddFob(context)
        return {'FINISHED'}

    def AddFob(self,context):
        fob = bpy.data.objects.new( "LSYS_texture", None )
        context.scene.collection.objects.link( fob )
        fob.empty_display_size = 1
        fob.empty_display_type = 'CUBE'   

        #img = bpy.data.images.new( 'LSYS_texture', 256, 256 )

        LSD = {}  #Lyndermayer System Data
        
        LSD['image_settings']="(512,512,256,512)"
        LSD['blur']= 1
        LSD['caps']= 3
        LSD['C1'] = "(0,0,0,255)"    
        LSD['C2'] = "(255,0,0,255)"   
        LSD['C3'] = "(0,255,0,255)"   
        LSD['C4'] = "(0,0,255,255)"   
        LSD['axiom']="FA"
        LSD['rule_1'] = "A:[&V+2;SFA]////[&V+3;SFA]////[&V+4;SFA]"
        LSD['angle']=30.0
        LSD['length']=150.0
        LSD['length_scale']=0.8
        LSD['radius']=24
        LSD['radius_scale']=0.6
        LSD['min_angle']=0
        LSD['max_angle']=0
        LSD['min_len']=0
        LSD['max_len']=0
        LSD['iteration']=4
        fob["LSYS_DATA"] = str(LSD)


class Cursor():
    
    def __init__(self,curve):
        
        self.points = curve.data.splines[0].points
        self.sample = 0.0
        self.curve_pos = curve.matrix_world.translation

        if not "LSYS_CURSOR_CTRL" in bpy.data.objects:
            self.cursor = bpy.data.objects.new("LSYS_CURSOR_CTRL",None)
            #bpy.context.scene.collection.objects.link(self.cursor)
            #bpy.context.collection.objects.link(self.cursor)
        else:
            self.cursor = bpy.data.objects["LSYS_CURSOR_CTRL"]
        
        scene = bpy.context.scene
        if not self.cursor.name in scene.collection.objects:
            scene.collection.objects.link(self.cursor)

        self.cursor.location = (0,0,0) #points[0].co[0:3]
        self.cursor.empty_display_type = 'ARROWS'
        for constraint in self.cursor.constraints:
            self.cursor.constraints.remove(constraint)

        self.f_mod = self.cursor.constraints.new(type='FOLLOW_PATH')
        self.f_mod.target = curve
        self.f_mod.use_fixed_location = True
        self.f_mod.use_curve_follow = True
        self.f_mod.use_curve_radius = True
        self.f_mod.forward_axis = 'FORWARD_Z'
        self.f_mod.up_axis = 'UP_X'
        self.f_mod.offset_factor = 0
        


    def evaluate(self):
        self.f_mod.offset_factor = self.sample
        bpy.context.view_layer.update()
        return self.cursor.matrix_world.translation.copy() - self.curve_pos

    def get_axis(self,axis):
        from mathutils import Vector
        bpy.context.view_layer.update()
        m = self.cursor.matrix_world
        if axis == 'X':
            axis = Vector((m[0][0],m[1][0],m[2][0]))
        elif axis == 'Y':
            axis = Vector((m[0][1],m[1][1],m[2][1]))
        elif axis == 'Z':
            axis = Vector((m[0][2],m[1][2],m[2][2]))
            
        return axis

    def remove(self):
        
        bpy.data.objects.remove( self.cursor , do_unlink=True)   



class FREX_OT_SetLineArtVertexMap(bpy.types.Operator):
    """Line art FREX setup"""
    bl_idname = "frex.set_line_art_vertex_map"
    bl_label = "Fob to Text"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        obj = bpy.context.object
        if not  obj.type == 'GPENCIL':
            bpy.ops.object.gpencil_add(type='LRT_OBJECT')
            obj = bpy.context.object


        if "FREX_radius" in obj.vertex_groups:
            FREX_radius = obj.vertex_groups.get("FREX_radius")
            obj.vertex_groups.remove(FREX_radius) 

        FREX_radius = obj.vertex_groups.new( name = "FREX_radius" )

        obj.grease_pencil_modifiers["Line Art"].source_vertex_group = "FREX_radius"
        obj.grease_pencil_modifiers["Line Art"].chaining_image_threshold = 0

        bpy.ops.object.gpencil_modifier_add(type='GP_THICK')
        obj.grease_pencil_modifiers["Thickness"].vertex_group = "FREX_radius"

        return {'FINISHED'}


class FREX_OT_LOAD_DOCS(bpy.types.Operator):
    """load the syntax txt doc"""
    bl_idname = "frex.load_docs"
    bl_label = "Load DOC txt"
    bl_options = {'REGISTER', 'UNDO'}

    mode : StringProperty(name="mode", default='')

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        from os import path
        fname = ''
        if self.mode == "SYNTAX":
            fname = 'syntax.txt'
        elif self.mode == "SV_SCRIPT":
            fname = 'SV_FREX_05.py'
        elif self.mode == "LOAD_EXAMPLES":

            from . FREX_EXAMPLES import EXAMPLES
  
            for LSYS_NAME, DATA in EXAMPLES.items():
                
                if not 'LSYS_'+LSYS_NAME in bpy.data.texts:
                    txt = bpy.data.texts.new('LSYS_'+LSYS_NAME)
                    txt.write( str(DATA).replace(", '" , ",\n'") )

            return {'FINISHED'}

        else:
            return {'CANCELLED'}

        txt = path.join( path.dirname(__file__), fname )
        bpy.data.texts.load(txt)

        return {'FINISHED'}




class FREX_OT_set_geo_node_data(bpy.types.Operator):
    """s"""
    bl_idname = "frex.set_geo_node_data"
    bl_label = "set geo node"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):

        obj = bpy.context.object

        geoNodeMod = obj.modifiers.active

        if geoNodeMod.type == "NODES":

            inputs = geoNodeMod.node_group.inputs
            print ("FREX GEONODE SETTINGS")
            if "radius" not in inputs:
                inputs.new("NodeSocketFloat", "radius")
                id = inputs["radius"].identifier
                geoNodeMod[id+'_attribute_name'] = "FREX_radius"
                geoNodeMod[id+'_use_attribute'] = True
                
            if "iters" not in inputs:
                inputs.new("NodeSocketFloat", "iters")
                id = inputs["iters"].identifier
                geoNodeMod[id+'_attribute_name'] = "FREX_iters"
                geoNodeMod[id+'_use_attribute'] = True        

            if "tag" not in inputs:
                inputs.new("NodeSocketFloat", "tag")
                id = inputs["tag"].identifier
                geoNodeMod[id+'_attribute_name'] = "FREX_tag"
                geoNodeMod[id+'_use_attribute'] = True        

            if "id" not in inputs:
                i = inputs.new("NodeSocketFloat", "id")
                id = inputs["id"].identifier
                geoNodeMod[id+'_attribute_name'] = "FREX_id"
                geoNodeMod[id+'_use_attribute'] = True 

        return {'FINISHED'}
