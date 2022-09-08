
import bpy

from bpy.types import (
                        PropertyGroup,
                        Panel
                        )

from bpy.props import ( 
                        BoolProperty,
                        EnumProperty,
                        IntProperty,
                        FloatProperty,
                        StringProperty,
                        PointerProperty
                        )

def find_LSYS(self, context):
    return ( (t.name,t.name,t.name) for t in bpy.data.texts if t.name[:4] == 'LSYS')

def find_FOBS(self, context):
    return ( (obj.name,obj.name,obj.name) for obj in bpy.data.objects if 'LSYS_DATA' in obj)

class GLOBAL_UL_fractal_extruder_props(PropertyGroup):
    
    F_OBJ : PointerProperty(name="F_OBJ", type=bpy.types.Object)
    PATH_OBJ : PointerProperty(name="PATH_OBJ", type=bpy.types.Object)
    ITERATIONS : IntProperty(name="ITERATIONS", default=10, min = 1, options = {'HIDDEN'})
    skin : BoolProperty(name="skin", default=False, options = {'HIDDEN'})
    particle : BoolProperty(name="particle", default=False, options = {'HIDDEN'})
    add_fob : BoolProperty(name="add_fob", default=False, options = {'HIDDEN'})
    vgroup_size : BoolProperty(name="vgroup_size", default=False, options = {'HIDDEN'})

    F_TEX : PointerProperty(name="F_TEX", type=bpy.types.Image)
    renderPath : StringProperty( name="render path", subtype="FILE_PATH" )

    LSYS_DATA : EnumProperty(
        items=find_LSYS,
        name="LSYS_DATA",
        description="SELECT LSYS",
        default=None,
        update=None,
        get=None,
        set=None,
        options={'HIDDEN'})

    GEO : EnumProperty(
        items=[
            ('wire', "wire", ""),
            ('skin', "skin", ""),
            ],
        name="GEO",
        description="GEO",
        default='wire',
        options={'HIDDEN'})

    FOB : EnumProperty(
        items=find_FOBS,
        name="LSYS_FOBS",
        description="SELECT LSYS",
        default=None,
        update=None,
        get=None,
        set=None,
        options={'HIDDEN'})

    MODE : EnumProperty(
        items=[
            ('read fob', "use fob data", ""),
            ('read txt', "use txt data", ""),
            ('clear fob', "clear fob", ""),
            ],
        name="MODE",
        description="MODE",
        default='read fob',
        options={'HIDDEN'})

class VIEW3D_PT_fractal_extruder_tool(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "FREX"
    bl_label = "FRACTAL EXTRUDER"

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        con = context.scene.fractal_extruder_props

        layout.prop(con, "MODE", text="GROW MODE")
        layout.prop(con, "LSYS_DATA", text="TEXT DATA")

        layout.label(text='GENERATE')
        layout.operator("frex.add_fob", text="add fractal seed")
        if bpy.context.mode == 'EDIT_MESH':
            layout.prop(con, "F_OBJ", text="target FOB")
        layout.operator("frex.fractal_extruder", text="[BETA]multi_grow_seed").multi=True
        layout.operator("frex.fractal_extruder", text="grow_seed").multi=False

        layout.separator()

        layout.label(text='LSYS PAINTER (PIL required)')

        layout.prop(con, "F_TEX", text="target texture")
        row = layout.row()
        row.operator("frex.add_tex_fob", text="add tex gen")
        row.operator("image.new",  text="new image")
        layout.operator("frex.fractal_painter", text="draw texture (no update)").OPT = ''
        layout.operator("frex.fractal_painter", text="draw texture").OPT = 'U'

        layout.label(text='PNG SEQUENCE EXPORT')
        layout.prop(con, "renderPath", text="render path")
        layout.operator("frex.fractal_painter", text="export drawing sequence").OPT='UP'
        layout.operator("frex.fractal_painter", text="export iteration sequence").OPT='UR'
        
        layout.separator()

        layout.label(text='SETTINGS')
        layout.prop(con, "ITERATIONS", text="limit iters")
        layout.prop(con, "GEO", text="LSYS geo")
        layout.prop(con, "vgroup_size", text="vertex data")
        #layout.prop(con, "particle", text="gen particles obj")
        layout.prop(con, "PATH_OBJ", text="curve path")
        layout.separator()
        
        layout.label(text='UTILS')
        layout.operator("frex.set_line_art_vertex_map", text="set lineArt weigths")
        layout.operator("frex.set_geo_node_data", text="set geoNode data")
        layout.operator("frex.fob_to_text", text="RESET FOB").mode='RESET'
        layout.operator("frex.fob_to_text", text="TXT TO FOB").mode='TextToFob'
        layout.operator("frex.fob_to_text", text="FOB TO TXT").mode='FobToText'

        layout.label(text='DOCS')
        layout.operator("frex.load_docs", text="syntax rules").mode='SYNTAX'
        layout.operator("frex.load_docs", text="sverchok script").mode='SV_SCRIPT'
        layout.operator("frex.load_docs", text="load example txts").mode='LOAD_EXAMPLES'



        
