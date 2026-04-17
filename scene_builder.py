import math

import bpy
import mathutils

from .state import VisualizerState


class StructureSceneBuilder:
    def __init__(self, app_state: VisualizerState):
        self.state = app_state

    def create_atom_spheres(self) -> None:
        for index, atom_data in enumerate(self.state.atoms):
            element, x, y, z = atom_data
            if element not in self.state.atom_info:
                continue

            atomic_radius = self.state.atom_info[element]["radius"]
            bpy.ops.mesh.primitive_uv_sphere_add(
                radius=1.0,
                location=(x, y, z),
                scale=(atomic_radius, atomic_radius, atomic_radius),
            )
            atom_object = bpy.context.active_object
            atom_object.name = f"{element}_{index + 1}"
            self.apply_shiny_geometry_style(atom_object)

            if element not in self.state.current_atoms_info:
                self.state.current_atoms_info[element] = self.state.atom_info[element]

    def create_bonds(self) -> None:
        for bond in self._list_bonds():
            self._create_cylinder_between_points(bond["elem1_pos"], bond["elem2_pos"], name="bond")

    def organize_into_collections(self) -> None:
        for element in self.state.elem_list:
            collection = bpy.data.collections.get(element)
            if collection is None:
                collection = bpy.data.collections.new(element)
                bpy.context.scene.collection.children.link(collection)

            for obj in bpy.context.scene.objects:
                if obj.type == "MESH" and obj.name.startswith(element + "_"):
                    for owner_collection in obj.users_collection:
                        owner_collection.objects.unlink(obj)
                    collection.objects.link(obj)

    def apply_materials(self) -> None:
        for element in self.state.elem_list:
            if element in self.state.atom_info:
                color = self.state.atom_info[element]["color"]
                self.apply_collection_color(element, color)

    def apply_collection_color(self, collection_name, color) -> None:
        material_name = f"{collection_name}_Material"
        material = bpy.data.materials.get(material_name)
        if material is None:
            material = bpy.data.materials.new(name=material_name)

        material.use_nodes = True
        bsdf = material.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Base Color"].default_value = color
            self._apply_material_style(bsdf, color)

        if self.state.atom_translucency > 0.001 and hasattr(material, "blend_method"):
            material.blend_method = "BLEND"
            if hasattr(material, "shadow_method"):
                material.shadow_method = "HASHED"
        elif hasattr(material, "blend_method"):
            material.blend_method = "OPAQUE"

        collection = bpy.data.collections.get(collection_name)
        if collection is None:
            return

        for obj in collection.objects:
            if obj.type != "MESH":
                continue
            self.apply_shiny_geometry_style(obj)
            if len(obj.data.materials) == 0:
                obj.data.materials.append(material)
            else:
                obj.data.materials[0] = material

    def setup_default_sun_light(self) -> None:
        center, radius = self._structure_center_and_radius()
        light_name = "AtomsVisualizer_Sun"

        light_object = bpy.data.objects.get(light_name)
        if light_object is None or light_object.type != "LIGHT":
            light_data = bpy.data.lights.get(light_name)
            if light_data is None:
                light_data = bpy.data.lights.new(name=light_name, type="SUN")
            else:
                light_data.type = "SUN"
            light_object = bpy.data.objects.new(light_name, light_data)
            bpy.context.scene.collection.objects.link(light_object)

        light_data = light_object.data
        light_data.type = "SUN"
        light_data.energy = 3.0
        light_data.angle = math.radians(5.0)

        sun_direction = mathutils.Vector((-1.0, -1.0, 2.0)).normalized()
        light_object.location = center + sun_direction * (radius * 8.0)
        to_center = (center - light_object.location).normalized()
        light_object.rotation_euler = to_center.to_track_quat("-Z", "Y").to_euler()

    def setup_camera_isometric_view(self) -> None:
        scene = bpy.context.scene
        center, radius = self._structure_center_and_radius()
        camera_name = "AtomsVisualizer_Camera"

        camera_object = bpy.data.objects.get(camera_name)
        if camera_object is None or camera_object.type != "CAMERA":
            camera_data = bpy.data.cameras.get(camera_name)
            if camera_data is None:
                camera_data = bpy.data.cameras.new(camera_name)
            camera_object = bpy.data.objects.new(camera_name, camera_data)
            scene.collection.objects.link(camera_object)

        camera_data = camera_object.data
        camera_data.type = "PERSP"
        camera_data.lens = 50

        fov = min(camera_data.angle_x, camera_data.angle_y)
        fit_distance = (radius / math.tan(fov * 0.5)) * 1.25

        iso_direction = mathutils.Vector((1.0, -1.0, 0.85)).normalized()
        camera_object.location = center + iso_direction * fit_distance
        look_vec = (center - camera_object.location).normalized()
        camera_object.rotation_euler = look_vec.to_track_quat("-Z", "Y").to_euler()
        scene.camera = camera_object

    def initialize_radius_collection(self, scene) -> None:
        scene.atomic_radius.clear()
        if hasattr(scene, "atomic_color"):
            scene.atomic_color.clear()
        for elem in self.state.elem_list:
            item = scene.atomic_radius.add()
            item.value = self.state.current_atoms_info[elem]["radius"]
            if hasattr(scene, "atomic_color"):
                color_item = scene.atomic_color.add()
                c = self.state.current_atoms_info[elem].get("color", (1.0, 1.0, 1.0, 1.0))
                color_item.value = (c[0], c[1], c[2], c[3])

    def apply_shiny_geometry_style(self, obj) -> None:
        if obj.type != "MESH":
            return

        for poly in obj.data.polygons:
            poly.use_smooth = True

        try:
            group = self._ensure_shiny_geo_node_group()
            if group is None:
                return
            modifier = obj.modifiers.get("AtomsVisualizer_GeoShiny")
            if modifier is None:
                modifier = obj.modifiers.new(name="AtomsVisualizer_GeoShiny", type="NODES")
            modifier.node_group = group
        except Exception:
            return

    def _apply_material_style(self, bsdf, color) -> None:
        style = self.state.material_style

        # Reset all style-affected inputs to neutral defaults so stale values never bleed through
        self._set_input(bsdf, "Metallic", 0.0)
        self._set_input(bsdf, "Transmission", 0.0)
        self._set_input(bsdf, "Roughness", 0.5)
        self._set_input(bsdf, "Specular", 0.5)
        self._set_input(bsdf, "IOR", 1.45)
        self._set_input(bsdf, "Emission Strength", 0.0)
        self._set_input(bsdf, "Emission Color", (0.0, 0.0, 0.0, 1.0))
        self._set_input(bsdf, "Emission", (0.0, 0.0, 0.0, 1.0))

        if style == "METAL":
            self._set_input(bsdf, "Metallic", 0.95)
            self._set_input(bsdf, "Transmission", 0.0)
            self._set_input(bsdf, "Roughness", max(0.02, 1.0 - self.state.atom_glossiness))
            self._set_input(bsdf, "Specular", 0.85)
        elif style == "GLASS":
            self._set_input(bsdf, "Metallic", 0.0)
            self._set_input(bsdf, "Transmission", max(0.65, self.state.atom_translucency))
            self._set_input(bsdf, "Roughness", 0.03)
            self._set_input(bsdf, "Specular", 1.0)
            self._set_input(bsdf, "IOR", 1.45)
        elif style == "PLASTIC":
            self._set_input(bsdf, "Metallic", 0.0)
            self._set_input(bsdf, "Transmission", 0.0)
            self._set_input(bsdf, "Roughness", 0.22)
            self._set_input(bsdf, "Specular", 0.65)
        elif style == "MATTE":
            self._set_input(bsdf, "Metallic", 0.0)
            self._set_input(bsdf, "Transmission", 0.0)
            self._set_input(bsdf, "Roughness", 0.82)
            self._set_input(bsdf, "Specular", 0.35)
        elif style == "EMISSION":
            self._set_input(bsdf, "Metallic", 0.0)
            self._set_input(bsdf, "Transmission", 0.0)
            self._set_input(bsdf, "Roughness", 0.15)
            self._set_input(bsdf, "Specular", 0.7)
            self._set_input(bsdf, "Emission", color)
            self._set_input(bsdf, "Emission Color", color)
            self._set_input(bsdf, "Emission Strength", 0.8)
        else:
            self._set_input(bsdf, "Metallic", self.state.atom_metallic)
            self._set_input(bsdf, "Transmission", self.state.atom_translucency)
            self._set_input(bsdf, "Roughness", 1.0 - self.state.atom_glossiness)
            self._set_input(bsdf, "Specular", 0.75)

    def _set_input(self, bsdf, input_name, value) -> None:
        if input_name in bsdf.inputs:
            bsdf.inputs[input_name].default_value = value

    def _ensure_shiny_geo_node_group(self):
        group_name = "AtomsVisualizer_GeoShiny"
        group = bpy.data.node_groups.get(group_name)
        if group is None:
            try:
                group = bpy.data.node_groups.new(group_name, "GeometryNodeTree")
            except Exception:
                return None

        if len(group.nodes) > 0:
            return group

        nodes = group.nodes
        links = group.links

        try:
            group.inputs.clear()
            group.outputs.clear()
            group.inputs.new("NodeSocketGeometry", "Geometry")
            group.outputs.new("NodeSocketGeometry", "Geometry")
        except Exception:
            try:
                interface = group.interface
                for item in list(interface.items_tree):
                    interface.remove(item)
                interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
                interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
            except Exception:
                return None

        input_node = nodes.new("NodeGroupInput")
        output_node = nodes.new("NodeGroupOutput")
        input_node.location = (-220, 0)
        output_node.location = (260, 0)

        try:
            smooth_node = nodes.new("GeometryNodeSetShadeSmooth")
            smooth_node.location = (10, 0)
            if "Shade Smooth" in smooth_node.inputs:
                smooth_node.inputs["Shade Smooth"].default_value = True
            links.new(input_node.outputs["Geometry"], smooth_node.inputs["Geometry"])
            links.new(smooth_node.outputs["Geometry"], output_node.inputs["Geometry"])
        except Exception:
            links.new(input_node.outputs["Geometry"], output_node.inputs["Geometry"])

        return group

    def _list_bonds(self):
        bonds = []
        num_atoms = len(self.state.atoms)
        for ind1 in range(num_atoms):
            elem1, x1, y1, z1 = self.state.atoms[ind1]
            for ind2 in range(ind1 + 1, num_atoms):
                elem2, x2, y2, z2 = self.state.atoms[ind2]
                if elem2 in self.state.bond_info.get(elem1, []) or elem1 in self.state.bond_info.get(elem2, []):
                    distance = ((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2) ** 0.5
                    if distance < self.state.bond_cutoff_distance:
                        bonds.append({
                            "elem1_pos": (x1, y1, z1),
                            "elem2_pos": (x2, y2, z2),
                        })
        return bonds

    def _create_cylinder_between_points(self, point1, point2, name="CustomCylinder"):
        if "Cube" in bpy.data.objects:
            bpy.data.objects.remove(bpy.data.objects["Cube"], do_unlink=True)

        p1 = mathutils.Vector(point1)
        p2 = mathutils.Vector(point2)
        distance = (p2 - p1).length

        bpy.ops.mesh.primitive_cylinder_add(
            radius=1.0,
            depth=distance,
            vertices=32,
            location=(0, 0, 0),
        )

        cylinder = bpy.context.active_object
        cylinder.name = name
        cylinder.scale = (self.state.bond_thickness / 2, self.state.bond_thickness / 2, 1)

        direction = p2 - p1
        direction.normalize()
        z_axis = mathutils.Vector((0, 0, 1))
        axis = z_axis.cross(direction)

        if axis.length > 0.001:
            axis.normalize()
            angle = math.acos(min(1, max(-1, z_axis.dot(direction))))
            rotation = mathutils.Quaternion(axis, angle)
            cylinder.rotation_mode = "QUATERNION"
            cylinder.rotation_quaternion = rotation

        cylinder.location = (p1 + p2) / 2
        return cylinder

    def _structure_center_and_radius(self):
        if not self.state.atoms:
            return mathutils.Vector((0.0, 0.0, 0.0)), 1.0

        center = mathutils.Vector((0.0, 0.0, 0.0))
        for _, x, y, z in self.state.atoms:
            center += mathutils.Vector((x, y, z))
        center /= len(self.state.atoms)

        radius = 0.0
        for elem, x, y, z in self.state.atoms:
            atom_pos = mathutils.Vector((x, y, z))
            atom_radius = float(self.state.atom_info.get(elem, {}).get("radius", 1.0))
            radius = max(radius, (atom_pos - center).length + atom_radius)

        return center, max(radius, 1.0)
