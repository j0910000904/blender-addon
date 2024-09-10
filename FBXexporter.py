bl_info = {
    "name": "FBX Batch Exporter",
    "blender": (2, 80, 0),
    "category": "Object",
}

import bpy
import os

class FBXExporterPanel(bpy.types.Panel):
    bl_label = "FBX Batch Exporter"
    bl_idname = "OBJECT_PT_fbx_exporter"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Export'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        export_tool = scene.export_tool

        layout.prop(export_tool, "export_path")
        layout.operator("object.batch_export_fbx", text="Export")

class BatchExportFBX(bpy.types.Operator):
    bl_idname = "object.batch_export_fbx"
    bl_label = "Batch Export FBX"

    def execute(self, context):
        scene = context.scene
        export_tool = scene.export_tool

        export_path = bpy.path.abspath(export_tool.export_path)

        for obj in bpy.context.selected_objects:
            if obj.type == 'MESH':  # 只导出网格物体
                original_location = obj.location.copy()
                obj.location = (0, 0, 0)
                file_name = obj.name + ".fbx"
                full_path = os.path.join(export_path, file_name)

                bpy.ops.export_scene.fbx(
                    filepath=full_path, 
                    use_selection=True, 
                    mesh_smooth_type='OFF', 
                    axis_forward='-Z', 
                    axis_up='Y'
                )

                obj.location = original_location
                self.report({'INFO'}, f"Exported {obj.name} to {full_path}")
        return {'FINISHED'}

class ExportToolProperties(bpy.types.PropertyGroup):
    export_path: bpy.props.StringProperty(
        name="Target Folder",
        description="Choose the target folder for FBX export",
        default="",
        maxlen=1024,
        subtype='DIR_PATH'
    )

def register():
    bpy.utils.register_class(FBXExporterPanel)
    bpy.utils.register_class(BatchExportFBX)
    bpy.utils.register_class(ExportToolProperties)
    bpy.types.Scene.export_tool = bpy.props.PointerProperty(type=ExportToolProperties)

def unregister():
    bpy.utils.unregister_class(FBXExporterPanel)
    bpy.utils.unregister_class(BatchExportFBX)
    bpy.utils.unregister_class(ExportToolProperties)
    del bpy.types.Scene.export_tool

if __name__ == "__main__":
    register()
