
bl_info = {
    "name":"Atoms Visualizer",
    "author": "Albert Linda",
    "version":(0,0,1),
    "blender": (2,80,0),
    "location": "3D Viewport > SideBar > Atoms Visualizer",
    "description": "A simple addon to load atoms in .xyz format.",
    "category":"Import-Export",
}


import bpy
import colorsys
import mathutils
import math
import json
import os
from bpy.props import StringProperty, FloatProperty, CollectionProperty
from bpy.types import Operator, Panel, PropertyGroup
from bpy_extras.io_utils import ImportHelper


elem_list = []
current_atoms_info = {}
bond_thickness = 0.2
bond_cutoff_distance = 3
atoms = []
atom_info = {}
bond_info = {}

def read_poscar(file_path):
    global atoms

    """
    Read atomic positions from a POSCAR file.
    
    Args:
        file_path (str): Path to the POSCAR file
        
    Returns:
        list: List of atoms with their element type and coordinates
    """
    with open(file_path, "r") as f:
        lines = f.readlines()

    # Get number of atoms from the first line
    num_atoms = int(lines[0])
    
    # Extract atomic positions
    atoms = []
    for i in range(num_atoms):
        line_index = i + 2  # Skip the first two lines
        atom_data = lines[line_index].split()
        element = atom_data[0]
        x, y, z = float(atom_data[1]), float(atom_data[2]), float(atom_data[3])
        atoms.append((element, x, y, z))

    # return atoms

def create_atom_spheres():
    global atoms
    global atom_info

    """
    Create sphere meshes for each atom at the specified positions.
    """
    global current_atoms_info

    for index, atom_data in enumerate(atoms):
        element, x, y, z = atom_data

        if element not in atom_info:
            print(f"Warning: Element '{element}' not found in atom_info.")
            continue

        # Get and scale radius
        atomic_radius_val = atom_info[element]["radius"] 

        # Create sphere at atom position
        bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, location=(x, y, z), scale=(atomic_radius_val, atomic_radius_val, atomic_radius_val))
        atom_object = bpy.context.active_object
        atom_object.name = f"{element}_{index + 1}"

        # Track unique elements
        if element not in current_atoms_info:
            current_atoms_info[element] = atom_info[element]


def get_element_list():
    global atoms
    global elem_list

    elem_list = list({atom[0] for atom in atoms})


def organize_into_collections():
    """
    Organize atom objects into collections based on their element type.
    """
    global elem_list

    for element in elem_list:
        # Create or retrieve the collection for this element
        collection_name = element
        if collection_name not in bpy.data.collections:
            new_collection = bpy.data.collections.new(collection_name)
            bpy.context.scene.collection.children.link(new_collection)
        else:
            new_collection = bpy.data.collections[collection_name]

        # Add atoms of this element type to the collection
        for obj in bpy.context.scene.objects:
            if obj.type == 'MESH' and obj.name.startswith(element + "_"):
                # Remove from any existing collections
                for collection in obj.users_collection:
                    collection.objects.unlink(obj)
                
                # Add to the correct element collection
                new_collection.objects.link(obj)

def color_collection(collection_name, color=(1, 0, 0, 1)):
    """
    Apply a material with the specified color to all objects in a collection.
    
    Args:
        collection_name (str): Name of the collection to color
        color (tuple): RGBA color values (default: red)
    """
    # Create a new material with the specified color
    material = bpy.data.materials.new(name=f"{collection_name}_Material")
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = color

    # Get the collection and apply the material to all mesh objects
    collection = bpy.data.collections.get(collection_name)
    if collection:
        for obj in collection.objects:
            if obj.type == 'MESH':
                # Add or replace the object's material
                if len(obj.data.materials) == 0:
                    obj.data.materials.append(material)
                else:
                    obj.data.materials[0] = material
    else:
        print(f"Collection '{collection_name}' not found")



def get_periodic_table_colors():
    """
    Generate distinct colors for all elements in the periodic table.
    
    Returns:
        dict: Dictionary mapping element symbols to RGBA color tuples
    """
    # Dictionary of all elements in the periodic table
    elements = [
        "H", "He", 
        "Li", "Be", "B", "C", "N", "O", "F", "Ne", 
        "Na", "Mg", "Al", "Si", "P", "S", "Cl", "Ar", 
        "K", "Ca", "Sc", "Ti", "V", "Cr", "Mn", "Fe", "Co", "Ni", "Cu", "Zn", "Ga", "Ge", "As", "Se", "Br", "Kr", 
        "Rb", "Sr", "Y", "Zr", "Nb", "Mo", "Tc", "Ru", "Rh", "Pd", "Ag", "Cd", "In", "Sn", "Sb", "Te", "I", "Xe", 
        "Cs", "Ba", "La", "Ce", "Pr", "Nd", "Pm", "Sm", "Eu", "Gd", "Tb", "Dy", "Ho", "Er", "Tm", "Yb", "Lu", 
        "Hf", "Ta", "W", "Re", "Os", "Ir", "Pt", "Au", "Hg", "Tl", "Pb", "Bi", "Po", "At", "Rn", 
        "Fr", "Ra", "Ac", "Th", "Pa", "U", "Np", "Pu", "Am", "Cm", "Bk", "Cf", "Es", "Fm", "Md", "No", "Lr", 
        "Rf", "Db", "Sg", "Bh", "Hs", "Mt", "Ds", "Rg", "Cn", "Nh", "Fl", "Mc", "Lv", "Ts", "Og"
    ]
    
    # Common CPK (Corey-Pauling-Koltun) color scheme for some frequent elements
    cpk_colors = {
        "H": (1.0, 1.0, 1.0, 1.0),           # White
        "C": (0.5, 0.5, 0.5, 1.0),           # Grey
        "N": (0.0, 0.0, 1.0, 1.0),           # Blue
        "O": (1.0, 0.0, 0.0, 1.0),           # Red
        "F": (0.0, 1.0, 0.0, 1.0),           # Green
        "Cl": (0.0, 1.0, 0.0, 1.0),          # Green
        "Br": (0.6, 0.2, 0.1, 1.0),          # Brown
        "I": (0.4, 0.0, 0.7, 1.0),           # Dark purple
        "He": (0.85, 1.0, 1.0, 1.0),         # Light cyan
        "Ne": (0.7, 0.9, 0.9, 1.0),          # Light blue
        "Ar": (0.5, 0.8, 0.9, 1.0),          # Light blue
        "P": (1.0, 0.5, 0.0, 1.0),           # Orange
        "S": (1.0, 0.8, 0.0, 1.0),           # Yellow
        "Li": (0.7, 0.0, 0.0, 1.0),          # Burgundy red
        "Na": (0.7, 0.0, 0.0, 1.0),          # Burgundy red
        "K": (0.7, 0.0, 0.0, 1.0),           # Burgundy red
        "Mg": (0.0, 0.6, 0.0, 1.0),          # Forest green
        "Ca": (0.0, 0.6, 0.0, 1.0),          # Forest green
        "Fe": (0.6, 0.5, 0.0, 1.0),          # Dark yellow
        "Si": (0.7, 0.7, 0.7, 1.0),          # Light grey
        "Al": (0.6, 0.8, 0.8, 1.0),          # Light blue
        "Ni": (0.5, 0.5, 0.0, 1.0),          # Bronze
        "Cu": (0.7, 0.1, 0.1, 1.0),          # Copper red
        "Zn": (0.4, 0.4, 0.7, 1.0),          # Light purple
        "Ag": (0.8, 0.8, 0.8, 1.0),          # Silver
        "Au": (1.0, 0.8, 0.0, 1.0),          # Gold
        "Ru": (1.0, 0.0, 0.0, 0.0)           # Red
    }
    
    # Generate colors for all other elements not in the CPK scheme
    element_colors = {}
    
    # Add CPK colors first
    for element, color in cpk_colors.items():
        element_colors[element] = color
    
    # Generate colors for remaining elements
    remaining_elements = [e for e in elements if e not in cpk_colors]
    num_remaining = len(remaining_elements)
    
    for i, element in enumerate(remaining_elements):
        # Use HSV color space for even distribution of colors
        hue = i / num_remaining
        saturation = 0.75 + (i % 3) * 0.08  # Slight variation in saturation
        value = 0.8 + (i % 4) * 0.05        # Slight variation in value
        
        # Convert HSV to RGB
        r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
        # Add alpha channel
        element_colors[element] = (r, g, b, 1.0)
    
    return element_colors

def create_cylinder_between_points(point1, point2, name="CustomCylinder"):
    """
    Create a cylinder between two points in Blender using Python.
    
    Args:
        point1 (tuple): The (x, y, z) coordinates of the first base center
        point2 (tuple): The (x, y, z) coordinates of the second base center
        radius (float): The radius of the cylinder
        name (str): The name of the created cylinder object
    
    Returns:
        bpy.types.Object: The created cylinder object
    """
    # Delete the default cube if it exists
    if "Cube" in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects["Cube"], do_unlink=True)
    
    # Convert points to vectors
    p1 = mathutils.Vector(point1)
    p2 = mathutils.Vector(point2)
    
    # Calculate the distance between the points (will be the height of the cylinder)
    distance = (p2 - p1).length
    
    # Create a cylinder
    bpy.ops.mesh.primitive_cylinder_add(
        radius=1.0, 
        depth=distance,
        vertices=32,  # Number of vertices on the circular base
        location=(0, 0, 0)
    )
    
    # Get the cylinder object
    cylinder = bpy.context.active_object
    cylinder.name = name
    cylinder.scale = (bond_thickness/2, bond_thickness/2, 1)
    
    # By default, the cylinder's axis is along the Z-axis
    # We need to rotate and position it to align between our two points
    
    # Calculate direction vector from p1 to p2
    direction = p2 - p1
    direction.normalize()
    
    # Calculate the rotation to align the cylinder with our direction
    # The default cylinder is aligned with the Z-axis (0, 0, 1)
    z_axis = mathutils.Vector((0, 0, 1))
    
    # Calculate the axis of rotation (cross product) and angle (dot product)
    axis = z_axis.cross(direction)
    if axis.length > 0.001:  # Check if cross product is not too small
        axis.normalize()
        angle = math.acos(min(1, max(-1, z_axis.dot(direction))))
        
        # Create rotation quaternion
        rotation = mathutils.Quaternion(axis, angle)
        cylinder.rotation_mode = 'QUATERNION'
        cylinder.rotation_quaternion = rotation
    
    # Position the cylinder midway between the two points
    midpoint = (p1 + p2) / 2
    cylinder.location = midpoint
    
    return cylinder



def get_material_info():
    global atom_info
    global bond_info
    global elem_list

    # Loading JSON data
    json_path = os.path.join(os.path.dirname(__file__), "materials_info.json")
    with open(json_path, "r") as file:
        data = json.load(file)
    
    all_atom_info = {}
    all_bond_info = {}

    # Accessing specific elements (assuming data is a dictionary)
    if isinstance(data, dict):
        if 'atom_info' in data:
            all_atom_info = data['atom_info']
        if 'bond_info' in data:
            all_bond_info = data['bond_info']
        

    for elem in elem_list:
        atom_info[elem] = all_atom_info[elem]
        bond_info[elem] = all_bond_info[elem]

    print(atom_info, bond_info)
    
    # return atom_info, bond_info


def list_bonds():
    """
    Estimate the list of bonds in the structure
    """
    global bond_cutoff_distance
    global atoms
    global bond_info

    num_atoms = len(atoms)
    bonds = []
    # print(bond_info)
    for ind1 in range(0, num_atoms):
        elem1, x1, y1, z1 = atoms[ind1]
        for ind2 in range(ind1, num_atoms):
            elem2, x2, y2, z2 = atoms[ind2]
            if (elem2 in bond_info[elem1] or elem1 in bond_info[elem2]):
                distance = ((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)**0.5
                if (distance < bond_cutoff_distance):
                    bond = {
                        "elem1_index": atoms[ind1],
                        "elem1": elem1,
                        "elem1_pos": (x1, y1, z1),
                        "elem2_index": atoms[ind2],
                        "elem2": elem2,
                        "elem2_pos": (x2, y2, z2)
                    }
                    bonds.append(bond)
    return bonds

def create_bonds():
    bonds = list_bonds()
    for bond in bonds:
        p1 = bond["elem1_pos"]
        p2 = bond["elem2_pos"]
        create_cylinder_between_points(p1, p2, name="bond")


def load_structure(file_path):
    global elem_list
    global atoms

    # Read the POSCAR file
    read_poscar(file_path)
    
    get_element_list()
    get_material_info()
    create_atom_spheres()
    create_bonds()
    
    # Organize atoms into collections by element type
    organize_into_collections()
    
    element_colors = get_periodic_table_colors()
    for elem in elem_list:
        color_collection(elem, color=element_colors[elem])

    # Reinitiazize the text fields 
    for scene in bpy.data.scenes:
        initialize_collections(scene)

    scene.bond_thickness_scene = bond_thickness


class LoadFileOperator(Operator, ImportHelper):
    """Load a file using the file browser"""
    bl_idname = "file.load_file_operator"
    bl_label = "Load File"
    
    # ImportHelper mixin class uses these properties
    filename_ext = "*.*"  # Accept all file types
    
    filter_glob: StringProperty(
        default="*.*",
        options={'HIDDEN'},
        maxlen=255,
    )
    
    def execute(self, context):
        filepath = self.filepath
        filename = os.path.basename(filepath)
        
        # Store the filepath in scene properties for reference
        context.scene.last_loaded_file = filepath
        
        # You can add specific file handling here depending on file type
        # For example, if it's an image:
        if filepath.lower().endswith(('.xyz')):
            try:
                # Load as image texture
                bpy.ops.image.open(filepath=filepath)
                self.report({'INFO'}, f"Image loaded: {filename}")
                load_structure(filepath)
                
            except Exception as e:
                self.report({'ERROR'}, f"Failed to load image: {str(e)}")
                return {'CANCELLED'}
        return {'FINISHED'}
    


# Panel class for the UI
class FILE_PT_loader_panel(Panel):
    global elem_list

    bl_label = "Atoms Visualizer"
    bl_idname = "FILE_PT_loader_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Atoms Visualizer'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # Display last loaded file
        if getattr(scene, "last_loaded_file", ""):
            box = layout.box()
            box.label(text="Last File:")
            box.label(text=os.path.basename(scene.last_loaded_file))

        layout.label(text="Load Structure:")
        row = layout.row()
        row.operator(LoadFileOperator.bl_idname, text=".xyz", icon='FILE')

        # Atomic Radius
        layout.label(text="Atomic Radius:")
        col = layout.column(align=True)
        
        ind = 0
        col = layout.column(align=True)
        for num in scene.atomic_radius:
            col.prop(num, "value", text=elem_list[ind])
            ind+=1

        # Bond Thickness
        layout.label(text="Bond Thickness:")
        layout.prop(scene, "bond_thickness_scene", text="")

        # Bond Cutoff Distance
        layout.label(text="Bond Cutoff Distance:")
        layout.prop(scene, "bond_cutoff_distance_scene", text="")
        

def update_atomic_radius(self, context):
    """
    Update scale of the specific atomic sphere that triggered the update.
    """
    global elem_list
    global current_atoms_info

    scene = context.scene

    # Identify which index in atomic_radius collection was updated
    index = None
    for i, prop in enumerate(scene.atomic_radius):
        if prop == self:
            index = i
            break

    if index is None:
        print("Could not determine the index of the updated atomic radius property.")
        return

    element = elem_list[index]

    for obj in bpy.data.objects:
        if obj.type == 'MESH' and obj.name.startswith(f"{element}_"):
            obj.scale = (self.value, self.value, self.value)
            current_atoms_info[element]['radius'] = self.value


def update_bond_thickness(self, context):
    global bond_thickness

    # Ensure that bond_thickness_scene is defined
    scene = context.scene
    if not hasattr(scene, "bond_thickness_scene"):
        print("Error: 'bond_thickness_scene' is not defined in the scene.")
        return

    bond_thickness = scene.bond_thickness_scene  # Retrieve bond thickness value

    for obj in bpy.data.objects:
        if obj.type == 'MESH' and obj.name.startswith("bond"):
            obj.scale.x = bond_thickness/2
            obj.scale.y = bond_thickness/2 
            obj.scale.z = 1  # Keep Z unchanged
            

def update_bond_cutoff_distance(self, context):
    global bond_cutoff_distance

    # Deselect all objects
    bpy.ops.object.select_all(action='DESELECT')

    # Loop over all objects and select the ones that start with "bond"
    for obj in bpy.data.objects:
        if obj.type == 'MESH' and obj.name.startswith("bond"):
            obj.select_set(True)

    # Delete selected objects
    bpy.ops.object.delete()

    # Ensure that bond_cutoff_distance_scene is defined
    scene = context.scene
    if not hasattr(scene, "bond_cutoff_distance_scene"):
        print("Error: 'bond_cutoff_distance_scene' is not defined in the scene.")
        return

    bond_cutoff_distance = scene.bond_cutoff_distance_scene  # Updated bond thickness value

    # Recreate bonds
    create_bonds()




class AtomPropertyGroup(PropertyGroup):
    value: FloatProperty(
        name="Atomic Radius", 
        default=1.0,
        min=0.1,
        max=4.0,
        update=update_atomic_radius
    )


# Register and add to the file menu
def menu_func(self, context):
    self.layout.operator(LoadFileOperator.bl_idname, text="Load File...")

# For storing the last loaded file path
def register_properties():
    bpy.types.Scene.last_loaded_file = StringProperty(
        name="Last Loaded File",
        description="Path to the last loaded file",
        default="",
        subtype='FILE_PATH'
    )

    bpy.types.Scene.atomic_radius = CollectionProperty(type=AtomPropertyGroup)
    bpy.types.Scene.bond_thickness_scene = FloatProperty(
        name="Current Bond Thickness",
        description="Controls the thickness of the bond",
        default=bond_thickness,
        min=0.01,
        max=0.5,
        update=update_bond_thickness
    )

    bpy.types.Scene.bond_cutoff_distance_scene = FloatProperty(
        name="Current Bond Formation",
        description="Controls whether bonds will form between atoms or not",
        default=bond_cutoff_distance,
        min=0,
        max=5,
        update=update_bond_cutoff_distance
    )

# Initialize collections with default values
def initialize_collections(scene):
    global elem_list
    global current_atoms_info

    # Clear existing collections to avoid duplicates
    scene.atomic_radius.clear()
    
    # Add items for each element
    for elem in elem_list:
        item = scene.atomic_radius.add()
        item.value = current_atoms_info[elem]['radius']



# You can store a reference to the handler so we can remove it later
def initialize_all_scenes(dummy=None):
    for scene in bpy.data.scenes:
        initialize_collections(scene)

def register():
    
    bpy.utils.register_class(AtomPropertyGroup)
    bpy.utils.register_class(LoadFileOperator)
    bpy.utils.register_class(FILE_PT_loader_panel)
    bpy.types.TOPBAR_MT_file.append(menu_func)
    register_properties()

    # Use a load-post handler to delay scene initialization
    bpy.app.handlers.load_post.append(initialize_all_scenes)

def unregister():
    del bpy.types.Scene.last_loaded_file
    bpy.utils.unregister_class(LoadFileOperator)
    bpy.utils.unregister_class(FILE_PT_loader_panel)
    bpy.utils.unregister_class(AtomPropertyGroup)
    del bpy.types.Scene.bond_thickness_scene
    bpy.types.TOPBAR_MT_file.remove(menu_func)


if __name__ == "__main__":
    register()