import bpy
import time
from bpy.types import Operator
from bpy.props import BoolProperty

class GP_OT_convert_geo_nodes(Operator):
    """Convert current Geo Node Object in Grease pencil one """
    bl_idname = "gp.convert_geo_node_to_gp"
    bl_label = "Convert Geo Node to Grease Pencil"
    bl_options = {'REGISTER','UNDO'}

    merge_generated_objects : BoolProperty(
        default=True
    )


    @classmethod
    def poll(cls, context):
        return  context.mode == 'OBJECT' and context.active_object is not None

    def execute(self, context):
        target_collection = bpy.data.collections['Test']
        obj = context.active_object

        gp_data = bpy.data.grease_pencils.new('roger')
        gp_data.layers.new('toto')
        gp_data.layers.active.frames.new(0)
        target_obj = bpy.data.objects.new('instance_object', gp_data)
        target_collection.objects.link(target_obj )

        to_select = []


        for frame in range(context.scene.frame_start, context.scene.frame_end+1):
            start_time = time.time()
            context.scene.frame_set(frame)
            context.view_layer.objects.active = obj
            obj.select_set(True)    
            bpy.ops.object.convert(target='GPENCIL', keep_original=True, thickness=2)
            newly_created_object = context.active_object
            newly_created_object.select_set(True)
            to_select.append(newly_created_object)
            end_time = time.time()
            print(f"Frame {frame} done in {end_time - start_time} seconds")

        for slc in to_select:
            slc.select_set(True)

        if not self.merge_generated_objects:
            return {'FINISHED'}

        context.view_layer.objects.active = target_obj
        target_obj.select_set(True)
        context.scene.frame_set(0)
        bpy.ops.object.join()
        bpy.ops.gpencil.editmode_toggle()
        bpy.ops.gpencil.layer_merge(mode='ALL')
        bpy.ops.gpencil.editmode_toggle()

        bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)

        return {'FINISHED'}
    
### Registration
classes = (
GP_OT_convert_geo_nodes,

)

def register():
    for cl in classes:  
        bpy.utils.register_class(cl)

def unregister():
    for cl in reversed(classes):
        bpy.utils.unregister_class(cl)
