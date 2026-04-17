# Atoms Visualizer

A Blender addon for loading and visualizing atomic structures from `.xyz` files. Atoms are rendered as
shaded spheres with configurable materials, and bonds are generated automatically based on element
compatibility rules.

---

## Addon Information

| Field       | Value                                              |
|-------------|----------------------------------------------------|
| Name        | Atoms Visualizer                                   |
| Author      | Albert Linda                                       |
| Version     | 0.2.0                                              |
| Blender     | 2.80 and above                                     |
| Category    | Import-Export                                      |
| Location    | 3D Viewport > Sidebar (N) > Atoms Visualizer       |

---

## Installation

This addon must be installed as a **zip package** (multi-file addon).

1. Ensure the following files are inside a folder named `atoms_visualizer`:

   ```
   atoms_visualizer/
   ├── __init__.py
   ├── addon.py
   ├── atoms_visualizer.py
   ├── controller.py
   ├── data_loader.py
   ├── operators.py
   ├── props.py
   ├── scene_builder.py
   ├── state.py
   ├── ui.py
   └── materials_info.json
   ```

2. Compress the folder into a `.zip` archive. The zip must contain the `atoms_visualizer/`
   directory at its top level.
3. Open Blender and navigate to `Edit > Preferences > Add-ons`.
4. Click **Install...** and select the zip file.
5. Enable the **Atoms Visualizer** entry in the add-ons list.
6. Open the Sidebar in the 3D Viewport (`N` key) and switch to the **Atoms Visualizer** tab.

---

## Data Source

All element metadata is stored in `materials_info.json` inside the addon package:

- **`atom_info`** — atomic radius and base RGBA color for all 118 elements.
- **`bond_info`** — per-element list of compatible bonding partners for covalent bond display.

---

## Features

- Import atomic structures from standard `.xyz` files.
- Automatic assignment of atomic radii and element colors sourced from `materials_info.json`.
- Bond generation based on element compatibility rules with a configurable cutoff distance.
- Per-element radius sliders and color pickers in the sidebar.
- Six material style presets: PBR, Metal, Glass, Plastic, Matte, Glow.
- Per-material controls: Metallic, Translucency, and Glossiness.
- Smooth shading applied via Geometry Nodes modifier.
- Automatic sun light placement sized relative to the structure's bounding sphere.
- Automatic camera framing in an isometric-style perspective view.

---

## UI Controls

| Control               | Description                                                    |
|-----------------------|----------------------------------------------------------------|
| Load .xyz             | Open a file browser to load an XYZ structure file             |
| Atomic Radius & Color | Per-element radius slider and base color picker                |
| Bond Thickness        | Uniform scale of all bond cylinders                           |
| Bond Cutoff Distance  | Maximum interatomic distance at which a bond is drawn         |
| Material              | Material style preset applied to all atom materials           |
| Metallic              | Metallic weight (PBR mode)                                    |
| Translucency          | Transmission weight (PBR mode)                                |
| Glossiness            | Inverse roughness (PBR mode)                                  |

---

## Project Structure

```
atoms_visualizer/
├── addon.py          — Addon entry point: bl_info, register/unregister, load_post handler
├── atoms_visualizer.py — Thin compatibility wrapper re-exporting from addon.py
├── controller.py     — Orchestrates load pipeline and UI update callbacks
├── data_loader.py    — Pure-Python XYZ file reader and JSON material loader
├── operators.py      — Blender operator for the file load action
├── props.py          — Scene property definitions and update callbacks
├── scene_builder.py  — All Blender scene construction: spheres, bonds, materials, lighting, camera
├── state.py          — Shared application state dataclass
├── ui.py             — Sidebar panel layout
└── materials_info.json — Element metadata: radius, color, bond partners
```

---

## Requirements

- Blender 2.80 or later.
- No external Python packages required; all dependencies are part of Blender's built-in environment.
