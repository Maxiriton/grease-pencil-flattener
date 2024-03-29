# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name": "Grease Pencil Flattener",
    "author": "Henri Hebeisen",
    "version": (0, 2),
    "blender": (3, 6, 1),
    "location": "3D View > Properties Region > View",
    "description": "Convert Your 3D Grease Pencil strokes to flat and  drawable strokes",
    "warning": "Hautement experimental !",
    "wiki_url": "",
    "category": "3D View",
    }

from .utils import get_addon_prefs

import bpy
from bpy.types import AddonPreferences
from bpy.props import BoolProperty, FloatProperty
from . import OP_point_selection
from . import UI_converter_panel
from . import OP_lattice_modifier
from . import OP_tickness_from_depth
from . import OP_convert_geo_node_to_gp
from . import OP_store_gp_tickness_to_attribute

from .properties import GP_Flattener_Settings

# class GP_30_prefs(AddonPreferences):
#     bl_idname = __package__

#     ## tabs
#     use_modifiers : BoolProperty(
#         name="Use Modifiers",
#         default=True
#     )

#     def draw(self, context):
#         layout = self.layout
#         row= layout.row(align=True)
#         row.prop(self, "use_modifier")


classes = (
    GP_Flattener_Settings,
)

addon_modules = (
    OP_point_selection,
    OP_lattice_modifier,
    UI_converter_panel,
    OP_tickness_from_depth,
    OP_convert_geo_node_to_gp,
    OP_store_gp_tickness_to_attribute,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    for mod in addon_modules:
        mod.register()

    bpy.types.Scene.gp_flattener = bpy.props.PointerProperty(type = GP_Flattener_Settings)

def unregister():
    for mod in reversed(addon_modules):
        mod.unregister()

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.gp_flattener


if __name__ == "__main__":
    register()