import os

import bpy

from .data_loader import MaterialRepository, StructureLoader
from .scene_builder import StructureSceneBuilder
from .state import state


class AtomsVisualizerController:
    def __init__(self):
        self.state = state
        self.loader = StructureLoader()
        self.material_repository = MaterialRepository(os.path.dirname(__file__))
        self.scene_builder = StructureSceneBuilder(self.state)

    def load_structure(self, file_path: str) -> None:
        self.state.reset_structure()
        self.state.atoms = self.loader.read_xyz(file_path)
        self.state.elem_list = list(dict.fromkeys(atom[0] for atom in self.state.atoms))
        self.state.atom_info, self.state.bond_info = self.material_repository.load_for_elements(self.state.elem_list)

        self.scene_builder.create_atom_spheres()
        self.scene_builder.create_bonds()
        self.scene_builder.organize_into_collections()
        self.scene_builder.apply_materials()
        self.scene_builder.setup_default_sun_light()
        self.scene_builder.setup_camera_isometric_view()

        for scene in bpy.data.scenes:
            self.scene_builder.initialize_radius_collection(scene)

        scene = bpy.context.scene
        if hasattr(scene, "bond_thickness_scene"):
            scene.bond_thickness_scene = self.state.bond_thickness
        if hasattr(scene, "atom_metallic_scene"):
            scene.atom_metallic_scene = self.state.atom_metallic
        if hasattr(scene, "atom_translucency_scene"):
            scene.atom_translucency_scene = self.state.atom_translucency
        if hasattr(scene, "atom_glossiness_scene"):
            scene.atom_glossiness_scene = self.state.atom_glossiness
        if hasattr(scene, "material_style_scene"):
            scene.material_style_scene = self.state.material_style

    def update_atomic_radius(self, prop, context) -> None:
        scene = context.scene
        index = None
        for i, radius_prop in enumerate(scene.atomic_radius):
            if radius_prop == prop:
                index = i
                break

        if index is None or index >= len(self.state.elem_list):
            return

        element = self.state.elem_list[index]
        for obj in bpy.data.objects:
            if obj.type == "MESH" and obj.name.startswith(f"{element}_"):
                obj.scale = (prop.value, prop.value, prop.value)
                self.state.current_atoms_info[element]["radius"] = prop.value

    def update_bond_thickness(self, context) -> None:
        scene = context.scene
        self.state.bond_thickness = scene.bond_thickness_scene

        for obj in bpy.data.objects:
            if obj.type == "MESH" and obj.name.startswith("bond"):
                obj.scale.x = self.state.bond_thickness / 2
                obj.scale.y = self.state.bond_thickness / 2
                obj.scale.z = 1

    def update_bond_cutoff_distance(self, context) -> None:
        bpy.ops.object.select_all(action="DESELECT")
        for obj in bpy.data.objects:
            if obj.type == "MESH" and obj.name.startswith("bond"):
                obj.select_set(True)
        bpy.ops.object.delete()

        self.state.bond_cutoff_distance = context.scene.bond_cutoff_distance_scene
        self.scene_builder.create_bonds()

    def update_atom_appearance(self, context) -> None:
        scene = context.scene
        self.state.atom_metallic = scene.atom_metallic_scene
        self.state.atom_translucency = scene.atom_translucency_scene
        self.state.atom_glossiness = scene.atom_glossiness_scene
        self.state.material_style = scene.material_style_scene
        self.scene_builder.apply_materials()

    def update_atom_color(self, prop, context) -> None:
        scene = context.scene
        index = None
        for i, color_prop in enumerate(scene.atomic_color):
            if color_prop == prop:
                index = i
                break

        if index is None or index >= len(self.state.elem_list):
            return

        element = self.state.elem_list[index]
        r, g, b, a = prop.value
        self.state.atom_info[element]["color"] = (r, g, b, a)
        self.state.current_atoms_info[element]["color"] = (r, g, b, a)
        self.scene_builder.apply_collection_color(element, (r, g, b, a))


_controller = AtomsVisualizerController()


def get_controller() -> AtomsVisualizerController:
    return _controller
