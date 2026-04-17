import bpy
from bpy.props import CollectionProperty, EnumProperty, FloatProperty, FloatVectorProperty, StringProperty

from bpy.types import PropertyGroup

from .controller import get_controller
from .state import state


def update_atomic_radius(self, context):
    get_controller().update_atomic_radius(self, context)


def update_bond_thickness(self, context):
    if not hasattr(context.scene, "bond_thickness_scene"):
        return
    get_controller().update_bond_thickness(context)


def update_bond_cutoff_distance(self, context):
    if not hasattr(context.scene, "bond_cutoff_distance_scene"):
        return
    get_controller().update_bond_cutoff_distance(context)


def update_atom_appearance(self, context):
    get_controller().update_atom_appearance(context)


def update_atom_color(self, context):
    get_controller().update_atom_color(self, context)


class AtomPropertyGroup(PropertyGroup):
    value: FloatProperty(
        name="Atomic Radius",
        default=1.0,
        min=0.1,
        max=4.0,
        update=update_atomic_radius,
    )


class AtomColorPropertyGroup(PropertyGroup):
    value: FloatVectorProperty(
        name="Atom Color",
        subtype="COLOR",
        size=4,
        default=(1.0, 1.0, 1.0, 1.0),
        min=0.0,
        max=1.0,
        update=update_atom_color,
    )


def register_scene_properties():
    bpy.types.Scene.last_loaded_file = StringProperty(
        name="Last Loaded File",
        description="Path to the last loaded file",
        default="",
        subtype="FILE_PATH",
    )

    bpy.types.Scene.atomic_radius = CollectionProperty(type=AtomPropertyGroup)
    bpy.types.Scene.atomic_color = CollectionProperty(type=AtomColorPropertyGroup)
    bpy.types.Scene.bond_thickness_scene = FloatProperty(
        name="Current Bond Thickness",
        description="Controls the thickness of the bond",
        default=state.bond_thickness,
        min=0.01,
        max=0.5,
        update=update_bond_thickness,
    )

    bpy.types.Scene.bond_cutoff_distance_scene = FloatProperty(
        name="Current Bond Formation",
        description="Controls whether bonds will form between atoms or not",
        default=state.bond_cutoff_distance,
        min=0,
        max=5,
        update=update_bond_cutoff_distance,
    )

    bpy.types.Scene.atom_metallic_scene = FloatProperty(
        name="Atom Metallic",
        description="Controls metallic appearance of atoms",
        default=state.atom_metallic,
        min=0.0,
        max=1.0,
        update=update_atom_appearance,
    )

    bpy.types.Scene.atom_translucency_scene = FloatProperty(
        name="Atom Translucency",
        description="Controls transmission/translucency of atoms",
        default=state.atom_translucency,
        min=0.0,
        max=1.0,
        update=update_atom_appearance,
    )

    bpy.types.Scene.atom_glossiness_scene = FloatProperty(
        name="Atom Glossiness",
        description="Controls glossy shine of atoms",
        default=state.atom_glossiness,
        min=0.0,
        max=1.0,
        update=update_atom_appearance,
    )

    bpy.types.Scene.material_style_scene = EnumProperty(
        name="Material Style",
        description="Select visual material type for atoms",
        items=[
            ("PBR", "PBR", "Balanced physically-based look"),
            ("METAL", "Metal", "Highly metallic polished look"),
            ("GLASS", "Glass", "Transmissive glassy look"),
            ("PLASTIC", "Plastic", "Smooth plastic look"),
            ("MATTE", "Matte", "Flat non-shiny look"),
            ("EMISSION", "Glow", "Self-illuminated glowing look"),
        ],
        default=state.material_style,
        update=update_atom_appearance,
    )



def unregister_scene_properties():
    for name in [
        "last_loaded_file",
        "atomic_radius",
        "atomic_color",
        "bond_thickness_scene",
        "bond_cutoff_distance_scene",
        "atom_metallic_scene",
        "atom_translucency_scene",
        "atom_glossiness_scene",
        "material_style_scene",
    ]:
        if hasattr(bpy.types.Scene, name):
            delattr(bpy.types.Scene, name)
