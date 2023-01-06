import bpy
from bpy.types import PropertyGroup
from bpy.props import (
                    BoolProperty,
                    IntProperty,
                    PointerProperty,
                    FloatProperty
)

class GP_Flattener_Settings(PropertyGroup):
    use_mesh_collection : BoolProperty(
        name="Use Mesh Collection",
        description="Flatten selected Mesh collection",
        default=True
    )

    use_grease_pencil_object : BoolProperty(
        name="Use Grease Pencil Object",
        description="Flatten selected Grease Pencil Object",
        default=True
    )

    use_line_art : BoolProperty(
        name="Use Line Art Object",
        description="Generate outline on an another layer",
        default=True
    )

    animation_step : IntProperty(
        name = "Animation Step",
        description = "Number of frame between two keyframes. Only used for animation baking",
        default = 2,
        min=1
    )

    flattener_mesh_collection : PointerProperty(
        name="Mesh Collection",
        description="Mesh Collection to flatten and to use to  compute occlusion on Flattener GP object",
        type=bpy.types.Collection, 
    )


    flattener_gp_object : PointerProperty(
        name="Grease Pencil Object",
        type=bpy.types.Object,
    )

    train_object : PointerProperty(
        name="Train Object",
        type=bpy.types.Object
    )

    lod_1_distance : FloatProperty(
        name="LOD 1 distance",
        description="First Level of Detail distance",
        default=5.4,
        min=1.0
    )

    lod_2_distance : FloatProperty(
        name="LOD 2 distance",
        description="Second Level of Detail distance",
        default=23.23,
        min=1.0
    )

    flattener_gp_line_art : PointerProperty(
        name="Line Art Object",
        type=bpy.types.Object,
    )

    merge_flattened : BoolProperty(
        name="Merge Flattened objects",
        description="Merge all flattened objects",
        default=True
    )