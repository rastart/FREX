# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name" : "FRACTAL_EXTRUDER",
    "author" : "Andrea -RaStart- Rastelli",
    "description" : "Lindenmayer system based extrusion",
    "blender" : (2, 90, 0),
    "version" : (0, 0, 5),
    "location" : "",
    "warning" : "IN DEVELOPMENT, USE WITH CAUTION",
    "category" : "Mesh"
}

import bpy
from . FREX_GUI import GLOBAL_UL_fractal_extruder_props
from . FREX_GUI import VIEW3D_PT_fractal_extruder_tool
from . FREX_OPERATOR import FREX_OT_fractal_extruder
from . FREX_UTILS import FREX_OT_AddFob
from . FREX_UTILS import FREX_OT_FobToText
from . FREX_UTILS import FREX_OT_SetLineArtVertexMap
from . FREX_UTILS import FREX_OT_LOAD_DOCS
from . FREX_PIXEL_OPERATOR import FREX_OT_fractal_painter
from . FREX_UTILS import FREX_OT_AddTexFob
from . FREX_UTILS import FREX_OT_set_geo_node_data

from bpy.props import PointerProperty




classes = (
    FREX_OT_fractal_extruder,
    FREX_OT_AddFob,
    FREX_OT_FobToText,
    FREX_OT_SetLineArtVertexMap,
    FREX_OT_LOAD_DOCS,
    GLOBAL_UL_fractal_extruder_props,
    VIEW3D_PT_fractal_extruder_tool,
    FREX_OT_fractal_painter,
    FREX_OT_AddTexFob,
    FREX_OT_set_geo_node_data
    
)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
    bpy.types.Scene.fractal_extruder_props = PointerProperty(
        type = GLOBAL_UL_fractal_extruder_props
    )

def unregister():
    del(bpy.types.Scene.fractal_extruder_props)
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

if __name__ == "__main__":
    register()
