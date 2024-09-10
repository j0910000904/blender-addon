bl_info = {
    "name": "UV+",
    "author": "LinJunZhe",
    "version": (1, 0, 1),
    "blender": (2, 83, 0),
    "location": "View3D > Sidebar > UV+ ",
    "warning": "",
    "category": "UV"}
    

import bpy
import math
import bmesh
import time
from mathutils import Vector


def get_seams(bm): 

    objects_seams = []
 
    for e in bm.edges:
        if e.seam:
            objects_seams.append(e.index)
                
    return objects_seams 

def get_islands(bm):
    
    sel_islands = []
    seams = get_seams(bm)
    faces = set(bm.faces)
    while len(faces) != 0:
        
        init_face = faces.pop()
        island = [init_face]
        stack = [init_face]
        while len(stack) != 0:
            face = stack.pop()
            for e in face.edges:
                if e.index not in seams:
                    for f in e.link_faces:
                        if f != face and f not in island:
                            stack.append(f)
                            island.append(f)
                            
        uv = bm.loops.layers.uv.verify() 
        sel = []
        for f in island:
            faces.discard(f)
            for loop in f.loops:
                uvloop = loop[uv]
                if uvloop.select:
                    sel.append(uvloop)
        if len(sel) != 0 :
            sel_islands.append(sel)                        
    
    return sel_islands   

def icon_get(name):
    return preview_icons[name].icon_id

def icon_register(fileName):
    name = fileName.split('.')[0]   # Don't include file extension
    icons_dir = os.path.join(os.path.dirname(__file__), "icons")
    preview_icons.load(name, os.path.join(icons_dir, fileName), 'IMAGE')

    
def icon_unregister():

    preview_icons.clear() 
       
def get_uv_num(me):

    bm = bmesh.from_edit_mesh(me)
    uv_layer = bm.loops.layers.uv.verify()
    selected_uv = [] 
    for face in bm.faces:
        for loop in face.loops:
            uvloop =loop[uv_layer]
            if uvloop.select:
                selected_uv.append(uvloop)
    num = len(get_uv_num)
    
    return num       

    
def selected_uv(bm,uv,me):

    selected_uv = []
    for face in bm.faces:
        for loop in face.loops:
            uvloop =loop[uv]
            if uvloop.select:
                selected_uv.append(uvloop)

    return selected_uv        

def check_island(me):
    
    bm = bmesh.from_edit_mesh(me)
    uv_layer = bm.loops.layers.uv.verify()
    is_island = False
    sel = get_selected_uv(me)
    sel_count1 = get_uv_num(me)
    bpy.Ops.uv.select_linked()
    sel_count2 = get_uv_num(me)
    if sel_count1 == sel_count2 :
        is_island = True
    bpy.ops.uv.select_all(action='DESELECT')
    for v in sel:
        V.select = True
    bmesh.update_edit_mesh(me, True)
    
    return is_island
    
    
def getSelectionBBox():

    bbox = {}
        
    boundsMin = Vector((99999999.0,99999999.0))
    boundsMax = Vector((-99999999.0,-99999999.0))
    boundsCenter = Vector((0.0,0.0))
    countFaces = 0
    
    for obj in bpy.context.selected_objects:

        me = obj.data
        bm = bmesh.from_edit_mesh(me)
        uv_layer = bm.loops.layers.uv.verify()
                
        for face in bm.faces:
            if face.select:
                for loop in face.loops:
                    if loop[uv_layer].select is True:
                        uv = loop[uv_layer].uv
                        boundsMin.x = min(boundsMin.x, uv.x)
                        boundsMin.y = min(boundsMin.y, uv.y)
                        boundsMax.x = max(boundsMax.x, uv.x)
                        boundsMax.y = max(boundsMax.y, uv.y)
                
                        boundsCenter+= uv
                        countFaces+=1
        
        bbox['min'] = boundsMin
        bbox['max'] = boundsMax
        bbox['width'] = (boundsMax - boundsMin).x
        bbox['height'] = (boundsMax - boundsMin).y
        
        if countFaces == 0:
            bbox['center'] = boundsMin
        else:
            bbox['center'] = boundsCenter / countFaces

        bbox['area'] = bbox['width'] * bbox['height']
        bbox['minLength'] = min(bbox['width'], bbox['height'])
                
    return bbox

class UvplusProperties(bpy.types.PropertyGroup):

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
 
    move_distance : bpy.props.FloatProperty(
        name = "",
        description = "Move distance",
        default = 1,
        min = 0,
        max = 1,
        precision=2,
        )
        
    rotate_angle : bpy.props.FloatProperty(
        name = "",
        description = "Move distance",
        default = 90,
        min = 0,
        max = 180,
        precision=2,
        )    

class Align_Islands(bpy.types.Operator):
    bl_idname = "uv.uvplus_align_islands"
    bl_label = "align_islands"
    
    direction : bpy.props.StringProperty(name = "Direction", default = "top")

    @classmethod
    def poll(cls, context):

        # uvmode = context.scene.tool_settings.uv_select_mode
        return context.mode == "EDIT_MESH" 

    def execute(self, context):

        if bpy.context.scene.tool_settings.use_uv_select_sync:
        
            self.report({"WARNING"}, 'Please disable Sync Selection mode !')

        else: 

            bbox_all = getSelectionBBox()
            sel_obj = bpy.context.selected_objects

            for ob in sel_obj:
                
                bpy.ops.object.editmode_toggle()
                bpy.ops.object.select_all(action='DESELECT')
                ob.select_set(True)
                bpy.context.view_layer.objects.active = ob
                bpy.ops.object.editmode_toggle()
                me = ob.data
                bm = bmesh.from_edit_mesh(me)
                uv = bm.loops.layers.uv.verify()
                if context.scene.tool_settings.uv_select_mode == 'ISLAND' :
                    
                    islands = get_islands(bm)
                    print(len(islands))

                    for island in islands:
                        bpy.ops.uv.select_all(action='DESELECT')
                        for l in island:                        
                            l.select = True
                                
                        bbox_island = getSelectionBBox()
       
                        distance_max = bbox_all['max'] - bbox_island['max']
                        distance_min = bbox_all['min'] - bbox_island['min']
                    
                        if self.direction == "top" and distance_max.y != 0:
                        
                            bpy.ops.transform.translate(value=(0, distance_max.y, 0))

                        elif self.direction == "left" and distance_min.x != 0:
                            
                            bpy .ops.transform.translate(value=(distance_min.x, 0, 0))

                        elif self.direction == "right" and distance_max.x != 0:
                            
                            bpy.ops.transform.translate(value=(distance_max.x, 0, 0))

                        elif self.direction == "bottom" and distance_min.y != 0:
                            
                            bpy.ops.transform.translate(value=(0, distance_min.y, 0))
                    for island in islands:
                        for l in island:
                            l.select = True
                else:
                    for face in bm.faces:
                        for loop in face.loops:
                            loop = loop[uv]
                            if loop.select:
                                distance_max = bbox_all['max']
                                distance_min = bbox_all['min']
                                if self.direction == "top" :
                                    loop.uv.y = distance_max.y

                                elif self.direction == "left" :
                                    
                                    loop.uv.x = distance_min.x

                                elif self.direction == "right" :
                                    
                                    loop.uv.x = distance_max.x

                                elif self.direction == "bottom" :
                                    
                                    loop.uv.y = distance_min.y
       
            bpy.ops.object.editmode_toggle()    
            for ob in sel_obj:
                ob.select_set(True)
            bpy.ops.object.editmode_toggle()    

        return {'FINISHED'}
    


class Align_Island(bpy.types.Operator):
    bl_idname = "uv.uvplus_align_island"
    bl_label = "align_island"

    @classmethod
    def poll(cls, context):

        # uvmode = context.scene.tool_settings.uv_select_mode
        return context.mode == "EDIT_MESH" 

    def execute(self, context):

        if bpy.context.scene.tool_settings.use_uv_select_sync:
        
            self.report({"WARNING"}, 'Please disable Sync Selection mode !')

        else: 
            sel_obj = bpy.context.selected_objects
            if len(sel_obj) == 0 :
                bpy.context.active_object.select_set(True)
                sel_obj = bpy.context.selected_objects
            for ob in sel_obj:
  
                bpy.ops.object.editmode_toggle()
                bpy.ops.object.select_all(action='DESELECT')
                bpy.context.view_layer.objects.active = ob
                ob.select_set(True)
                bpy.ops.object.editmode_toggle()
                me = ob.data
                bm = bmesh.from_edit_mesh(me)
                uv = bm.loops.layers.uv.verify()

                islands = get_islands(bm)
                bpy.ops.uv.select_all(action='DESELECT')

                print(len(islands))
                for island in islands:
                    uvx = []
                    uvy = []
                    print(len(island))                    
                    for l in island:
                        print(l.uv)
                        if l.select == True:
                            
                            if l.uv.x not in uvx :
                                uvx.append(l.uv.x)
                            if l.uv.y not in uvy :
                                uvy.append(l.uv.y)

                    bpy.ops.uv.select_linked()
                    if len(uvx) == 1:
                        uvx.append(uvx[0])
                    if len(uvy) == 1:
                        uvy.append(uvy[0])

                    a = (uvx[1]-uvx[0])/2
                    b = (uvy[1]-uvy[0])/2

                    if a*b>0 :
                        if abs(a) >= abs(b) :
                            radian = -math.atan(b/a)
                        else :
                            radian = math.atan(a/b)
                    elif a*b<0 :
                        if abs(a) <= abs(b) :
                            radian = math.atan(a/b)
                        else:
                            radian = -math.atan(b/a)

                    else :
                        radian = 0
                    
                    bpy.ops.transform.rotate(value=radian, orient_axis='Z', orient_type='VIEW')
                    bpy.ops.uv.select_all(action='DESELECT')
                
                for island in islands:
                    for l in island:
                        l.select = True            

            bpy.ops.object.editmode_toggle()
            for ob in sel_obj:
                ob.select_set(True)            
            bpy.ops.object.editmode_toggle()
            
        return {'FINISHED'} 
    
    
    
class stitch(bpy.types.Operator):
    
    bl_idname = "uv.uvplus_stitch"
    bl_label = "stitch"

    @classmethod
    def poll(cls, context):

         # uvmode = context.scene.tool_settings.uv_select_mode
        return context.mode == "EDIT_MESH" 

    def execute(self, context):

        if bpy.context.scene.tool_settings.use_uv_select_sync:

            self.report({"WARNING"}, 'Please disable Sync Selection mode !')

        else :
            
            sel_obj = bpy.context.selected_objects

            for ob in sel_obj:

                bpy.ops.object.editmode_toggle()
                bpy.ops.object.select_all(action='DESELECT')
                bpy.context.view_layer.objects.active = ob
                ob.select_set(True)
                bpy.ops.object.editmode_toggle()
                me = ob.data
                bm = bmesh.from_edit_mesh(me)
                uv = bm.loops.layers.uv.verify()
                init_seams = get_seams(bm)
                bpy.ops.uv.stitch(use_limit=False, snap_islands=True, limit=0.01,clear_seams=True)
                cur_seams = get_seams(bm)

                if len(init_seams) == len(cur_seams) :
                    bpy.ops.uv.snap_selected(target='ADJACENT_UNSELECTED')
                    bpy.ops.uv.seams_from_islands()
                else :
                    while len(init_seams) != len(cur_seams):
                        init_seams = get_seams(bm)
                        bpy.ops.uv.stitch(use_limit=False, snap_islands=True, limit=0.01,clear_seams=True)
                        cur_seams = get_seams(bm)
            
                            
            bpy.ops.object.editmode_toggle()
            for ob in sel_obj:
                ob.select_set(True)
            bpy.ops.object.editmode_toggle()
                
            
                    
                    
        return {'FINISHED'} 

class cut(bpy.types.Operator):
    
    bl_idname = "uv.uvplus_cut"
    bl_label = "cut"

    @classmethod
    def poll(cls, context):

         # uvmode = context.scene.tool_settings.uv_select_mode
        return context.mode == "EDIT_MESH" 

    def execute(self, context):
        
        bpy.ops.uv.mark_seam(clear=False)

        bpy.ops.uv.uvplus_unwrap_selected()
        
        return {'FINISHED'} 
    
class split_uv(bpy.types.Operator):
    
    bl_idname = "uv.uvplus_split_uv"
    bl_label = "split_uv"

    @classmethod
    def poll(cls, context):

         # uvmode = context.scene.tool_settings.uv_select_mode
        return context.mode == "EDIT_MESH" 

    def execute(self, context):
        
        bpy.ops.uv.select_split()
        bpy.ops.transform.translate(value=(0.01, 0, 0))
        bpy.ops.uv.seams_from_islands()
        bpy.ops.transform.translate(value=(-0.01, 0, 0))
        bpy.ops.transform.translate('INVOKE_DEFAULT')
        
        return {'FINISHED'} 
    
            
class unwrap_selected(bpy.types.Operator):
    
    bl_idname = "uv.uvplus_unwrap_selected"
    bl_label = "unwrap selected"

    @classmethod
    def poll(cls, context):

         # uvmode = context.scene.tool_settings.uv_select_mode
        return context.mode == "EDIT_MESH" 

    def execute(self, context):

        if bpy.context.scene.tool_settings.use_uv_select_sync:

            self.report({"WARNING"}, 'Please disable Sync Selection mode !')

        else :
            

            sel_obj = bpy.context.selected_objects

            for ob in sel_obj:

                bpy.ops.object.editmode_toggle()
                bpy.ops.object.select_all(action='DESELECT')
                bpy.context.view_layer.objects.active = ob
                ob.select_set(True)
                bpy.ops.object.editmode_toggle()
                me = ob.data
                bm = bmesh.from_edit_mesh(me)
                uv = bm.loops.layers.uv.verify() 
                selected = selected_uv(bm,uv,me)
                print(len(selected))
                bpy.ops.uv.select_linked()
                island = selected_uv(bm,uv,me)
                bpy.ops.uv.select_all(action='DESELECT')
                bpy.ops.uv.select_all(action='SELECT')
                bpy.ops.uv.pin(clear=True)
                bpy.ops.uv.remove_doubles(threshold=0.0001)
                bpy.ops.uv.seams_from_islands()
                bpy.ops.uv.select_all(action='DESELECT')
                print(len(island))

                
                if  len(selected) == len(island) and len(selected)!=0 :

                    sel = []
                    for l in selected:
                        l.select = True
                    bmesh.update_edit_mesh(me)
                    for face in bm.faces:
                        for l in face.loops:
                            l = l[uv]
                            if l.select:
                                sel.append(l)
                    sel[0].select = False
                    sel[1].select = False              
                    bpy.ops.uv.select_all(action = 'INVERT')
                    bpy.ops.uv.pin(clear=False)
                    bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.001)
                    bpy.ops.uv.pin(clear=True)
                    bpy.ops.uv.select_all(action = 'INVERT')
                    sel[0].select = True
                    sel[1].select = True
                    
                elif len(selected)!=0 :
                    for l in selected:
                        l.select = True
                    bmesh.update_edit_mesh(me)    
                    bpy.ops.uv.select_all(action = 'INVERT')
                    bpy.ops.uv.pin(clear=False)
                    bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.001)
                    bpy.ops.uv.pin(clear=True)
                    bpy.ops.uv.select_all(action = 'INVERT')
                else:
                    pass    
             
            bpy.ops.object.editmode_toggle()
             
            for ob in sel_obj:
                ob.select_set(True)
            bpy.ops.object.editmode_toggle()
         
        return {'FINISHED'} 
    
""" move ============================================="""  

class move_uv(bpy.types.Operator):
    
    bl_idname = "uv.uvplus_move_uv"
    bl_label = "move_uv"
    
    direction : bpy.props.StringProperty(name = "Direction", default = "top")
    @classmethod
    def poll(cls, context):

         # uvmode = context.scene.tool_settings.uv_select_mode
        return context.mode == "EDIT_MESH" 

    def execute(self, context):

        if bpy.context.scene.tool_settings.use_uv_select_sync:

            self.report({"WARNING"}, 'Please disable Sync Selection mode !')

        else:
            distance = bpy.data.scenes['Scene'].uvplus.move_distance
         
        if self.direction == "top" :
            bpy.ops.transform.translate(value=(0, distance, 0))

        elif self.direction == "left" :
            bpy.ops.transform.translate(value=(-distance, 0, 0))

        elif self.direction == "right" :
            bpy.ops.transform.translate(value=(distance, 0, 0))

        elif self.direction == "bottom" :
            bpy.ops.transform.translate(value=(0, -distance, 0))

                
        return {'FINISHED'}  
    

""" Rotate ============================================= """                
class rotate_uv(bpy.types.Operator):
    
    bl_idname = "uv.uvplus_rotate_uv"
    bl_label = "rotate_uv"
    
    direction : bpy.props.StringProperty(name = "Direction", default = "right")
    @classmethod
    def poll(cls, context):

         # uvmode = context.scene.tool_settings.uv_select_mode
        return context.mode == "EDIT_MESH" 

    def execute(self, context):

        if bpy.context.scene.tool_settings.use_uv_select_sync:

            self.report({"WARNING"}, 'Please disable Sync Selection mode !')

        else:
            angle = math.radians(bpy.data.scenes['Scene'].uvplus.rotate_angle)

            if self.direction == "left" :
                bpy.ops.transform.rotate(value=angle, orient_axis='Z', orient_type='VIEW')

            if self.direction == "right" :
                bpy.ops.transform.rotate(value=-angle, orient_axis='Z', orient_type='VIEW')


                
        return {'FINISHED'}  
"""3D================================================================================="""
class AutoUnwrap(bpy.types.Operator):
    
    bl_idname = "uv.uvplus_autounwrap"
    bl_label = "Auto Unwrap"
    bl_options = {'REGISTER','UNDO'}
    
    angle : bpy.props.IntProperty(
            name = "Angle",
            description = "Angle",
            default = 30,
            min = -0,
            max = 360
            )
            
  
    def execute(self,context):
        bpy.context.space_data.overlay.show_edge_sharp = False

        if bpy.context.mode == "OBJECT" :
            
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.mark_seam(clear=True)
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.mesh.edges_select_sharp(sharpness= math.radians(self.angle)) 
            bpy.ops.mesh.mark_seam(clear=False)
            bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')
            bpy.ops.mesh.select_all(action='SELECT') 
            bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.03)
            bpy.ops.uv.select_all(action='SELECT')
            bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.03) 

        elif bpy.context.mode == "EDIT_MESH" :


            bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.mark_seam(clear=True)
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.mesh.edges_select_sharp(sharpness= math.radians(self.angle)) 
            bpy.ops.mesh.mark_seam(clear=False)
            bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')
            bpy.ops.mesh.select_all(action='SELECT') 
            bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.03)
            bpy.ops.uv.select_all(action='SELECT')
            bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.03)   

        else :
            
            self.report({"WARNING"}, '" AutoUnwrap " failed !')


        return {'FINISHED'}
    
class Unwrap(bpy.types.Operator):
    
    bl_idname = "uv.uvplus_unwrap"
    bl_label = "Unwrap"
    bl_options = {'REGISTER','UNDO'}

    margin : bpy.props.FloatProperty(
            name = "Margin",
            description = "Mrgin",
            default = 0.001,
            precision=4,
            min = 0,
            max = 1
            )
    def execute(self,context):
        
        bpy.context.space_data.overlay.show_edge_sharp = False
        if bpy.context.mode == "OBJECT" :
            
            bpy.ops.object.editmode_toggle()
            bpy.context.tool_settings.mesh_select_mode = (False, False,True)
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=self.margin)

        else :
            
            bpy.context.tool_settings.mesh_select_mode = (False, False,True)
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=self.margin)

        return {'FINISHED'}

""" Seams============================================="""    

class MarkSeam(bpy.types.Operator):
    bl_idname = "mesh.uvplus_mark_seam"
    bl_label = "Mark Seam" 
    
    @classmethod
    def poll(cls, context):
        return context.mode == "EDIT_MESH"    
    
    def execute(self,context):
        bpy.context.space_data.overlay.show_edge_sharp = False
        bpy.ops.mesh.mark_seam(clear=False)
        
        return {'FINISHED'}
    
class ClearSeam(bpy.types.Operator):
    
    bl_idname = "mesh.uvplus_clear_seam"
    bl_label = "clear Seam" 
    
    @classmethod
    def poll(cls, context):
        
        return context.mode == "EDIT_MESH"    
    
    def execute(self,context):
        
        bpy.context.space_data.overlay.show_edge_sharp = False
        bpy.ops.mesh.mark_seam(clear=True)        

        return {'FINISHED'}

""" PROJECTION ===========================================""" 
      
      
class Align_view(bpy.types.Operator):

    bl_idname = "mesh.uvplus_align_view"
    bl_label = "align view"
     
    
    @classmethod
    def poll(cls, context):
        return context.mode == "EDIT_MESH" 
    
    def execute(self,context):
        
        bpy.ops.view3d.view_axis(type='TOP', align_active=True)

        return {'FINISHED'}        
      
"""PANEL============================================="""

        
class VIEW3D_PT_UV_Plus_3D(bpy.types.Panel):
    
    
    bl_label = "UV+"
    bl_idname = "uvplus_3d_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'UV+'
    

    def draw(self, context):
        
        layout = self.layout
        
        view = context.space_data
        overlay = view.overlay
        
        row = layout.row(align = True)
        row.label(text = "Display options :")
        row = layout.row(align = True) 
        row.prop(overlay,"show_edge_sharp",icon = 'HIDE_OFF',text = "Sharp")
        row.prop(overlay,"show_edge_seams",icon = 'HIDE_OFF',text = "Seams")
            
        box = layout.box()   
        row = box.row(align = True)
        row.label(text = "Seam :",icon = 'FCURVE')
        row = box.row(align = True)
        row.operator('mesh.uvplus_clear_seam',text = 'Clear') 
        row.operator('mesh.uvplus_mark_seam',text = 'Mark') 
        
        split = layout.split()
        col = split.column(align=True)
        row = col.row(align=True)
        row.operator('uv.uvplus_unwrap',text = 'Unwrap')
        row = col.row(align=True)
        row.operator('uv.uvplus_autounwrap',text = 'Auto Unwrap')
        
class VIEW3D_PT_UV_Plus_Project(bpy.types.Panel):
    
    bl_label = "Planar Projection"
    bl_idname = "uvplus_project_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "UV+"
    bl_parent_id = "uvplus_3d_panel"
       
    def draw(self, context):
        

        layout = self.layout
        split = layout.split()
        col = split.column(align=True)

        row = col.row(align=True)
        row.operator('mesh.uvplus_align_view',text = 'Align View',icon = 'VIS_SEL_11')
        row = col.row(align=True)
        row.operator('uv.project_from_view',text = 'Project from view',icon = 'HIDE_OFF')

class VIEW3D_PT_UV_Plus_2D(bpy.types.Panel):

    bl_label = "UV+"
    bl_idname ="uvplus_2d_panel"
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "UV+"

    def draw( self, context):
        
        uvplus = bpy.data.scenes['Scene'].uvplus
        layout = self.layout
        col = layout.column(align=True)
        td = context.scene.td
#align_islands 
      
        row = col.row(align = True)   
        row.label(text="align:")
        row.operator('uv.uvplus_align_islands',text = " ",icon = 'CUBE').direction="top"
        row.label(text="")
        row = col.row(align = True)
        row.operator('uv.uvplus_align_islands',text = " ",icon = 'CUBE').direction="left"
        row.operator('uv.uvplus_align_islands',text = " ",icon = 'CUBE').direction="bottom"
        row.operator('uv.uvplus_align_islands',text = " ",icon = 'CUBE').direction="right"      
         
#MOVE

        row = col.row(align = True)
        row.label(text="move:")
        row.operator('uv.uvplus_move_uv',text = " ",icon = 'CUBE').direction="top"
        row.label(text="")
        row = col.row(align = True)
        row.operator('uv.uvplus_move_uv',text = " ",icon = 'CUBE').direction="left"
        row.prop(uvplus,'move_distance',text = "")
        row.operator('uv.uvplus_move_uv',text = " ",icon = 'CUBE').direction="right"
        row = col.row(align = True)        
        row.label(text="")
        row.operator('uv.uvplus_move_uv',text = " ",icon = 'CUBE').direction="bottom"
        row.label(text="")
        
#unwrap_selected   

        row = col.row()
        row.operator('uv.uvplus_unwrap_selected',text = "unwrap_selected")
        
#align_island  

        row = col.row()
        row.operator('uv.uvplus_align_island',text = "Align Island",icon = 'CUBE')  
        
#ROTATE  
  
        row = col.row(align = True)   
        row.operator('uv.uvplus_rotate_uv',text = " ",icon = 'CUBE').direction="left" 
        row.prop(uvplus,'rotate_angle',text = "")
        row.operator('uv.uvplus_rotate_uv',text = " ",icon = 'CUBE').direction="right"         
 
#cut

        row = col.row(align = True)
        row.operator('uv.uvplus_cut',text = "Cut")
        row = col.row(align = True)
        row.operator('uv.uvplus_stitch',text = "Stitch") 
        row = col.row(align = True)
        row.operator('uv.uvplus_split_uv',text = "Split") 
       
        row = col.row(align = True)
        row.operator('object.texel_density_check',text = "Get TD")
        row = col.row(align = True)
        			
        row.prop(td, "density_set")
        
        if td.units == '0':
            row.label(text="px/cm")
        if td.units == '1':
            row.label(text="px/m")
        if td.units == '2':
            row.label(text="px/in")
        if td.units == '3':
            row.label(text="px/ft") 
        row.operator("object.texel_density_set", text="Set TD") 
        row = col.row(align = True) 
        row.scale_y = 1.75
        row.operator("uvpackmaster2.uv_pack", text="pack") 
        
        
  

    
    
"""PieMenu============================================="""           
    
class VIEW3D_MT_UV_Plus_Pie(bpy.types.Menu):
    
    bl_label = "UV +"
    bl_idname = "pie.uvplus_pie"

    

    def draw(self, context):
        
        if context.area.type == "VIEW_3D":
            
            layout = self.layout
            active = context.active_object

            pie = layout.menu_pie() 
            pie.operator("mesh.uvplus_clear_seam", icon="FCURVE",text = "Clear Seam")  
            pie = layout.menu_pie() 
            pie.operator("mesh.uvplus_mark_seam", icon="FCURVE",text = "Mark Seam") 
            pie = layout.menu_pie() 
            pie.operator("uv.uvplus_unwrap", icon="OUTLINER_OB_SURFACE",text = "Unwrap")
            pie = layout.menu_pie() 
            pie.operator("uv.uvplus_autounwrap", icon="FUND",text = "Auto Unwrap")
        
        if context.area.type == "IMAGE_EDITOR":
            
            layout = self.layout
            active = context.active_object       
            pie = layout.menu_pie() 
            pie.operator("uv.uvplus_stitch", icon="FCURVE",text = "Stitch") 
            pie = layout.menu_pie() 
            pie.operator('uv.uvplus_alignisland',text = "Align Island")
            pie = layout.menu_pie() 
            pie.operator('uv.uvplus_unwrap_selected',text = "Unwrap")            
            pie = layout.menu_pie() 
            pie.operator('uv.select_linked',text = "Select Linked")  
            pie = layout.menu_pie()
            

classes = [
#   3D
    UvplusProperties,
    AutoUnwrap,
    ClearSeam,
    MarkSeam,
    Align_view,
    Unwrap,
#   2D
    stitch,
    unwrap_selected,
    move_uv,
    Align_Island,
    rotate_uv,
    Align_Islands,
    cut,
    split_uv,
#   Panel 
    VIEW3D_PT_UV_Plus_2D,
    VIEW3D_PT_UV_Plus_3D,
    VIEW3D_MT_UV_Plus_Pie,
    VIEW3D_PT_UV_Plus_Project,    

] 

addon_keymaps = []

def add_pie():
    
    kc = bpy.context.window_manager.keyconfigs.addon
    km = kc.keymaps.new(name = "Window",space_type='EMPTY')    
    kmi = km.keymap_items.new("wm.call_menu_pie",'Z','PRESS',shift = True)  
    kmi.properties.name = "pie.uvplus_pie"
    addon_keymaps.append((km,kmi))
         
def remove_pie():
    
    for km,kmi in addon_keymaps:
        
        km.keymap_items.remove(kmi)
        
    km.keymaps.clear() 
    
        
def register():

    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.uvplus = bpy.props.PointerProperty(type=UvplusProperties) 
    add_pie()    
    


def unregister():

    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.uvplus
    remove_pie()




if __name__ == "__main__":
    register()    