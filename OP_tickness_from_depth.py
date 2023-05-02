import bpy
from bpy.types import Operator
from bpy.props import FloatProperty, EnumProperty
from mathutils import Vector

def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolate on the scale given by a to b, using t as the point on that scale.
    Examples
    --------
        50 == lerp(0, 100, 0.5)
        4.2 == lerp(1, 5, 0.8)
    """
    return (1 - t) * a + t * b

class GP_OT_reset_bake_in_vertex_color(Operator):
    """Remove Position baking from point vertex color """
    bl_idname = "gp.reset_position_in_vertex_color"
    bl_label = "Reset Position from vertex colors"
    bl_options = {'REGISTER','UNDO'}

    @classmethod
    def poll(cls, context):
        return  context.active_object is not None and context.active_object.type == 'GPENCIL'
    
    def execute(self, context):
            obj = context.active_object

            if not obj['gp_flattener_is_baked']:
                return {'CANCELLED'}

            for layer in obj.data.layers:
                total_frames = len(layer.frames)
                for index, frame in enumerate(layer.frames):
                    for stroke in frame.strokes:
                        for point in stroke.points:
                            point.vertex_color = Vector((0.0, 0.0,0.0,1.0))

                    print(f"Progress {index/(total_frames-1) *100} %")

            obj['gp_flattener_is_baked'] = False
            return {'FINISHED'}


class GP_OT_bake_position_in_vertex_color(Operator):
    """Bake points world position in their vertex color """
    bl_idname = "gp.bake_position_in_vertex_color"
    bl_label = "Bake Position in vertex colors"
    bl_options = {'REGISTER','UNDO'}

    @classmethod
    def poll(cls, context):
        return  context.active_object is not None and context.active_object.type == 'GPENCIL'

    def execute(self, context):
        obj = context.active_object

        camera  = context.scene.camera
        cam_position = camera.matrix_world.translation

        min = 100000
        max = -100000

        for layer in obj.data.layers:
            total_frames = len(layer.frames)
            for index, frame in enumerate(layer.frames):
                for stroke in frame.strokes:
                    for point in stroke.points:
                        point_loc = obj.matrix_world @ point.co
                        distance = (cam_position - point_loc).length
                        if distance < min :
                            min = distance
                        if distance > max:
                            max = distance

                print(f"Progress {index/(total_frames-1) *100} %")

        print(f"La distance min est {min}")
        print(f"La distance max est {max}")

        obj['gp_flattener_max'] = max
        obj['gp_flattener_min'] = min

        for layer in obj.data.layers:
            total_frames = len(layer.frames)
            for index, frame in enumerate(layer.frames):
                for stroke in frame.strokes:
                    for point in stroke.points:
                        point_loc = obj.matrix_world @ point.co
                        normalized = ((cam_position - point_loc).length - min) / (max - min)
                    
                        point.vertex_color = Vector((normalized,normalized,normalized,1.0))

                print(f"Progress {index/(total_frames-1) *100} %")

        obj['gp_flattener_is_baked'] = True

        # TODO Add a tag to the current object to tell it has been baked

        return {'FINISHED'}
    
    
class GP_OT_change_tickness_from_depth(Operator):
    """Run statistics """
    bl_idname = "gp.change_thickness_from_depth"
    bl_label = "Remap tickness"
    bl_options = {'REGISTER','UNDO'}

    easing : EnumProperty(
        items = [('EaseIn','Ease In','','',0), 
             ('EaseOut','Ease Out','','',1)],
        name = "Easing",
        default = 'EaseOut',
    )


    falloff : EnumProperty(
        items = [('Linear','Linear','','',0), 
             ('Quadratic','Quadratic','','',1),
             ('Cubic','Cubic','','',2),
             ('Quartic','Quartic','','',4),
             ('Quintic','Quintic','','',5)],
        name = "Falloff",
        default = 'Linear',
    )

    min_thickness : FloatProperty(
        default=1.0,
        min=0.0
    )

    max_thickness : FloatProperty(
        default=2.0,
        min=0.0
    )

    @classmethod
    def poll(cls, context):
        return  context.active_object is not None and context.active_object.type == 'GPENCIL'
    
    def execute(self, context):
        obj = context.active_object

        for layer in obj.data.layers:
            total_frames = len(layer.frames)
            for index, frame in enumerate(layer.frames):
                for stroke in frame.strokes:
                    for point in stroke.points:
                        fac = point.vertex_color[0]
                        if self.falloff == 'Linear':
                            pass
                        elif self.falloff == 'Quadratic' and self.easing == 'EaseIn':
                            fac = fac ** 2
                        elif self.falloff == 'Quadratic' and self.easing == 'EaseOut':
                            fac = 1 - (1- fac) ** 2
                        elif self.falloff == 'Cubic' and self.easing == 'EaseIn':
                            fac = fac ** 3
                        elif self.falloff == 'Cubic' and self.easing == 'EaseOut':
                            fac = 1 - (1- fac) ** 3
                        elif self.falloff == 'Quartic' and self.easing == 'EaseIn':
                            fac = fac ** 4
                        elif self.falloff == 'Quartic' and self.easing == 'EaseOut':
                            fac = 1 - (1- fac) ** 4
                        elif self.falloff == 'Quintic' and self.easing == 'EaseIn':
                            fac = fac ** 5
                        elif self.falloff == 'Quintic' and self.easing == 'EaseOut':
                            fac = 1 - (1- fac) ** 5

                        new_tickness_factor = lerp(self.min_thickness, self.max_thickness, fac)
                        point.pressure = new_tickness_factor
                print(f"Progress {index/(total_frames-1) *100} %")

        return {'FINISHED'}

### Registration
classes = (
GP_OT_bake_position_in_vertex_color,
GP_OT_reset_bake_in_vertex_color,
GP_OT_change_tickness_from_depth,
)

def register():
    for cl in classes:  
        bpy.utils.register_class(cl)

def unregister():
    for cl in reversed(classes):
        bpy.utils.unregister_class(cl)
