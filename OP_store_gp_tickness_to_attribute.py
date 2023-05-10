'''Store the GP pencil tickness to a mesh attribute
    Tickness must be then multiplied by the value stored in the custom property to retrieve the tickness '''


import bpy
from bpy.types import Operator

class GP_OT_store_radius_to_custom_property(Operator):
    """Store the radius of each point into a custom property """
    bl_idname = "gp.store_radius_to_custom_property"
    bl_label = "Convert radius to custom property"
    bl_options = {'REGISTER','UNDO'}

    @classmethod
    def poll(cls, context):
        return  context.active_object is not None and context.active_object.type == 'CURVE'

    def execute(self, context):
        obj = context.active_object

        result = []
        max_radius = 0.0
        #we assume that we start
        for spline in obj.data.splines:
            point_spline = []
            for point in spline.points:
                point_spline.append(point.radius)
                if point.radius > max_radius:
                    max_radius = point.radius
            result.append(point_spline)

        obj['stored_radius'] = result
        obj['max_radius'] = max_radius

        return {'FINISHED'}


class GP_OT_convert_custom_property_to_vertex_group(Operator):
    """Store the radius of each point into a custom property """
    bl_idname = "gp.convert_custom_property_to_vertex_group"
    bl_label = "Convert custom property to vertex group"
    bl_options = {'REGISTER','UNDO'}

    @classmethod
    def poll(cls, context):
        return  context.active_object is not None and context.active_object.type == 'MESH'

    def execute(self, context):
        
        return {'FINISHED'}


class GP_OT_convert_vertex_group_to_thickness(Operator): 
    """Convert stroke tickness to a mesh attribute """
    bl_idname = "gp.convert_vertex_group_to_thickness"
    bl_label = "Convert vertex group to thickness"
    bl_options = {'REGISTER','UNDO'}

    def execute(self, context):
        print ('yiha')
        return {'FINISHED'}


### Registration
classes = (
    GP_OT_store_radius_to_custom_property,
    GP_OT_convert_custom_property_to_vertex_group,
    GP_OT_convert_vertex_group_to_thickness,
)

def register():
    for cl in classes:  
        bpy.utils.register_class(cl)

def unregister():
    for cl in reversed(classes):
        bpy.utils.unregister_class(cl)
