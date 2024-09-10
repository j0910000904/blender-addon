bl_info = {
    "name": "Duplicate Master",
    "author": "LinJunZhe",
    "version": (2, 0, 2),
    "blender": (4, 2, 0),
    "location": "View3D > Object context Menu",
    "description": "Duplicate Master ",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Mesh"}

import bpy
import math

def deselect_all():
    
    bpy.ops.object.select_all(action='DESELECT')


def set_pivot_to_cursor():
    
    bpy.context.scene.tool_settings.transform_pivot_point = 'CURSOR'


def restore_pivot(pre_mode):
    
    bpy.context.scene.tool_settings.transform_pivot_point = pre_mode

class DP_mirror(bpy.types.Operator):
    
    bl_idname = "mesh.dp__mirror"
    bl_label = "Duplicate Master Mirror"
    bl_description = "Mirror objects ( use the CURSOR's location as the center )"
    bl_options = {'REGISTER', 'UNDO'}

    link: bpy.props.BoolProperty(name="link", default=True)
    direction: bpy.props.EnumProperty(
        name="",
        items=[('X', 'X', ""), ('Y', 'Y', ""), ('Z', 'Z', ""), ('XYZ', 'Cursor Axis', "")],
        default='X'
    )

    @classmethod
    def poll(cls, context):
        return context.mode == "OBJECT" and len(context.selected_objects) > 0

    def execute(self, context):
        duplicates = []
        selected = bpy.context.selected_objects[:]
        original_orientation = bpy.context.scene.transform_orientation_slots[0].type

        bpy.context.scene.transform_orientation_slots[0].type = 'GLOBAL'
        pre_pivot = bpy.context.scene.tool_settings.transform_pivot_point
        set_pivot_to_cursor()

        for obj in selected:
            if obj not in duplicates:
                deselect_all()
                obj.select_set(True)
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.select_linked(type='OBDATA')

                bpy.ops.object.make_single_user(object=False, obdata=True, material=False, animation=False)
                bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
                bpy.ops.object.make_links_data(type='OBDATA')

                duplicates += bpy.context.selected_objects

                if self.link:
                    bpy.ops.object.duplicate_move_linked()
                else:
                    bpy.ops.object.duplicate_move()

                if self.direction == 'X':
                    bpy.ops.transform.mirror(constraint_axis=(True, False, False))
                elif self.direction == 'Y':
                    bpy.ops.transform.mirror(constraint_axis=(False, True, False))
                elif self.direction == 'Z':
                    bpy.ops.transform.mirror(constraint_axis=(False, False, True))
                elif self.direction == 'XYZ':
                    bpy.context.scene.transform_orientation_slots[0].type = 'CURSOR'
                    bpy.ops.transform.mirror(constraint_axis=(True, False, False))
                    bpy.ops.transform.mirror(constraint_axis=(False, True, False))
                    bpy.ops.transform.mirror(constraint_axis=(False, False, True))

        for ob in set(duplicates):
            ob.select_set(True)

        restore_pivot(pre_pivot)
        bpy.context.scene.transform_orientation_slots[0].type = original_orientation
        bpy.context.view_layer.objects.active = selected[0]
        return {'FINISHED'}
    
class DP_join(bpy.types.Operator):
    
    bl_idname = "mesh.dp_join"
    bl_label = "Duplicate Master Join"
    bl_description = "Join selected objects ( Automatically fix up the inverse faces and doubles vertices )"
    bl_options = {'REGISTER', 'UNDO'}

    distance: bpy.props.FloatProperty(
        name="Merge Distance",
        description="Merge Distance",
        default=0.005,
        max=1000,
        min=0,
        precision=3,
    )

    @classmethod
    def poll(cls, context):
        return context.mode == "OBJECT" and len(context.selected_objects) > 0

    def execute(self, context):
        bpy.ops.object.join()
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.select_mode(use_extend=False, use_expand=True, type='VERT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.remove_doubles(threshold=self.distance)
        bpy.ops.mesh.select_mode(use_extend=False, use_expand=True, type='FACE')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.normals_make_consistent(inside=False)
        bpy.ops.object.editmode_toggle()
        return {'FINISHED'}  

class DP_circular_array(bpy.types.Operator):

    bl_idname = "mesh.dp_circular_array"
    bl_label = "Circular Array"
    bl_description = "Circular Array ( use the CURSOR's location as the center )"
    bl_options = {'REGISTER','UNDO'}

    link : bpy.props.BoolProperty(name="link", default=True) 

    count : bpy.props.IntProperty(
        name = "Count",
        description = "Number Of Copies",
        default = 6,
        min = 2
        )  
    degree : bpy.props.FloatProperty(
        name = "Degree",
        description = "Rotate Angle",
        default = 360,
        max = 360,
        min = -360
        ) 
    orient_axis : bpy.props.EnumProperty(
        name = "Axis",
        description = "Orient Axis",
        items = (
            ('X','X',""),
            ('Y','Y',""),
            ('Z','Z',""),
            ('XYZ','Cursor Axis',"")),
            default = 'Z'
        )
         
    @classmethod
    def poll(cls, context):

        return context.mode == "OBJECT" and len(context.selected_objects)>0
    
       
    def execute(self,context):
        
        duplication = []
        selected_objs = bpy.context.selected_objects[:]
        
        pre_mode = bpy.context.scene.tool_settings.transform_pivot_point
        bpy.context.scene.tool_settings.transform_pivot_point = 'CURSOR'
        angle = math.radians(self.degree/self.count) if self.degree == 360 else math.radians(self.degree/(self.count-1))
        
        for obj in selected_objs :
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj

            duplication.append(bpy.context.active_object.name_full)
            
            
            for i in range(self.count-1):
                if self.link == True:
                    bpy.ops.object.duplicate_move_linked()
                else :
                    bpy.ops.object.duplicate_move()

                duplication.append(bpy.context.active_object.name_full)

                if self.orient_axis == 'XYZ':
                    bpy.ops.transform.rotate(value=angle, orient_type='CURSOR')
                else :
                    bpy.ops.transform.rotate(value=angle, orient_axis=self.orient_axis)  

        for name in duplication:
            
            bpy.context.scene.objects[name].select_set(True)
        bpy.context.scene.tool_settings.transform_pivot_point = pre_mode

        return {'FINISHED'} 
     
class DP_spiral_array(bpy.types.Operator):

    bl_idname = "mesh.dp_spiral_array"
    bl_label = "Spiral Array"
    bl_description = "Spiral Array ( use the CURSOR's location as the center )"
    bl_options = {'REGISTER','UNDO'}

    link : bpy.props.BoolProperty(name="link", default=True) 

    count : bpy.props.IntProperty(
        name = "Count",
        description = "Number Of Copies",
        default = 6,
        min = 2
        )  
    
    orient_axis : bpy.props.EnumProperty(
        name = "Axis",
        description = "Orient Axis",
        items = (
            ('X','X',""),
            ('Y','Y',""),
            ('Z','Z',""),
            ('XYZ','Cursor Axis',"")),
            default = 'Z'
        )
        
    height : bpy.props.FloatProperty(
        name = "Height",
        description = "Height of the spiral",
        default = 1,
        max = 10000,
        min = -10000
        ) 
    revolutions : bpy.props.FloatProperty(
        name = "Revolutions",
        description = "Revolutions of the spiral",
        default = 1,
        max = 10000,
        min = 0.0,
        ) 
    
    taper : bpy.props.FloatProperty(
        name = "Taper degree",
        description = "Taper degree of the spiral",
        default = 0,
        max = 89.99,
        min = -89.99,
        ) 

    @classmethod
    def poll(cls, context):

        return context.mode == "OBJECT" and len(context.selected_objects)>0
       
    def execute(self,context):
        def cal_move(cord,dis_1,dis_2):
            if cord == 0 or dis_1 == 0:
                move_cord = dis_2
            else :    
                move_cord = dis_2/dis_1*cord

            return move_cord


        duplication = []
        selected = bpy.context.selected_objects[:]
        
        pre_mode = bpy.context.scene.tool_settings.transform_pivot_point
        bpy.context.scene.tool_settings.transform_pivot_point = 'CURSOR'
        angle = math.radians(self.revolutions*360/(self.count-1))
        dis_2 = self.height/(self.count-1)*math.tan(math.radians(self.taper))
        cursor_location=bpy.context.scene.cursor.location


        for obj in selected :
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj

            duplication.append(bpy.context.active_object.name_full)
            
            
            
            for i in range(self.count-1):
                if self.link == True:
                    bpy.ops.object.duplicate_move_linked()
                else:
                    bpy.ops.object.duplicate_move()
                    
                
                duplication.append(bpy.context.active_object.name_full)
                x = bpy.context.object.location[0]-cursor_location[0]
                y = bpy.context.object.location[1]-cursor_location[1]
                z = bpy.context.object.location[2]-cursor_location[2]
                distance=[x,y,z]
                
                cords=['X','Y','Z','XYZ']

                index = cords.index(self.orient_axis) if self.orient_axis!='XYZ' else 2

                distance.pop(index)
                dis_1 = math.hypot(abs(distance[0]),abs(distance[1]))
                moves=[cal_move(x,dis_1,dis_2),cal_move(y,dis_1,dis_2),cal_move(z,dis_1,dis_2)]
                moves[index]=self.height/self.count
                if self.orient_axis == 'XYZ':
                    bpy.ops.transform.rotate(value=angle, orient_type='CURSOR')
                    bpy.ops.transform.translate(value=(moves[0], moves[1], moves[2]), orient_type='CURSOR')
                else:
                    bpy.ops.transform.rotate(value=angle, orient_axis=self.orient_axis)
                    bpy.ops.transform.translate(value=(moves[0], moves[1], moves[2]), orient_type='GLOBAL')



        for name in duplication:
            
            bpy.context.scene.objects[name].select_set(True)
        bpy.context.scene.tool_settings.transform_pivot_point = pre_mode

        return {'FINISHED'}   
                                
class DP_linear_array(bpy.types.Operator):

    bl_idname = "mesh.dp_linear_array"
    bl_label = "Linear Array"
    bl_description = "Linear Array ( use the CURSOR's location as the endpoint )"
    bl_options = {'REGISTER','UNDO'}

    link : bpy.props.BoolProperty(name="link", default=True) 

    count : bpy.props.IntProperty(
        name = "Count",
        description = "Number Of Copies",
        default = 6,
        min = 2
        )  

    axis : bpy.props.EnumProperty(
        name = "Axis",
        description = "Axis",
        items = (
            ('X','X',""),
            ('Y','Y',""),
            ('Z','Z',""),
            ('XYZ','Cursor Axis',"")),
            default = 'X'
        )
         
    @classmethod
    def poll(cls, context):

        return context.mode == "OBJECT"  and len(context.selected_objects)>0
       
    def execute(self,context):
        pre_mode = bpy.context.scene.transform_orientation_slots[0].type
        bpy.context.scene.transform_orientation_slots[0].type = 'GLOBAL'

        duplication = []
        selected = []
        cur_x = bpy.context.scene.cursor.location[0]
        cur_y = bpy.context.scene.cursor.location[1]
        cur_z = bpy.context.scene.cursor.location[2]
        obj_x = bpy.context.active_object.location[0]
        obj_y = bpy.context.active_object.location[0]
        obj_z = bpy.context.active_object.location[0]       

        
        distance_x = (cur_x-obj_x)/(self.count-1)
        distance_y = (cur_y-obj_y)/(self.count-1)
        distance_z = (cur_z-obj_z)/(self.count-1)
        
        
        for obj in bpy.context.selected_objects:
            selected.append(obj)

        for obj in selected :
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
            duplication.append(bpy.context.active_object.name_full)

            for i in range(self.count-1):
                if self.link == True:
                    bpy.ops.object.duplicate_move_linked()
                else :
                    bpy.ops.object.duplicate_move()

                duplication.append(bpy.context.active_object.name_full)

                if self.axis ==  'X':
                    bpy.ops.transform.translate(value=(distance_x,0,0))
                elif self.axis ==  'Y':
                    bpy.ops.transform.translate(value=(0,distance_y,0))
                elif self.axis ==  'Z':
                    bpy.ops.transform.translate(value=(0,0,distance_z))
                elif self.axis ==  'XYZ':
                    bpy.ops.transform.translate(value=(distance_x,distance_y,distance_z))
                    
        for name in duplication:
            bpy.context.scene.objects[name].select_set(True)

        bpy.context.scene.transform_orientation_slots[0].type = pre_mode
        return {'FINISHED'}  
class DP_curve_array(bpy.types.Operator):

    bl_idname = "mesh.dp__curve_array"
    bl_label = "Curve Array"
    bl_description = "Select at least one object and a curve (the curve should be the active one)"
    bl_options = {'REGISTER','UNDO'}
    
    count : bpy.props.IntProperty(
        name = "Count",
        description = "Number Of Copies",
        default = 6,
        min = 1
        ) 
        
    distance : bpy.props.FloatProperty(
        name = "Distance",
        description = "the distance between array items",
        default = 2,
        min = 0,
        precision = 2
        ) 
            
    direction : bpy.props.EnumProperty(
        name = "Axis",
        items = (
            ('X','X',""),
            ('Y','Y',""),
            ('Z','Z',""),
            ('-X','-X',""),
            ('-Y','-Y',""),
            ('-Z','-Z',"")),
            default = 'Y'
        ) 
    
    @classmethod
    def poll(cls, context):
        cur_count = 0 
        for ob in bpy.context.selected_objects:
            if ob.type == 'CURVE':
                cur_count+=1 

        return context.mode == "OBJECT" and len(context.selected_objects)>0 and cur_count == 1
    
    
    def execute(self,context):
        
        bpy.ops.view3d.snap_selected_to_active()
        sel = []
        for ob in bpy.context.selected_objects:
            if ob.type == 'MESH' :
                sel.append(ob)
        
        curve = bpy.context.active_object
        
        for ob in sel :
            
            a = ob.modifiers.new(name = 'Array',type='ARRAY')
            b = ob.modifiers.new(name = 'Curve',type='CURVE')
            ob.modifiers[a.name].count = self.count
            ob.modifiers[b.name].object = curve

            if self.direction == 'X':
                ob.modifiers[b.name].deform_axis = 'POS_X'
                ob.modifiers[a.name].relative_offset_displace[0] = self.distance
                ob.modifiers[a.name].relative_offset_displace[1] = 0    
                ob.modifiers[a.name].relative_offset_displace[2] = 0
            elif self.direction == '-X':
                ob.modifiers[b.name].deform_axis = 'NEG_X'
                ob.modifiers[a.name].relative_offset_displace[0] = -self.distance
                ob.modifiers[a.name].relative_offset_displace[1] = 0    
                ob.modifiers[a.name].relative_offset_displace[2] = 0
            elif self.direction == 'Y':
                ob.modifiers[b.name].deform_axis = 'POS_Y'
                ob.modifiers[a.name].relative_offset_displace[0] = 0
                ob.modifiers[a.name].relative_offset_displace[1] = self.distance   
                ob.modifiers[a.name].relative_offset_displace[2] = 0    
            elif self.direction == '-Y':
                ob.modifiers[b.name].deform_axis = 'NEG_Y'
                ob.modifiers[a.name].relative_offset_displace[0] = 0
                ob.modifiers[a.name].relative_offset_displace[1] = -self.distance 
                ob.modifiers[a.name].relative_offset_displace[2] = 0
            elif self.direction == 'Z':
                ob.modifiers[b.name].deform_axis = 'POS_Z'
                ob.modifiers[a.name].relative_offset_displace[0] = 0
                ob.modifiers[a.name].relative_offset_displace[1] = 0    
                ob.modifiers[a.name].relative_offset_displace[2] = self.distance            
            elif self.direction == '-Z':
                ob.modifiers[b.name].deform_axis = 'NEG_Z'
                ob.modifiers[a.name].relative_offset_displace[0] = 0
                ob.modifiers[a.name].relative_offset_displace[1] = 0    
                ob.modifiers[a.name].relative_offset_displace[2] = -self.distance
          
            
        
        
        return {'FINISHED'}  

class DP_unlink_objects(bpy.types.Operator):

    bl_idname = "mesh.dp_unlink_objects"
    bl_label = "Unlink Selected Objects"
    bl_description = "Unlink selected objects"


         
    @classmethod
    def poll(cls, context):

        return context.mode == "OBJECT"  and len(context.selected_objects)>0
       
    def execute(self,context):
        
        bpy.ops.object.make_single_user(object=False, obdata=True, material=False, animation=False)
 
        return {'FINISHED'}  
    
class DP_sync_modifier(bpy.types.Operator):

    bl_idname = "mesh.dp_sync_modifier"
    bl_label = "Sync Modifier"
    bl_description = "Sync modifier to the linked objects"

 
    @classmethod
    def poll(cls, context):

        return context.mode == "OBJECT"  and len(context.selected_objects)>0
       
    def execute(self,context):
        
        for ob in bpy.context.selected_objects:
            bpy.context.view_layer.objects.active = ob
            bpy.ops.object.select_linked(type='OBDATA')
            bpy.ops.object.make_links_data(type='MODIFIERS')

        return {'FINISHED'}  
          
class DP_apply_modifier(bpy.types.Operator):

    bl_idname = "mesh.dp_apply_modifier"
    bl_label = "Apply Modifier"
    bl_description = "Apply all modifier to the linked objects"

 
    @classmethod
    def poll(cls, context):

        return context.mode == "OBJECT"  and len(context.selected_objects)>0
       
    def execute(self,context):
        
       

        for ob in bpy.context.selected_objects:
            sel = []
            bpy.context.view_layer.objects.active = ob
            bpy.ops.object.select_linked(type='OBDATA')
            for ob in bpy.context.selected_objects:
                sel.append(ob)
            bpy.ops.object.make_links_data(type='MODIFIERS')
            bpy.ops.object.make_single_user(object=False, obdata=True, material=False, animation=False)
            for ob in sel:
                bpy.context.view_layer.objects.active = ob 
                for m in ob.modifiers:
                    
                    bpy.ops.object.modifier_apply(modifier=m.name)
                    

            bpy.ops.object.make_links_data(type='OBDATA')

        return {'FINISHED'}  
                         
class VIEW3D_MT_object_context_menu_Duplicate_Master(bpy.types.Menu):
    
    bl_label = "Duplicate Master"

    def draw(self,context):
        
        layout = self.layout
        layout.operator('mesh.dp__mirror',text = "Mirror",icon = 'MOD_MIRROR')
        layout.operator('mesh.dp_circular_array',text = "Circular Array",icon = 'ONIONSKIN_ON')
        layout.operator('mesh.dp_linear_array',text = "Linear Array",icon = 'MOD_ARRAY')
        layout.operator('mesh.dp_spiral_array',text = "Spiral Array",icon = 'MOD_SCREW')
        layout.operator('mesh.dp__curve_array',text = "Curve Array",icon = 'MOD_THICKNESS')
        layout.operator('mesh.dp_sync_modifier',text = "Sync modifier",icon = 'FILE_REFRESH') 
        layout.operator('mesh.dp_apply_modifier',text = "Apply modifier",icon = 'MODIFIER')
        layout.operator('mesh.dp_join',text = "Join",icon = 'SELECT_EXTEND')

class VIEW3D_MT_Duplicate_Master_Pie(bpy.types.Menu):
    bl_idname = "duplicate_master_pie"
    bl_label = "Duplicate Master"
    bl_space_type = 'UI'

    def draw(self, context):
        layout = self.layout
        object = bpy.ops.object
        pie = layout.menu_pie()
        pie.operator('mesh.dp_circular_array',text = "Circular Array",icon = 'ONIONSKIN_ON')
        pie = layout.menu_pie()
        pie.operator('mesh.dp_linear_array',text = "Linear Array",icon = 'MOD_ARRAY')
        pie = layout.menu_pie()
        col = pie.column()
        col.scale_y = 1.5
        col.scale_x = 1.1
        col.operator('object.select_linked',text = "Select Linked",icon = 'LINKED').type='OBDATA'
        col.operator('mesh.dp_unlink_objects',text = "Unlink selected",icon = 'UNLINKED')
        pie = layout.menu_pie()
        col = pie.column()
        col.scale_y = 1.5
        col.scale_x = 1.1
        col.operator('mesh.dp_sync_modifier',text = "Sync modifier",icon = 'FILE_REFRESH') 
        col.operator('mesh.dp_apply_modifier',text = "Apply modifier",icon = 'MODIFIER')
        pie = layout.menu_pie()
        pie.operator('mesh.dp__mirror',text = "Mirror",icon = 'MOD_MIRROR')
        pie = layout.menu_pie()
        pie.operator('mesh.dp_join',text = "Join",icon = 'SELECT_EXTEND')
        pie = layout.menu_pie()
        pie.operator('mesh.dp_spiral_array',text = "Spiral Array",icon = 'MOD_SCREW')
        pie = layout.menu_pie()
        pie.operator('mesh.dp__curve_array',text = "Curve Array",icon = 'MOD_THICKNESS')
        

        
classes = [
    DP_mirror,
    VIEW3D_MT_object_context_menu_Duplicate_Master,
    DP_circular_array,
    DP_linear_array,
    DP_unlink_objects,
    VIEW3D_MT_Duplicate_Master_Pie,
    DP_sync_modifier,
    DP_apply_modifier,
    DP_spiral_array,
    DP_curve_array,
    DP_join
 
]

keymap_items = [
    
    ['3D View', 'VIEW_3D', 'wm.call_menu_pie', 'D', 'PRESS', False, False, False, 'duplicate_master_pie'],
    ['3D View Generic', 'VIEW_3D', 'wm.call_menu_pie', 'D', 'PRESS', False, False, False, 'duplicate_master_pie'],


] 

addon_keymaps = []

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
        addon_keymaps.append((km, kmi))
        if pie_name:
            kmi.properties.name = pie_name
 
def menu_func(self,context):
    self.layout.menu("VIEW3D_MT_object_context_menu_Duplicate_Master")
    self.layout.separator()
    
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.VIEW3D_MT_object_context_menu.prepend(menu_func)
    wm = bpy.context.window_manager 

    keymap_register(wm)
     

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    bpy.types.VIEW3D_MT_object_context_menu.remove(menu_func)
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        for km, kmi in addon_keymaps:
            km.keymap_items.remove(kmi)
    addon_keymaps.clear()


if __name__ == "__main__":
    register()
