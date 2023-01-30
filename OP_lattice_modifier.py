import bpy
from bpy.types import Operator
from mathutils import Vector


def get_object_max_dimension(context, object):
    max_dim_x = 0.0
    max_dim_y = 0.0
    max_dim_z = 0.0

    max_area = 0
    bbox_corners = None
    for frame in range(context.scene.frame_start, context.scene.frame_end):
        context.scene.frame_set(frame)
        dim = object.dimensions

        if dim.x * dim.z > max_area:
            max_area  = dim.x * dim.z
            bbox_corners = [object.matrix_world @ Vector(corner) for corner in object.bound_box]

        max_dim_x = dim.x if dim.x >max_dim_x else max_dim_x
        max_dim_y = dim.y if dim.y >max_dim_y else max_dim_y
        max_dim_z = dim.z if dim.z >max_dim_z else max_dim_z

    max_xyz = max(bbox_corners, key=lambda x: (x[0], x[1], x[2]))
    min_xyz = min(bbox_corners, key=lambda x: (x[0], x[1], x[2]))
    location = (max_xyz + min_xyz) *0.5
    dimension = Vector((max_dim_x, max_dim_y, max_dim_z))

    return location, dimension

class GP_OT_add_lattice(Operator):
    """Add a lattice modifier to objects defined in the target collection"""
    bl_idname="flattener.add_lattice"
    bl_description="Add a lattice modifier to all the objects "
    bl_label = "Add lattice to target"

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def execute(self, context):
        for obj in context.scene.gp_flattener.target_collection.objects:
            location, dimension = get_object_max_dimension(context, obj)
        lattice = bpy.data.lattices.new("Lattice")
        lattice_ob = bpy.data.objects.new("Lattice", lattice)
        lattice_ob.scale = (dimension.x, 0.05, dimension.z)
        lattice_ob.location = location

        context.scene.gp_flattener.target_collection.objects.link(lattice_ob)
        
        for ob in context.scene.gp_flattener.target_collection.objects:
            if ob.type == 'GPENCIL':
                mod = ob.grease_pencil_modifiers.new("Lattice", 'GP_LATTICE')
                mod.object = lattice_ob

        print('on ajoute le lattice ')
        return {'FINISHED'}

### Registration
classes = (
GP_OT_add_lattice,
)

def register():
    for cl in classes:  
        bpy.utils.register_class(cl)

def unregister():
    for cl in reversed(classes):
        bpy.utils.unregister_class(cl)