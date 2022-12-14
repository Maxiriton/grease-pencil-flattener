import bpy
import time
from bpy.types import Operator
from bpy.props import BoolProperty, IntProperty
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector

def get_points_on_screen(context, gp_obj):
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
            print(f"Layer {layer} - Frame {frame.frame_number}")
            #We delete the selected points  
            bpy.ops.gpencil.delete(type='POINTS')
    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
    end_time = time.time()
    print(f'Operation réalisée en {end_time - start_time} s')

class GP_OT_get_points_visible(Operator):
    """Select all visibles points """
    bl_idname = "gp.get_visible_points"
    bl_label = "Select Visible Points"
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

    animation_step : IntProperty(
        name = "Animation Step",
        description = "Number of frame between two keyframes. Only used for animation baking",
        default = 2
    )

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT' and context.active_object is not None and context.active_object.type == 'GPENCIL'

    def execute(self, context):
        if self.bake_animation:
            bpy.ops.gpencil.bake_grease_pencil_animation(step=self.animation_step) #This will create a new object with baked animation
        else:
            new_obj = context.active_object.copy()
            context.view_layer.objects.link(new_obj)
            context.active_object = new_obj

        gp_obj = context.active_object

        get_points_on_screen(context, gp_obj)

        if self.flatten_object:
            #TODO Do not depend on external operators for this one
            #TODO Let the use choose the distance to camera for reprojection
            if context.space_data.region_3d.view_perspective != 'CAMERA':
                bpy.ops.view3d.view_camera()
            bpy.ops.gp.batch_reproject_all_frames()



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
