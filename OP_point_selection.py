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
    '''Delete all the non visible point '''
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


def create_instance_dict(context, obj):
    result = {}

    for frame in range(context.scene.frame_start, context.scene.frame_end +1):
        context.scene.frame_set(frame)

        depsgraph = context.evaluated_depsgraph_get()
        evaluated_train = obj.evaluated_get(depsgraph)
        current_frame_list =[]
        for inst in depsgraph.object_instances:
            if not inst.is_instance:
                continue
            if inst.parent != evaluated_train:
                continue 
            if inst.instance_object.name == obj.name:
                continue
            current_frame_list.append((inst.instance_object.name,inst.matrix_world.copy()))

            # print(Vector(inst.matrix_world.to_translation()- context.scene.camera.matrix_world.to_translation()).length)
            # print(f"Le nom est {inst. instance_object.name} et sa matrice est {inst.matrix_world}")

        result[frame] = current_frame_list

    return result


def duplicate(obj, data=True, actions=True, collection=None):
    obj_copy = obj.copy()
    if data:
        obj_copy.data = obj_copy.data.copy()
    if actions and obj_copy.animation_data:
        obj_copy.animation_data.action = obj_copy.animation_data.action.copy()
    collection.objects.link(obj_copy)
    return obj_copy

def instanciate_gp_from_dict(context, dict):
    to_duplicate = bpy.data.objects['Stroke']
    target_collection = bpy.data.collections['Target']
    target_obj = bpy.data.objects['Target']
    previous_frame = 0
    for index, frame in enumerate(range(context.scene.frame_start, context.scene.frame_end +1)):
        bpy.ops.object.select_all(action='DESELECT')
        for name, matrix in dict[frame]:
            # TODO Choose object to duplicate based on name and distance to camera

            new_obj = duplicate(to_duplicate,True,False,target_collection)
            new_obj.matrix_world = matrix

            new_obj.data.layers[0].frames[0].frame_number = frame

            new_obj.select_set(True)
        
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        target_obj.select_set(True)
        context.view_layer.objects.active = target_obj

        bpy.ops.object.join()
        #on passe en mode gp edit
        bpy.ops.gpencil.editmode_toggle()

        #on deselectionne tout
        bpy.ops.gpencil.select_all(action='DESELECT',)
        #on selectionne les points de layer line
        for stroke in target_obj.data.layers['Lines'].frames[max(index-1,0)].strokes:
            stroke.select = True
        #on se place a la bonne frame 
        context.scene.frame_set(frame)
        #on merge down
        target_obj.data.layers.active = target_obj.data.layers['Lines']
        target_obj.data.layers['Lines'].select = True

        bpy.ops.gpencil.layer_merge(mode='ALL')
        #on supprime les points selectionnés
        bpy.ops.gpencil.delete(type='STROKES')
        #on passe en mode object
        bpy.ops.gpencil.editmode_toggle()

        bpy.ops.outliner.orphans_purge(do_recursive=True)
        previous_frame = frame
        print(f"Frame {frame} done ")


class GP_OT_evaluate_despgraph(Operator):
    """Evaluate the current dependency graph"""
    bl_idname="gp.evaluate_graph"
    bl_description="Evaluate dependency graph at current frame"
    bl_label = "Evaluate !"

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def execute(self, context):
        train = context.scene.gp_flattener.train_object
        if not train:
            return {'CANCELED'}
        dict = create_instance_dict(context, train)
        print(len(dict))

        instanciate_gp_from_dict(context, dict)

       
        return {'FINISHED'}


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

    merge_fills : BoolProperty(
        name="Merge Fills",
        description="Merge all fills layers in mesh grease pencil",
        default=True
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

        if gp_props.use_line_art and gp_props.flattener_gp_line_art is not None:
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
            bpy.ops.gpencil.bake_mesh_animation(step=gp_props.animation_step, project_type='KEEP')
            mesh_obj = context.active_object
            mesh_obj.name = f"{gp_props.flattener_mesh_collection.name}_flattened"
            move_obj_to_collection(context, 'Target', mesh_obj)
            objects_to_flatten.append(mesh_obj)

            layers_to_remove = []
            for layer in mesh_obj.data.layers:
                if layer.info.endswith('_Lines'):
                    layers_to_remove.append(layer)

            for to_remove in layers_to_remove:
                mesh_obj.data.layers.remove(to_remove)

            if self.merge_fills:
                bpy.ops.object.mode_set(mode='EDIT_GPENCIL')
                mesh_obj.data.layers.active_index =0
                bpy.ops.gpencil.layer_merge(mode='ALL')
                bpy.ops.object.mode_set(mode='OBJECT')

        if self.flatten_object:
            #TODO Let the user choose the distance to camera for reprojection
            if context.space_data.region_3d.view_perspective != 'CAMERA':
                bpy.ops.view3d.view_camera()
            bpy.ops.object.select_all(action='DESELECT')
            for obj in objects_to_flatten:
                obj.select_set(True)
                context.view_layer.objects.active = obj
                bpy.ops.gp.batch_reproject_all_frames()

        if gp_props.merge_flattened:
            bpy.ops.object.select_all(action='DESELECT')
            print(f'On merge !! {len(objects_to_flatten)}')
            for obj in objects_to_flatten:
                obj.select_set(True)
                context.view_layer.objects.active = obj
            bpy.ops.object.join() 

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
GP_OT_evaluate_despgraph,
)

def register():
    for cl in classes:  
        bpy.utils.register_class(cl)

def unregister():
    for cl in reversed(classes):
        bpy.utils.unregister_class(cl)
