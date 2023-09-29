import bpy, bmesh
from mathutils import Vector
from .FREX_ENGINE import FRACTALEX

from bpy.props import ( 
                        BoolProperty,
                        EnumProperty,
                        IntProperty,
                        FloatProperty,
                        StringProperty,
                        FloatVectorProperty
                        )



class FREX_OT_fractal_extruder(bpy.types.Operator):
    bl_idname = "frex.fractal_extruder"
    bl_label = "Fractal Extruder"
    bl_options = {'REGISTER', 'UNDO'}

    update : BoolProperty(name="UPDATE", default=True)
    
    multi : BoolProperty(name="multi", default=True)

    fractal_ID : StringProperty(name="ID", default='fractal_obj')

    axiom : StringProperty(name="AXIOM", default='FA')
    rule_1 : StringProperty(name="RULE", default="A:[&SFA]////[&SFA]////[&SFA]")
    rule_2 : StringProperty(name="RULE", default="")
    rule_3 : StringProperty(name="RULE", default="")
    rule_4 : StringProperty(name="RULE", default="")
    load : BoolProperty(name="LOAD", default=False)
    use_text : BoolProperty(name="use_text", default=False)
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
    #custom_input : FloatProperty(name="k_val", default=30.0)
    custom_input : FloatVectorProperty(name="g j k w", size=4, default = [1,1,1,1])
    
    show_rands : BoolProperty(name="random variables", default=False)
    show_curve : BoolProperty(name="use profile", default=False)

    extra_rules = []
    
    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if (obj and obj.type == 'MESH' and context.mode == 'EDIT_MESH'):
            return True
        if 'LSYS_DATA' in obj :
            return ( 'image_settings' not in obj['LSYS_DATA'] )
        #return (obj and obj.type == 'MESH' and context.mode == 'EDIT_MESH')

    def draw(self, context):
        box = self.layout
        #box = layout.box()
        box.prop(self, "axiom")
        box.prop(self, "rule_1")
        box.prop(self, "rule_2")
        box.prop(self, "rule_3")
        box.prop(self, "rule_4")
        #box.separator()
        row = box.row()
        row.prop(self, "iterations")
        row.prop(self, "update")
        row.prop(self,"RandSeed")
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
        
        if bpy.context.mode == 'EDIT_MESH':
            obj = bpy.context.object
            fob = bpy.context.scene.fractal_extruder_props.F_OBJ
        else:
            fob = bpy.context.object

        MODE =  bpy.context.scene.fractal_extruder_props.MODE

        if MODE == 'clear fob':
            self.axiom ="FA"
            self.rule_1 = "A:[&SFA]////[&SFA]////[&SFA]"
            self.rule_2 =""
            self.rule_3 =""
            self.rule_4 = ""
            self.angle = 30.0
            self.length =1
            self.scale = 0.8
            self.radius_scale =0.5
            self.min_angle = 0
            self.max_angle = 0
            self.min_len = 0
            self.max_len = 0
            self.iterations = 3
            self.area = 0.3
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
            
            self.extra_rules = []

            for k in LSD:
                if "rule_" in k:
                    r_i = int(k.split('_')[1])
                    if r_i > 4:
                        self.extra_rules.append(LSD[k])
            
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
            self.multi_action(context,True,True)
        else:
            self.action(context,True)

        return {'FINISHED'}

    def execute(self, context):
        
        if self.multi:
            #bm = bmesh.new()
            #fob = bpy.context.scene.fractal_extruder_props.F_OBJ
            #bm.to_mesh(fob.data)
            self.multi_action(context,False,False)


        else:
            self.action(context, False)

        return {'FINISHED'}


    def action(self, context, invoked):
        if not self.update:
            return ['CANCELLED'] 

        if context.mode == 'EDIT_MESH':
            obj = bpy.context.edit_object
            me = obj.data
            bm = bmesh.from_edit_mesh(me)

            sel = set([f for f in bm.faces if f.select])

            direction=Vector()
            wpos=Vector()
            area=0
            fn=0
            for f in sel: 
                direction+=f.normal
                wpos+=f.calc_center_median()
                area+=f.calc_area()
                fn+=1

            direction.normalize()
            wpos/=fn

            ROOT = (direction,wpos,area)

        else:
            ROOT = ( (0,0,1),(0,0,0),1 )

        FRACTALEX(
            ROOT, self.axiom, self.extra_rules,
            self.rule_1,self.rule_2,self.rule_3,self.rule_4,
            self.angle, self.length,self.scale, self.radius_scale, 
            self.min_angle, self.max_angle, self.min_len, self.max_len, 
            self.iterations, self.area, self.prof_x, self.multi, 
            self.custom_input, invoked, self.RandSeed)


    def multi_action(self, context, get_roots, invoked):
        fob = bpy.context.scene.fractal_extruder_props.F_OBJ
        #if 'frex_roots_data' not in fob.data:
            #fob.data['frex_roots_data']=[]
        bm = bmesh.new()
        bm.to_mesh(fob.data)
        
        #if context.mode != 'EDIT_MESH':
            #return ['CANCELLED'] 
        
        if get_roots and context.mode == 'EDIT_MESH':
            #fob['frex_roots_data']=[]

            obj = bpy.context.edit_object
            me = obj.data
            bm = bmesh.from_edit_mesh(me)

            F = set([f for f in bm.faces if f.select])

            multi_sel = []

            bpy.ops.mesh.hide(unselected=True)
            bpy.ops.mesh.select_all(action='DESELECT')

            while len(F)!=0:
                f = F.pop()
                f.select=True
                
                bpy.ops.mesh.select_linked(delimit={'NORMAL'})  
                f_group=set([f for f in bm.faces if f.select])
                multi_sel.append(f_group)
                F=F-f_group
                bpy.ops.mesh.hide(unselected=False)

            bpy.ops.mesh.reveal()
            
            ROOTS=[]

            for i,sel in enumerate(multi_sel):
                if len(sel)==0: continue

                direction=Vector()
                wpos=Vector()
                area=0
                fn=0
                for f in sel: 
                    direction+=f.normal
                    wpos+=f.calc_center_median()
                    area+=f.calc_area()
                    fn+=1

                direction.normalize()
                wpos/=fn

                ROOTS.append( 
                    (direction[0], direction[1], direction[2],
                     wpos[0], wpos[1], wpos[2],
                     area) )
            
            fob['frex_roots_data'] = ROOTS
            bpy.ops.mesh.select_all(action='DESELECT')

        elif not 'frex_roots_data' in fob:
            return ['CANCELLED'] 
        bpy.ops.object.mode_set(mode='EDIT')  
        for R in fob['frex_roots_data']:
            ROOT = ( Vector((R[0], R[1], R[2])) , Vector((R[3], R[4], R[5])), R[6] )
            FRACTALEX(
                ROOT, self.axiom, self.extra_rules,
                self.rule_1,self.rule_2,self.rule_3,self.rule_4,
                self.angle, self.length,self.scale, self.radius_scale, 
                self.min_angle, self.max_angle, self.min_len, self.max_len, 
                self.iterations, self.area, self.prof_x, self.multi, 
                self.custom_input, invoked, self.RandSeed)
