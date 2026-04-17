import os

from bpy.props import StringProperty
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper

from .controller import get_controller


class LoadFileOperator(Operator, ImportHelper):
    bl_idname = "file.load_file_operator"
    bl_label = "Load File"

    filename_ext = "*.*"

    filter_glob: StringProperty(
        default="*.*",
        options={"HIDDEN"},
        maxlen=255,
    )

    def execute(self, context):
        filepath = self.filepath
        filename = os.path.basename(filepath)
        context.scene.last_loaded_file = filepath

        if not filepath.lower().endswith(".xyz"):
            self.report({"ERROR"}, "Only .xyz files are supported")
            return {"CANCELLED"}

        try:
            get_controller().load_structure(filepath)
            self.report({"INFO"}, f"Structure loaded: {filename}")
            return {"FINISHED"}
        except Exception as exc:
            self.report({"ERROR"}, f"Failed to load structure: {str(exc)}")
            return {"CANCELLED"}
