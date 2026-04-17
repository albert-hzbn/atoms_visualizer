import bpy

from .controller import get_controller
from .operators import LoadFileOperator
from .props import AtomColorPropertyGroup, AtomPropertyGroup, register_scene_properties, unregister_scene_properties
from .state import state
from .ui import FILE_PT_loader_panel


bl_info = {
    "name": "Atoms Visualizer",
    "author": "Albert Linda",
    "version": (0, 2, 0),
    "blender": (2, 80, 0),
    "location": "3D Viewport > SideBar > Atoms Visualizer",
    "description": "A simple addon to load atoms in .xyz format.",
    "category": "Import-Export",
}


CLASSES = (
    AtomPropertyGroup,
    AtomColorPropertyGroup,
    LoadFileOperator,
    FILE_PT_loader_panel,
)


def menu_func(self, context):
    self.layout.operator(LoadFileOperator.bl_idname, text="Load File...")


def initialize_all_scenes(dummy=None):
    if not state.elem_list:
        return
    builder = get_controller().scene_builder
    for scene in bpy.data.scenes:
        builder.initialize_radius_collection(scene)


def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)

    bpy.types.TOPBAR_MT_file.append(menu_func)
    register_scene_properties()

    if initialize_all_scenes not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(initialize_all_scenes)


def unregister():
    if initialize_all_scenes in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(initialize_all_scenes)

    if hasattr(bpy.types, "TOPBAR_MT_file"):
        bpy.types.TOPBAR_MT_file.remove(menu_func)

    unregister_scene_properties()

    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
