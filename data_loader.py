import json
import os
from typing import Dict, List, Tuple

AtomRecord = Tuple[str, float, float, float]


def normalize_rgba(color_value):
    if isinstance(color_value, (list, tuple)) and len(color_value) == 4:
        return tuple(float(channel) for channel in color_value)
    if isinstance(color_value, (list, tuple)) and len(color_value) == 3:
        return (float(color_value[0]), float(color_value[1]), float(color_value[2]), 1.0)
    return (0.8, 0.8, 0.8, 1.0)


class StructureLoader:
    @staticmethod
    def read_xyz(file_path: str) -> List[AtomRecord]:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        num_atoms = int(lines[0])
        atoms: List[AtomRecord] = []
        for i in range(num_atoms):
            line_index = i + 2
            atom_data = lines[line_index].split()
            element = atom_data[0]
            x, y, z = float(atom_data[1]), float(atom_data[2]), float(atom_data[3])
            atoms.append((element, x, y, z))

        return atoms


class MaterialRepository:
    def __init__(self, base_dir: str):
        self.json_path = os.path.join(base_dir, "materials_info.json")

    def load_for_elements(self, elements: List[str]) -> Tuple[Dict[str, Dict[str, object]], Dict[str, List[str]]]:
        data = {}
        if os.path.exists(self.json_path):
            with open(self.json_path, "r", encoding="utf-8") as f:
                data = json.load(f)

        all_atom_info = {}
        all_bond_info = {}
        if isinstance(data, dict):
            atom_info = data.get("atom_info", {})
            bond_info = data.get("bond_info", {})
            if isinstance(atom_info, dict):
                all_atom_info = atom_info
            if isinstance(bond_info, dict):
                all_bond_info = bond_info

        atom_info_for_scene: Dict[str, Dict[str, object]] = {}
        bond_info_for_scene: Dict[str, List[str]] = {}

        for elem in elements:
            info = dict(all_atom_info.get(elem, {"radius": 1.0, "color": (0.8, 0.8, 0.8, 1.0)}))
            info["radius"] = float(info.get("radius", 1.0))
            info["color"] = normalize_rgba(info.get("color", (0.8, 0.8, 0.8, 1.0)))
            atom_info_for_scene[elem] = info
            partners = all_bond_info.get(elem, [])
            bond_info_for_scene[elem] = partners if isinstance(partners, list) else []

        return atom_info_for_scene, bond_info_for_scene
