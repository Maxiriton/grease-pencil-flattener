import bpy
import time
from bpy.types import Operator
from bpy.props import BoolProperty, IntProperty
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector

def move_obj_to_collection(context, target_collection_name, obj):
    for coll in obj.users_collection:
        # Unlink the object
        coll.objects.unlink(obj)
    bpy.data.collections[target_collection_name].objects.link(obj)


def delete_non_visible_points(context, gp_obj):
    start_time = time.time()
    # For each point on the stroke we check if it is visible from screen
    bpy.ops.object.mode_set(mode='EDIT_GPENCIL', toggle=False)

    for layer in gp_obj.data.layers:
        for frame in layer.frames:
            context.scene.frame_set(frame.frame_number)
            for stroke in frame.strokes:
                for point in stroke.points:
                    co_world = gp_obj.matrix_world @ point.co

                    ray_target = context.scene.camera.location  #We launch a ray from the center of the camera
                    ray_direction = Vector(ray_target - co_world).normalized()
                
                    _, _, _, _, obj, _ = context.scene.ray_cast(context.view_layer.depsgraph, co_world, ray_direction)

                    if obj is None:
                        #ce point est visible, on le garde
                        point.select = False
                    else:
                        #ce point a été intercepté par un objet quelconque, on doit le faire disparaitre    
                        point.select = True
            # print(f"Layer {layer} - Frame {frame.frame_number}")
            #We delete the selected points  
            bpy.ops.gpencil.delete(type='POINTS')
    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
    end_time = time.time()
    print(f'Operation réalisée en {end_time - start_time} s')

class GP_OT_get_points_visible(Operator):
    """Select all visibles points """
    bl_idname = "gp.flatten_grease_pencil"
    bl_label = "Flatten !"
    bl_options = {'REGISTER','UNDO'}

    bake_animation : BoolProperty(
        name="Bake Grease Pencil Object",
        description="Bake current object animation and modifiers",
        default=True
    )

    flatten_object : BoolProperty(
        name = "Flatten Object",
        description = "Call Reproject Operator after stroke selection",
        default= True
    )

    hide_originals : BoolProperty(
        name= "Hide Base Objects",
        description= " Hide the mesh collection and the orginal grease pencil object after the operation",
        default= True
    )

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def execute(self, context):
        objects_to_flatten = []
        gp_props = context.scene.gp_flattener

        if gp_props.flattener_gp_object is not None: 
            context.view_layer.objects.active = gp_props.flattener_gp_object
            if self.bake_animation:
                bpy.ops.gpencil.bake_grease_pencil_animation(step= gp_props.animation_step) #This will create a new object with baked animation
            else:
                gp_obj = context.active_object.copy()
                context.view_layer.objects.link(gp_obj)
                context.view_layer.objects.active = gp_obj

            gp_obj = context.active_object
            gp_obj.name = f"{gp_props.flattener_gp_object.name}_flattened"
            move_obj_to_collection(context, 'Target', gp_obj)

            objects_to_flatten.append(gp_obj)
            delete_non_visible_points(context, gp_obj)

        if gp_props.flattener_gp_line_art is not None:
            bpy.ops.object.select_all(action='DESELECT')
            gp_props.flattener_gp_line_art.select_set(True)
            context.view_layer.objects.active =  gp_props.flattener_gp_line_art
            bpy.ops.gpencil.bake_grease_pencil_animation(step=gp_props.animation_step) #This will create a new object with baked animation
            line_art_obj = context.active_object
            line_art_obj.name = f"{gp_props.flattener_gp_line_art.name}_flattened"
            move_obj_to_collection(context, 'Target', line_art_obj)
            objects_to_flatten.append(line_art_obj)


        if gp_props.use_mesh_collection:
            if context.space_data.region_3d.view_perspective != 'CAMERA':
                bpy.ops.view3d.view_camera()
            bpy.ops.object.select_all(action='DESELECT')
            for obj in gp_props.flattener_mesh_collection.objects:
                obj.select_set(True)
            bpy.ops.gpencil.bake_mesh_animation(step=gp_props.animation_step)
            mesh_obj = context.active_object
            mesh_obj.name = f"{gp_props.flattener_mesh_collection.name}_flattened"
            move_obj_to_collection(context, 'Target', mesh_obj)

            #TODO Remove lines layers in this object


        if self.flatten_object:
            #TODO Do not depend on external operators for this one
            #TODO Let the user choose the distance to camera for reprojection
            if context.space_data.region_3d.view_perspective != 'CAMERA':
                bpy.ops.view3d.view_camera()
            bpy.ops.object.select_all(action='DESELECT')
            for obj in objects_to_flatten:
                context.view_layer.objects.active = obj
                bpy.ops.gp.batch_reproject_all_frames()

        if gp_props.merge_flattened:
            print('on merge calice !!')

        if self.hide_originals:
            if gp_props.flattener_mesh_collection is not None: 
                gp_props.flattener_mesh_collection.hide_viewport = True
            if gp_props.flattener_gp_object is not None:
                gp_props.flattener_gp_object.hide_viewport = True
            if gp_props.flattener_gp_line_art is not None:
                gp_props.flattener_gp_line_art.hide_viewport = True
        return {'FINISHED'}
        
### Registration
classes = (
GP_OT_get_points_visible,
)

def register():
    for cl in classes:  
        bpy.utils.register_class(cl)

def unregister():
    for cl in reversed(classes):
        bpy.utils.unregister_class(cl)
