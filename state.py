from dataclasses import dataclass, field
from typing import Dict, List, Tuple

AtomRecord = Tuple[str, float, float, float]


@dataclass
class VisualizerState:
    elem_list: List[str] = field(default_factory=list)
    current_atoms_info: Dict[str, Dict[str, object]] = field(default_factory=dict)
    bond_thickness: float = 0.2
    bond_cutoff_distance: float = 3.0
    atom_metallic: float = 0.35
    atom_translucency: float = 0.18
    atom_glossiness: float = 0.82
    material_style: str = "PBR"
    atoms: List[AtomRecord] = field(default_factory=list)
    atom_info: Dict[str, Dict[str, object]] = field(default_factory=dict)
    bond_info: Dict[str, List[str]] = field(default_factory=dict)

    def reset_structure(self) -> None:
        self.elem_list = []
        self.current_atoms_info = {}
        self.atoms = []
        self.atom_info = {}
        self.bond_info = {}


state = VisualizerState()
