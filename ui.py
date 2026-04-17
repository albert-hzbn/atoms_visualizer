import os

from bpy.types import Panel

from .operators import LoadFileOperator
from .state import state


class FILE_PT_loader_panel(Panel):
    bl_label = "Atoms Visualizer"
    bl_idname = "FILE_PT_loader_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Atoms Visualizer"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        if getattr(scene, "last_loaded_file", ""):
            box = layout.box()
            box.label(text="Last File:")
            box.label(text=os.path.basename(scene.last_loaded_file))

        layout.label(text="Load Structure:")
        row = layout.row()
        row.operator(LoadFileOperator.bl_idname, text=".xyz", icon="FILE")

        layout.label(text="Atomic Radius & Color:")
        col = layout.column(align=True)
        for i, num in enumerate(scene.atomic_radius):
            label = state.elem_list[i] if i < len(state.elem_list) else f"Elem {i + 1}"
            row = col.row(align=True)
            row.prop(num, "value", text=label)
            if i < len(scene.atomic_color):
                row.prop(scene.atomic_color[i], "value", text="")

        layout.label(text="Bond Thickness:")
        layout.prop(scene, "bond_thickness_scene", text="")

        layout.label(text="Bond Cutoff Distance:")
        layout.prop(scene, "bond_cutoff_distance_scene", text="")

        layout.label(text="Atom Appearance:")
        layout.prop(scene, "material_style_scene", text="Material")
        layout.prop(scene, "atom_metallic_scene", text="Metallic")
        layout.prop(scene, "atom_translucency_scene", text="Translucency")
        layout.prop(scene, "atom_glossiness_scene", text="Glossiness")
