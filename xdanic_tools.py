# ----- BEGIN GPL LICENSE BLOCK -----
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ----- END GPL LICENSE BLOCK -----

import bpy
from bpy import ops
from bpy.types import (
        Menu,
        Operator,
        )

bl_info = {
    "name": "Xdanic's utilities",
    "description": "A set ot tools for easier modeling on blender",
    "author": "Daniel Calderón, CDMJ, Vaughan Ling",
    "version": (1, 0, 0),
    "blender": (2, 80, 0),
    "support": "COMMUNITY",
    "category": "Object"
}


class OBJECT_OT_AddCreases(Operator):
    """Quick creases"""
    bl_label = "Creases quick"
    bl_idname = "mesh.creases_add"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.area.type == 'VIEW_3D' and context.tool_settings.mesh_select_mode[1] or context.mode == 'OBJECT'

    def execute(self, context):
        angle = context.active_object.data.auto_smooth_angle
        mode = context.mode
        ops.object.mode_set(mode='EDIT')
        ops.mesh.select_all(action='DESELECT')
        ops.mesh.edges_select_sharp(sharpness=angle)
        ops.object.editmode_toggle()
        for e in context.active_object.data.edges:
            if e.use_edge_sharp:
                e.select = True
        ops.object.editmode_toggle()
        ops.transform.edge_crease(value=1)
        if mode == 'OBJECT':
            ops.object.editmode_toggle()
        self.report({'INFO'}, "Done!")
        return {'FINISHED'}


class OBJECT_OT_RemoveCreases(Operator):
    """Quick creases remove"""
    bl_label = "Creases quick remove"
    bl_idname = "mesh.creases_remove"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.area.type == 'VIEW_3D' and context.tool_settings.mesh_select_mode[1] or context.mode == 'OBJECT'

    def execute(self, context):
        mode = context.mode
        ops.object.mode_set(mode='EDIT')
        ops.mesh.select_all(action='SELECT')
        ops.transform.edge_crease(value=-1.0)
        if mode == 'OBJECT':
            ops.object.editmode_toggle()
        self.report({'INFO'}, "Done!")
        return {'FINISHED'}

class OBJECT_OT_PivotSet(Operator):
    """Set Pivot"""
    bl_idname = "mesh.pivot_set"
    bl_label = "Pivot"
    bl_options = {'REGISTER', 'UNDO'}
    # https://blender.stackexchange.com/questions/1291/change-pivot-or-local-origin-of-an-object
    @classmethod
    def poll(cls, context):
        return (context.mode == 'EDIT_MESH')

    def execute(self, context):
        saved_location = bpy.context.scene.cursor.location.copy()
        bpy.ops.view3d.snap_cursor_to_selected()

        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        bpy.context.scene.cursor.location = saved_location

        bpy.ops.object.mode_set(mode='EDIT')
        return {'FINISHED'}


def menu_func(self, context):
    is_edge_mode = context.tool_settings.mesh_select_mode[1]
    layout = self.layout
    layout.operator_context = "INVOKE_DEFAULT"
    if is_edge_mode:
        self.layout.operator(OBJECT_OT_AddCreases.bl_idname, text="Quick creases")
        self.layout.operator(OBJECT_OT_RemoveCreases.bl_idname, text="Quick creases remove")


class HPXD_MT_pie_pivots(Menu):
    bl_label = "Pivots Pie"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        # 4 - LEFT
        prop = pie.operator("wm.context_toggle_enum", text="Direction", icon='OBJECT_DATA')
        prop.data_path = "scene.transform_orientation_slots[0].type"
        prop.value_1 = "NORMAL"
        prop.value_2 = "GLOBAL"


        # 6 - RIGHT
        pie.split()
        # 2 - BOTTOM

        prop = pie.operator("wm.context_set_enum", text="Pivot Individuals", icon='PIVOT_INDIVIDUAL')
        prop.data_path = "scene.tool_settings.transform_pivot_point"
        prop.value = 'INDIVIDUAL_ORIGINS'
		
        prop = pie.operator("wm.context_set_enum", text="Pivot Median", icon='PIVOT_MEDIAN')
        prop.data_path = "scene.tool_settings.transform_pivot_point"
        prop.value = 'MEDIAN_POINT'

        prop = pie.operator("wm.context_set_enum", text="Pivot Last Selected", icon='PIVOT_ACTIVE')
        prop.data_path = "scene.tool_settings.transform_pivot_point"
        prop.value = 'ACTIVE_ELEMENT'

        prop = pie.operator("wm.context_set_enum", text="Pivot Cursor", icon='PIVOT_CURSOR')
        prop.data_path = "scene.tool_settings.transform_pivot_point"
        prop.value = 'CURSOR'
        # 8 - TOP
        prop = pie.operator("transform.create_orientation", text="Pivot Custom", icon='FACESEL')
        prop.use = True
        prop.name = "Pivot Custom"
        prop.overwrite = True
        # 7 - TOP - LEFT

        # 9 - TOP - RIGHT
        pie.operator("transform.shear", text="Shear")
        # 1 - BOTTOM - LEFT


        # 3 - BOTTOM - RIGHT

classes = (
    OBJECT_OT_AddCreases,
    OBJECT_OT_RemoveCreases,
    OBJECT_OT_PivotSet,
    HPXD_MT_pie_pivots
)

addon_keymaps = []

def kmi_props_setattr(kmi_props, attr, value):
    try:
        setattr(kmi_props, attr, value)
    except AttributeError:
        print("Warning: property '%s' not found in keymap item '%s'" %
              (attr, kmi_props.__class__.__name__))
    except Exception as e:
        print("Warning: %r" % e)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.VIEW3D_MT_edit_mesh_context_menu.append(menu_func)
    bpy.types.VIEW3D_MT_edit_mesh_edges.append(menu_func)
    bpy.types.VIEW3D_MT_object_context_menu.append(menu_func)

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        # Name "mesh" is inside 3D view, but space_type should be set as empty to work
        km = kc.keymaps.new(name='Mesh', space_type='EMPTY')
        kmi = km.keymap_items.new("mesh.pivot_set", 'BACK_SLASH', 'PRESS')
        kmi = km.keymap_items.new("mesh.inset", 'GRLESS', 'PRESS', shift=True)
        km = kc.keymaps.new('3D View', space_type='VIEW_3D', region_type='WINDOW', modal=False)
        kmi = km.keymap_items.new("wm.call_menu_pie", 'GRLESS', 'PRESS').properties.name="HPXD_MT_pie_pivots"
        # kmi = km.keymap_items.new("view3d.ke_tt", 'G', 'PRESS')
        # kmi_props_setattr(kmi.properties, 'mode', 'MOVE')
        # kmi = km.keymap_items.new("view3d.ke_tt", 'R', 'PRESS')
        # kmi_props_setattr(kmi.properties, 'mode', 'ROTATE')
        # kmi = km.keymap_items.new("view3d.ke_tt", 'S', 'PRESS')
        # kmi_props_setattr(kmi.properties, 'mode', 'SCALE')


def unregister():
    for km,kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
        addon_keymaps.clear()

    for cls in reversed(classes):
        bpy.utils.register_class(cls)
    bpy.types.VIEW3D_MT_edit_mesh_context_menu.remove(menu_func)
    bpy.types.VIEW3D_MT_edit_mesh_edges.remove(menu_func)
    bpy.types.VIEW3D_MT_object_context_menu.remove(menu_func)


if __name__ == "__main__":
    register()
