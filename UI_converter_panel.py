# BEGIN GPL LICENSE BLOCK #####
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
# END GPL LICENSE BLOCK #####

import bpy
from bpy.types import Panel


class VIEW3D_PT_convert_grease_pencil_panel(Panel):
    """UI for managing Grease Pencil Flattener"""
    bl_idname = "VIEW3D_PT_grease_pencil_flattener_panel"
    bl_label = "Grease Pencil Flattener"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Grease Pencil"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        row = layout.row(align=True)
        row.prop(scene.gp_flattener, "animation_step")
        row = layout.row(align=True)
        split = row.split(factor=0.1)
        c = split.column()
        c.prop(scene.gp_flattener,"use_mesh_collection",text="", icon="OUTLINER_COLLECTION")
        split = split.split()
        c = split.column()
        c.prop(scene.gp_flattener, "flattener_mesh_collection")
        c.enabled = context.scene.gp_flattener.use_mesh_collection
        row = layout.row(align=True)
        split = row.split(factor=0.1)
        c = split.column()
        c.prop(scene.gp_flattener,"use_grease_pencil_object",text="", icon="OUTLINER_OB_GREASEPENCIL")
        split = split.split()
        c = split.column()
        c.prop(scene.gp_flattener, "flattener_gp_object")
        c.enabled = context.scene.gp_flattener.use_grease_pencil_object
        row = layout.row(align=True)
        split = row.split(factor=0.1)
        c = split.column()
        c.prop(scene.gp_flattener,"use_line_art",text="", icon="OUTLINER_DATA_GREASEPENCIL")
        split = split.split()
        c = split.column()
        c.prop(scene.gp_flattener, "flattener_gp_line_art")
        c.enabled = context.scene.gp_flattener.use_line_art
        row = layout.row(align=True)
        row.operator('gp.flatten_grease_pencil', icon="IPO_BOUNCE")

### Registration
classes = (
VIEW3D_PT_convert_grease_pencil_panel,
)

def register():
    for cl in classes:  
        bpy.utils.register_class(cl)

def unregister():
    for cl in reversed(classes):
        bpy.utils.unregister_class(cl)