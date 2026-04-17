# Atoms Visualizer

A simple Blender addon to load and visualize atomic structures from `.xyz` files.

---

## 📦 Addon Info

- **Name:** Atoms Visualizer  
- **Author:** Albert Linda  
- **Blender Support:** 2.80+  
- **Category:** Import-Export  
- **Location in Blender:** 3D Viewport → Sidebar (`N` key) → Atoms Visualizer tab  
- **Description:** Load atomic positions from `.xyz` files and visualize them as spheres and bonds in the 3D viewport.

---

## 🚀 Installation

Install this addon as a **zip package** (multi-file addon), not as a single `.py` file.

1. Create a folder named `atoms_visualizer` containing:
	- `__init__.py`
	- `addon.py`
	- `atoms_visualizer.py`
	- `controller.py`
	- `data_loader.py`
	- `operators.py`
	- `props.py`
	- `scene_builder.py`
	- `state.py`
	- `ui.py`
	- `materials_info.json`
2. Zip that folder (the zip should contain the `atoms_visualizer/` directory at top level).
3. Open **Blender**.
4. Go to `Edit` → `Preferences` → `Add-ons`.
5. Click **Install...** and select the zip file.
6. Enable the **Atoms Visualizer** addon in the list.
7. You will find the addon in the **Sidebar (`N` key)** under the **Atoms Visualizer** tab.

---

## 📁 Data Files

The addon uses one data source inside the addon package:

- `materials_info.json`: atom metadata (radius + color) and bond rules.

---

## 📤 Features

- ✅ Import atomic structures from `.xyz` files.
- ✅ Automatically assign atomic radii and element colors for all elements.
- ✅ Display bonds using configurable bond rules.
- ✅ Customize atomic and bond visuals through the UI.
- ✅ Simple and lightweight, designed for quick inspection and visualization.

---
