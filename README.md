# Atoms Visualizer

A simple Blender addon to load and visualize atomic structures from `.xyz` files.

---

## 📦 Addon Info

- **Name:** Atoms Visualizer  
- **Author:** Albert Linda  
- **Version:** 0.0.1  
- **Blender Support:** 2.80+  
- **Category:** Import-Export  
- **Location in Blender:** 3D Viewport → Sidebar (`N` key) → Atoms Visualizer tab  
- **Description:** Load atomic positions from `.xyz` files and visualize them as spheres and bonds in the 3D viewport.

---

## 🚀 Installation

1. Download the `.zip` file.
2. Open **Blender**.
3. Go to `Edit` → `Preferences` → `Add-ons`.
4. Click **Install...** and select the `atoms_visualizer.py` file.
5. Enable the **Atoms Visualizer** addon in the list.
6. You will find the addon in the **Sidebar (`N` key)** under the **Atoms Visualizer** tab.

---

## 📁 Additional Setup

The addon requires a `materials.json` file to load element-specific properties like atomic radius and bond thickness.

### ➕ Step: Copy `materials.json`

Copy the provided `materials.json` file to Blender's **addons directory**:

#### 🔧 Linux
```
~/.config/blender/[your_blender_version]/scripts/addons/
```

#### 🔧 Windows
```
%APPDATA%\Blender Foundation\Blender[your_blender_version]\scripts\addons\
```

> 🔁 Replace `[your_blender_version]` with your installed Blender version, e.g., `3.6`.

After copying, **restart Blender** to apply changes.

---

## 📤 Features

- ✅ Import atomic structures from `.xyz` files.
- ✅ Automatically assign atomic radii and display bonds.
- ✅ Customize atomic and bond visuals through the UI.
- ✅ Simple and lightweight, designed for quick inspection and visualization.

---
