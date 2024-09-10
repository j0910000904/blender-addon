bl_info = {
    "name": "Normal Editor",
    "author": "LinJunZhe",
    "version": (1, 3, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Sidebar >Normal Editor",
    "description": "Normal_Editor",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Mesh"}


import bpy
import bmesh
import math
import time
import os 
from pathlib import Path
from sys import platform

value = 10000000000000000000


s = 0    
class SetVertexNormal(bpy.types.Operator):
    bl_idname = "mesh.set_vertex_normal"
    bl_label = "SetVertexNormal"

    direction : bpy.props.StringProperty(name="Direction", default="top") 

    @classmethod
    def poll(cls,context):
        return context.mode == "EDIT_MESH"   
    
    def execute(self,context):

        if self.direction == "X":
            bpy.ops.mesh.point_normal(target_location=(value,0,0),align=True)
        elif self.direction == "-X":
            bpy.ops.mesh.point_normal(target_location=(-value,0,0),align=True)
        elif self.direction == "Y":
            bpy.ops.mesh.point_normal(target_location=(0,value,0),align=True)
        elif self.direction == "-Y":
            bpy.ops.mesh.point_normal(target_location=(0,-value,0),align=True)
        elif self.direction == "Z":
            bpy.ops.mesh.point_normal(target_location=(0,0,value),align=True)
        elif self.direction == "-Z":
            bpy.ops.mesh.point_normal(target_location=(0,0,-value),align=True)

        return {'FINISHED'}
 
class CopyNormal(bpy.types.Operator):
    
    bl_idname = "mesh.copynormal_c"
    bl_label = "Copy Normal"
    bl_description = "Copy normal from selected"
    
    @classmethod
    def poll(cls, context):
        return context.mode == "EDIT_MESH" 

    def execute(self,context):
        obj = bpy.context.object
        me = obj.data
        bm = bmesh.from_edit_mesh(me)

        bm.verts.ensure_lookup_table()
        bm.faces.ensure_lookup_table()

        faces = [f for f in bm.faces if f.select and not f.hide]
        verts = [v for v in bm.verts if v.select and not v.hide]

        if len(faces) == 1 or len(verts) == 1:
            bpy.ops.mesh.normal_tools(mode='COPY')
            return {'FINISHED'}
        else :
            self.report({"WARNING"},'Can only copy one custom normal, vertex normal or face normal !')

        return {'FINISHED'}
    
class PasteNormal(bpy.types.Operator):
    
    bl_idname = "mesh.pastenormal_c"
    bl_label = "Paste Normal"
    bl_description = "Paste normal to selected"

    @classmethod
    def poll(cls, context):
        return context.mode == "EDIT_MESH"     

    def execute(self,context):
        
        bpy.ops.mesh.normal_tools(mode='PASTE')

        return {'FINISHED'}   

class Recalculate(bpy.types.Operator):
    
    bl_idname = "mesh.recalculate_c"
    bl_label = "Paste Normal"
    bl_description = "Recaculate outside"

    @classmethod
    def poll(cls, context):
        return context.mode == "EDIT_MESH"  

    def execute(self,context):
        
        bpy.ops.mesh.normal_make_consistent(inside=False)

        return {'FINISHED'}   
                          
class RotateNormal(bpy.types.Operator):
    
    bl_idname = "mesh.rotatenormal_c"
    bl_label = "Rotate Normal"
    bl_description = "Rotate normal"
    bl_options = {'REGISTER', 'UNDO'}
    
    aa : bpy.props.FloatProperty(
        name = "X",
        description = "Rotation angle of x axis",
        default = 0,
        min = -360,
        max = 360,
        )
    
    bb : bpy.props.FloatProperty(
        name = "Y",
        description = "Rotation angle of y axis",
        default = 0,
        min = -360,
        max = 360,
        )
    
    cc : bpy.props.FloatProperty(
        name = "Z",
        description = "Rotation angle of z axis",
        default = 0,
        min = -360,
        max = 360,
        )
        
    @classmethod
    def poll(cls, context):
        return context.mode == "EDIT_MESH"  

                  
    def execute(self,context):

        anglex = math.radians(self.aa)
        angley = math.radians(self.bb)
        anglez = math.radians(self.cc) 
        bpy.ops.transform.rotate_normal(value=anglex, orient_axis='X')
        bpy.ops.transform.rotate_normal(value=angley, orient_axis='Y')
        bpy.ops.transform.rotate_normal(value=anglez, orient_axis='Z')
        


        return {'FINISHED'} 
    
class FlipNormal(bpy.types.Operator):
    
    bl_idname = "mesh.flipnormal"
    bl_label = "Flip Normal"
    bl_description = "Flip normal"

    @classmethod
    def poll(cls, context):
        return context.mode == "EDIT_MESH"   

    def execute(self,context):
        
        bpy.ops.mesh.flip_normal()



        return {'FINISHED'}
    
class ResetNormal(bpy.types.Operator):
    
    bl_idname = "mesh.resetnormal_c"
    bl_label = "Reset Normal"
    bl_description = "Reset normal"

    @classmethod
    def poll(cls, context):
        return context.mode == "EDIT_MESH"      
    
    def execute(self,context):
        
        bpy.ops.mesh.normal_tools(mode='RESET')

        return {'FINISHED'} 

class NormalTransfer(bpy.types.Operator):

    bl_idname = "mesh.normal_transfer"
    bl_label = "normal transfer"
    bl_description = "Transfer normal from object to object"

    @classmethod
    def poll(cls, context):
        return context.mode == "OBJECT" and len(context.selected_objects) == 2      
    
    def execute(self,context):
        
        selected = []
        for i in range(len(bpy.context.selected_objects)):
            selected.append(bpy.context.selectable_objects[i])
        target = bpy.context.active_object
        selected.remove(target)
        i = selected[0]
        i.data.use_auto_smooth = True

         
        bpy.context.active_object.data.use_auto_smooth = True
        bpy.context.active_object.modifiers.new(name = 'name',type='DATA_TRANSFER')
        bpy.context.object.modifiers["name"].use_loop_data = True
        bpy.context.object.modifiers["name"].data_types_loops = {'CUSTOM_NORMAL'}
        bpy.context.object.modifiers["name"].object = i
        bpy.ops.object.shade_smooth()
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.modifier_apply( modifier="name")

        return {'FINISHED'} 

class SetTarget(bpy.types.Operator):

    bl_idname = "mesh.set_target_c"
    bl_label = "set target"
    bl_description = "Set transfer target"

    @classmethod
    def poll(cls, context):

        return context.mode == "EDIT_MESH"
    
    
    def execute(self,context):
        obj = bpy.context.object
        me = obj.data
        bm = bmesh.from_edit_mesh(me)

        bm.verts.ensure_lookup_table()
        verts = [v for v in bm.verts if v.select and not v.hide]

        if len(verts) == 0:

            self.report({"WARNING","Please select at least one vertex !"})

        selectmode = tuple(bpy.context.scene.tool_settings.mesh_select_mode)

        if selectmode != (True,False,False):
            self.report({"WARNING","Please set target in vertex mode !"})

        else:
            vg = bpy.context.object.vertex_groups.get('Vertex Normal Transfer Group') 

            if vg is not None:
                bpy.context.object.vertex_groups.remove(vg)
                bpy.ops.object.vertex_group_assign_new()
                bpy.context.object.vertex_groups.active.name = "Vertex Normal Transfer Group"
                
            else :

                bpy.ops.object.vertex_group_assign_new()
                bpy.context.object.vertex_groups.active.name = "Vertex Normal Transfer Group"
                

        return {'FINISHED'} 

class NormalRepair(bpy.types.Operator):

    bl_idname = "mesh.normal_repair"
    bl_label = "normal repair"
    bl_description = "Transfer normal from object to target"
    bl_options = {'REGISTER','UNDO'}

    @classmethod
    def poll(cls, context):

        return context.mode == "OBJECT" and len(context.selected_objects) == 2
    
    
    def execute(self,context):

        selected = bpy.context.selected_objects
        selected_o = bpy.context.selected_objects
        selected.remove(bpy.context.active_object)
        bpy.ops.mesh.customdata_custom_splitnormal_add()
        bpy.context.active_object.modifiers.new(name = 'repair', type='DATA_TRANSFER')
        bpy.context.active_object.modifiers["repair"].use_loop_data = True
        bpy.context.active_object.modifiers["repair"].data_types_loops = {'CUSTOM_NORMAL'}
        bpy.context.active_object.modifiers["repair"].loop_mapping = 'POLYINTERP_NEAREST'
        bpy.context.active_object.modifiers["repair"].vertex_group = "Vertex Normal Transfer Group"
        bpy.context.active_object.modifiers["repair"].object = selected[0]
        bpy.ops.object.modifier_apply(modifier="repair")

        for obj in selected_o:
            obj.select_set(True)

        return {'FINISHED'}  
        
class NPProperties(bpy.types.PropertyGroup):
    
    size : bpy.props.EnumProperty(
        name = "",
        items = (
            ('256','256 px',""),
            ('512','512 px',""),
            ('1024','1024 px',""),
            ('2048','2048 px',""),
            ('4096','4096 px',""),
            ('8192','8192 px',"")
            ),
            default = '1024'
        ) 
 
    bevelradius : bpy.props.FloatProperty(
        name = "Bevel Radius",
        description = "Bevel Radius",
        default = 1,
        min = 0,
        max = 1000,
        precision=2,
        )
    
    normal_map_format : bpy.props.EnumProperty(
        name = "",
        items = (
            ('POS_Y','OpenGL',""),
            ('NEG_Y','DirectX',"")),
            default = 'NEG_Y'
        )
    cage_extrusion : bpy.props.FloatProperty(
        name = "",
        description = "Cage Extrusion",
        default = 0.001,
        min = 0,
        max = 1000,
        precision=4,
        )  
    layout : bpy.props.BoolProperty(
        name = "Export Layout",
        default = True
        ) 
        
    lastbaked : bpy.props.StringProperty(
        name = "Last Baked",
        default = "none"
        )   
           

class AutoGenerateNormalMap(bpy.types.Operator):
    
    bl_idname = "mesh.autogeneratenormalmap"
    bl_label = "GenerateNormalMap"
    bl_description = "Auto generate normal map"

    @classmethod
    def poll(cls,context):
        return len(context.selected_objects) >= 1
        
    def execute(self,context):
        bpy.context.scene.render.engine = 'BLENDER_EEVEE'

        low = []
        high = []
        del_obj = []

        cage_extrusion = float(bpy.data.scenes['Scene'].nMap.cage_extrusion)
        
        bevelradius = bpy.data.scenes['Scene'].nMap.bevelradius
        format = bpy.data.scenes['Scene'].nMap.normal_map_format       
        size = int(bpy.data.scenes['Scene'].nMap.size)
        layout = bpy.data.scenes['Scene'].nMap.layout
        if len(context.selected_objects) > 1 :
            
            for ob in bpy.context.selected_objects:
                high.append(ob)
                
            high.remove(bpy.context.active_object)
            low.append(bpy.context.active_object)                    

        else:
            for ob in bpy.context.selected_objects:
                low.append(ob)
                
                
            bpy.ops.object.duplicate_move()
            del_obj.append(bpy.context.active_object)
            low[0].select_set(False)
        
                        
            for ob in bpy.context.selected_objects:
                high.append(ob)            
                
        #Bevel Material
        mat_b = bpy.data.materials.get("BevelMat")

        if mat_b is None:

            mat_b = bpy.data.materials.new(name="BevelMat")
        else :
            bpy.data.materials.remove(bpy.data.materials["BevelMat"])
            mat_b = bpy.data.materials.new(name="BevelMat")    

        bpy.data.materials['BevelMat'].use_nodes = True
        node_tree = bpy.data.materials["BevelMat"].node_tree
        node_1 = node_tree.nodes.new('ShaderNodeBevel')
        node_2 = node_tree.nodes['Principled BSDF']
        node_tree.links.new(node_1.outputs['Normal'], node_2.inputs['Normal'])
        bpy.data.materials["BevelMat"].node_tree.nodes["Bevel"].inputs[0].default_value = bevelradius

        for ob in high:
            if ob.data.materials:
                    # assign to 1st material slot
                    ob.data.materials[0] = mat_b
            else:
                    # no slots
                    ob.data.materials.append(mat_b)
        #Normal Generator Material
        mat_n = bpy.data.materials.get("Normal Map +")

        if mat_n is None:
            
            mat_n = bpy.data.materials.new(name="Normal Map +")
        else :
            
            bpy.data.materials.remove(bpy.data.materials["Normal Map +"])
            mat_n = bpy.data.materials.new(name="Normal Map +")
            
        bpy.data.materials['Normal Map +'].use_nodes = True    
        node_tree = bpy.data.materials["Normal Map +"].node_tree 
        node_1 = node_tree.nodes.new('ShaderNodeTexImage')
        node_1.image = bpy.data.images.new(name = "Normal Map",width = size,height = size)
        export_texture_name = node_1.image.name
        node_2 = node_tree.nodes['Principled BSDF']

            
        if low[0].data.materials:
                    
            low[0].data.materials[0] = mat_n
        else:
                   
            low[0].data.materials.append(mat_n)

        low[0].select_set(True)
        high[0].select_set(True)
                      
        bpy.context.view_layer.objects.active = low[0]  
        bpy.context.scene.render.engine = 'CYCLES'
        bpy.context.scene.cycles.bake_type = 'NORMAL'
        bpy.context.scene.render.bake.normal_g = format
        bpy.context.scene.render.bake.use_selected_to_active = True
        bpy.context.scene.render.bake.cage_extrusion = cage_extrusion
        node_tree.links.new(node_1.outputs['Color'], node_2.inputs['Normal'])  
        bpy.ops.object.bake(type='NORMAL')
        
#       remove items
        bpy.ops.object.select_all(action='DESELECT')
        if del_obj:
            bpy.context.scene.objects[del_obj[0].name].select_set(True)
        bpy.ops.object.delete(use_global=False)
        bpy.data.materials.remove(bpy.data.materials["BevelMat"])
        bpy.data.materials.remove(bpy.data.materials["Normal Map +"])
        
#        normal_preview
        
            
        preview_mat_name = bpy.context.active_object.name + "_N"
        preview_mat = bpy.data.materials.get(preview_mat_name)
        
        if preview_mat is None:

            preview_mat = bpy.data.materials.new(name=preview_mat_name)
        else :
            bpy.data.materials.remove(bpy.data.materials[preview_mat_name])
            preview_mat = bpy.data.materials.new(name=preview_mat_name)
            
        if low[0].data.materials:
                    
            low[0].data.materials[0] = preview_mat
        else:
                   
            low[0].data.materials.append(preview_mat)  
              
        bpy.data.materials[preview_mat_name].use_nodes = True    
        node_tree = bpy.data.materials[preview_mat_name].node_tree 
        p_node_1 = node_tree.nodes.new('ShaderNodeTexImage')
        p_node_2 = node_tree.nodes.new('ShaderNodeNormalMap')
        p_node_2.space = 'TANGENT'
        p_node_1.image = bpy.data.images[export_texture_name]
        p_node_3 = node_tree.nodes['Principled BSDF']
        
        if format == 'POS_Y' :
            node_tree.links.new(p_node_1.outputs['Color'], p_node_2.inputs['Color'])
            
        elif format == 'NEG_Y' :
            p_node_4 = node_tree.nodes.new('ShaderNodeSeparateRGB')
            p_node_5 = node_tree.nodes.new('ShaderNodeInvert')
            p_node_6 = node_tree.nodes.new('ShaderNodeCombineRGB')
            node_tree.links.new(p_node_1.outputs['Color'], p_node_4.inputs['Image'])
            node_tree.links.new(p_node_4.outputs['R'], p_node_6.inputs['R'])
            node_tree.links.new(p_node_4.outputs['G'], p_node_5.inputs['Color'])
            node_tree.links.new(p_node_5.outputs['Color'], p_node_6.inputs['G'])
            node_tree.links.new(p_node_4.outputs['B'], p_node_6.inputs['B'])
            node_tree.links.new(p_node_6.outputs['Image'], p_node_2.inputs['Color'])
              
        node_tree.links.new(p_node_2.outputs['Normal'], p_node_3.inputs['Normal'])        
        node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.05, 0.05, 0.05, 1)

        
        
#       save texture
        home_dir = str(Path.home())

        if platform == 'linux' or platform == 'win32' or platform == 'darwin':
            desktop_dir = os.path.join(home_dir, 'Desktop')
        else:
            raise RuntimeError("OS not supported")
        if layout == True :
            bpy.ops.object.select_all(action='DESELECT')
            low[0].select_set(True)
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.select_all(action='SELECT')
            layout_path = str(desktop_dir) +"\\" + str(bpy.data.images[export_texture_name].name + "_layout.png")
            bpy.ops.uv.export_layout(filepath=layout_path, size=(size, size))
            bpy.ops.object.editmode_toggle()

        im = bpy.data.images[export_texture_name]
        
        im.filepath_raw = str(desktop_dir) +"\\" + str(bpy.data.images[export_texture_name].name + ".tga")
        im.file_format = 'TARGA' 
        im.save()
        msg = "Baking Finished ! Texture had been saved to Desktop as " + str(bpy.data.images[export_texture_name].name)
        bpy.data.scenes['Scene'].nMap.lastbaked = bpy.data.images[export_texture_name].name
        self.report({"INFO"},msg)  
        bpy.data.images[export_texture_name].colorspace_settings.name = 'Raw'
        bpy.context.space_data.shading.type = 'MATERIAL'


        return {'FINISHED'}  
    
class AutoSharp(bpy.types.Operator):
    
    bl_idname = "mesh.unormal_autosharp"
    bl_label = "Auto Sharp"
    bl_options = {'REGISTER','UNDO'}
    
    angle : bpy.props.IntProperty(
            name = "Angle",
            description = "Angle",
            default = 30,
            min = -0,
            max = 360
            )
            
  
    def execute(self,context):
        
        selected = []
        for obj in bpy.context.selected_objects:
            selected.append(obj)
        for obj in selected: 
            obj.data.use_auto_smooth = True
            obj.data.auto_smooth_angle = 3.14159

        if bpy.context.mode == "OBJECT" :
            bpy.ops.object.shade_smooth()
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.mark_sharp(clear=True)
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.mesh.edges_select_sharp(sharpness= math.radians(self.angle)) 
            bpy.ops.mesh.mark_sharp(clear=False)
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.normal_tools(mode='RESET')
            bpy.ops.mesh.select_all(action='DESELECT')            
            bpy.ops.object.editmode_toggle()


        elif bpy.context.mode == "EDIT_MESH" :

            bpy.ops.object.editmode_toggle()
            bpy.ops.object.shade_smooth()
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.mark_sharp(clear=True)
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.mesh.edges_select_sharp(sharpness= math.radians(self.angle)) 
            bpy.ops.mesh.mark_sharp(clear=False)
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.normal_tools(mode='RESET')
            bpy.ops.mesh.select_all(action='DESELECT')
            
            


        else :
            
            self.report({"WARNING"}, '" AutoUnwrap " failed !')


        return {'FINISHED'}
        
class VIEW3D_PT_NormalEditorPanel(bpy.types.Panel):
    
    bl_label = "Normal Editor"
    bl_idname = "normal_editor_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Normal  Editor'

    
    def draw(self,context):


        layout = self.layout

        row = layout.row()
        row.operator('mesh.set_vertex_normal',text = '+X').direction = "X" 
        row.operator('mesh.set_vertex_normal',text = '+Y').direction = "Y"  
        row.operator('mesh.set_vertex_normal',text = '+Z').direction = "Z"  
        row = layout.row()
        row.operator('mesh.set_vertex_normal',text = '-X').direction = "-X" 
        row.operator('mesh.set_vertex_normal',text = '-Y').direction = "-Y"  
        row.operator('mesh.set_vertex_normal',text = '-Z').direction = "-Z"   
        row = layout.row()
        row.operator('mesh.copynormal_c',text = 'Copy')
        row.operator('mesh.pastenormal_c',text = 'Paste')
        row = layout.row()
        row.operator('mesh.flipnormal',text = 'Flip      ',icon = 'UV_SYNC_SELECT') 
        row = layout.row()
        row.operator('mesh.rotatenormal_c',text = 'Rotate      ',icon = 'SNAP_NORMAL')
        row = layout.row()
        row.operator('mesh.smooth_normal',text = 'Smooth      ',icon = 'MOD_CURVE')
        row = layout.row()
        row.operator('mesh.merge_normal',text = 'Soft',icon = 'NORMAL_VERTEX')  
        row.operator('mesh.split_normal',text = 'Hard',icon = 'NORMAL_VERTEX_FACE')      
        row = layout.row()
        row.operator('mesh.normal_transfer',text = 'Noramls Transfer     ',icon = 'XRAY')
        row = layout.row()
        row.operator('mesh.recalculate_c',text = 'Recalculate     ',icon = 'FACE_MAPS')
        row = layout.row()
        row.operator("mesh.unormal_autosharp", icon="MESH_ICOSPHERE",text = "AutoSharp")
        row = layout.row()
        row.scale_y = 1.8
        row.operator('mesh.resetnormal_c',text = 'Reset     ',icon = 'FILE_REFRESH') 
        
        box = layout.box()
        row = box.row(align=True)
        row.label(text = "Vertex Normal Transfer :",icon = 'OUTLINER_OB_POINTCLOUD')
        row = box.row(align=True)
        row.operator('mesh.set_target_c',text = 'Set Target    ',icon = 'RESTRICT_SELECT_OFF') 
        row.operator('mesh.normal_repair',text = 'Transfer    ',icon = 'ARROW_LEFTRIGHT')  
           
        
class VIEW3D_PT_NormalEditorDisplayPanel(bpy.types.Panel):
    
    bl_label = "Display Options :"
    bl_idname = "normal_editor_display_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Normal  Editor'
    bl_parent_id = "normal_editor_panel"

    
    def draw(self,context):
        
        view = context.space_data
        overlay = view.overlay
        shading = view.shading
        layout = self.layout
        box = layout.box()
        box.prop(shading,"show_backface_culling")
        box.prop(overlay,"show_face_orientation")
        col = layout.column_flow(align = True)
        col.operator('object.shade_smooth')
        col.operator('object.shade_flat')
        
        box = layout.box()
        box.prop(overlay,"show_split_normal",text = "Show Normal")
        row = layout.row()
        box.prop(overlay,"normal_length")
        if context.active_object:    
            data = context.object.data
            box = layout.box()
            box.prop(data,"use_auto_smooth")
            row = layout.row()
            box.prop(data,"auto_smooth_angle",text = "Angle")
        
class VIEW3D_PT_NormalMapPlus(bpy.types.Panel):
    
    bl_label = "Normal Map +"
    bl_idname = "normal_map_plus_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Normal  Editor'


    
    def draw(self,context):
        
        layout = self.layout
        row = layout.row() 
        col = layout.row()
        nMap = context.scene.nMap
        row = layout.row()
        row.prop(nMap, "layout")
        
        row = layout.row()
        row.label(text = "Texture Size :")

        row.prop(nMap, "size")
        row = layout.row()
        row.label(text = "Bevel Radius :")  
        row.prop(nMap, "bevelradius",text = "")
        row = layout.row()
        row.label(text = "Format :")  
        row.prop(nMap, "normal_map_format",text = "")
        row = layout.row()
        row.label(text = "Ray Distace :")  
        row.prop(nMap, "cage_extrusion",text = "")        
        row = layout.row()
        row.scale_y = 1.7
        row.operator('mesh.autogeneratenormalmap',text = 'Generate')
        row = layout.row()
        box = layout.box()
        box.label(text = "Baked Maps  :")
        box = box.box()
        box.label(text = bpy.data.scenes['Scene'].nMap.lastbaked) 
"""PieMenu============================================="""           
    
class VIEW3D_MT_Normal_Editor_Pie(bpy.types.Menu):
    
    bl_label = "Normal Editor Pie"
    bl_idname = "pie.normal_editor_pie"

    

    def draw(self, context):
        
        if context.area.type == "VIEW_3D":
            view = context.space_data
            overlay = view.overlay
            layout = self.layout
            active = context.active_object
            
            shading = view.shading
        
        
            pie = layout.menu_pie() 
            pie.operator('mesh.merge_normal',text = 'Soft',icon = 'NORMAL_VERTEX')
            pie = layout.menu_pie() 
            pie.operator('mesh.split_normal',text = 'Hard',icon = 'NORMAL_VERTEX_FACE') 
            pie = layout.menu_pie() 
            pie.operator("mesh.unormal_autosharp", icon="MESH_ICOSPHERE",text = "AutoSharp")
            
            
            pie = layout.menu_pie() 
            box = pie.box()
            
            row = box.row()
            row.prop(overlay,"show_face_orientation")
            row = box.row()
            row.prop(overlay,"show_split_normal",text = "Show Normal")
            row = box.row()
            row.prop(overlay,"normal_length")
            row = box.row(align = True) 
            row.operator('mesh.set_vertex_normal',text = '+X').direction = "X" 
            row.operator('mesh.set_vertex_normal',text = '+Y').direction = "Y"  
            row.operator('mesh.set_vertex_normal',text = '+Z').direction = "Z"  
            row = box.row(align = True) 
            row.operator('mesh.set_vertex_normal',text = '-X').direction = "-X" 
            row.operator('mesh.set_vertex_normal',text = '-Y').direction = "-Y"  
            row.operator('mesh.set_vertex_normal',text = '-Z').direction = "-Z" 
            
            
            
            pie = layout.menu_pie() 
            pie.operator("mesh.flipnormal", icon="UV_SYNC_SELECT",text = "Flip")
            pie = layout.menu_pie()
            pie.operator("mesh.recalculate_c", icon="FACE_MAPS",text = "Recalculate")
            
            pie = layout.menu_pie()
            pie.operator('mesh.resetnormal_c',text = 'Reset     ',icon = 'FILE_REFRESH') 
            pie = layout.menu_pie()
            row = pie.row(align = True) 
            row.operator('mesh.copynormal_c',text = 'Copy')
            row.operator('mesh.pastenormal_c',text = 'Paste')
            
            
        
   
classes = [
    
    SetVertexNormal,
    CopyNormal,
    PasteNormal,
    RotateNormal,
    FlipNormal,
    ResetNormal,
    Recalculate,
    NormalTransfer,
    NormalRepair,
    VIEW3D_PT_NormalEditorPanel,
    VIEW3D_PT_NormalEditorDisplayPanel,
    NPProperties,
    AutoGenerateNormalMap,
    VIEW3D_PT_NormalMapPlus,
    SetTarget,
    VIEW3D_MT_Normal_Editor_Pie,
    AutoSharp



]


addon_keymaps = []
keymap_items = [
    ['3D View','VIEW_3D','wm.call_menu_pie','Z','PRESS',False,False,False,'pie.normal_editor_pie'],
    ['3D View Generic','VIEW_3D','wm.call_menu_pie','Z','PRESS',False,False,False,'pie.normal_editor_pie'],

]

def keymap_register(wm):
    for items in keymap_items:
        (area_name, space,
            item_id, button, value,
            shift_state, ctrl_state, alt_state,
            pie_name) = items
        km = wm.keyconfigs.addon.keymaps.new(name=area_name, space_type=space)
        kmi = km.keymap_items.new(
            item_id, button, value,
            shift=shift_state, ctrl=ctrl_state, alt=alt_state
        )
        if pie_name:
            kmi.properties.name = pie_name
        addon_keymaps.append((km, kmi))
        
def remove_pie():
    
    for km,kmi in addon_keymaps:
        
        km.keymap_items.remove(kmi)
        
    km.keymaps.clear() 
            
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.nMap = bpy.props.PointerProperty(type=NPProperties) 
    wm = bpy.context.window_manager

    if wm.keyconfigs.addon:
        keymap_register(wm)

   


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.nMap
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        for km, kmi in addon_keymaps:
            km.keymap_items.remove(kmi)
    addon_keymaps.clear()


if __name__ == "__main__":
    register()
