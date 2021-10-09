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
from bpy.props import StringProperty
from bpy.types import (
        AddonPreferences,
        Operator,
        )

bl_info = {
    "name": "UV Helper",
    "author": "Daniel Calderón",
    "description": "UV Panel",
    "blender": (2, 80, 0),
    "version": (0, 0, 1),
    "location": "UV area > Toolbox",
    "warning": "",
    "doc_url": "https://github.com/xdanielc",
    "category": "UV"
}


class UV_OT_SmoothSplit(Operator):
    """Split by hard edges"""
    bl_label = "Split by smoothing"
    bl_idname = "uv.split_by_smoothing"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.area.type == 'VIEW_3D' and context.tool_settings.mesh_select_mode[1] or context.area.type == 'IMAGE_EDITOR' and context.mode == 'EDIT_MESH'

    def execute(self, context):
        angle = context.active_object.data.auto_smooth_angle
        mode = context.mode
        ops.object.mode_set(mode='EDIT')
        # Si hay marcas borrar
        ops.mesh.select_all(action='SELECT')
        for e in context.active_object.data.edges:
            e.select = True
        ops.mesh.mark_seam(clear=True)
        # Si hay marcas borrar
        ops.mesh.select_all(action='DESELECT')
        ops.mesh.edges_select_sharp(sharpness=angle)
        ops.object.editmode_toggle()
        for e in context.active_object.data.edges:
            if e.use_edge_sharp:
                e.select = True
        ops.object.editmode_toggle()
        ops.mesh.mark_seam(clear=False)
        ops.mesh.select_all(action='SELECT')
        self.report({'INFO'}, "Done!")
        return {'FINISHED'}


class UV_OT_IDSplit(Operator):
    """Split by material"""
    bl_label = "Split by material"
    bl_idname = "uv.split_by_id"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.area.type == 'VIEW_3D' and context.tool_settings.mesh_select_mode[1] or context.area.type == 'IMAGE_EDITOR' and context.mode == 'EDIT_MESH'

    def execute(self, context):
        mode = context.mode
        ops.object.mode_set(mode='EDIT')
        # Si hay marcas borrar
        ops.mesh.select_all(action='SELECT')
        for e in context.active_object.data.edges:
            e.select = True
        ops.mesh.mark_seam(clear=True)
        # Si hay marcas borrar
#        ops.object.mode_set(mode='OBJECT')
        ops.mesh.select_all(action='DESELECT')
#        ops.object.editmode_toggle()
        # Selecciona algo
        for imat in range(len(context.active_object.material_slots)):
            bpy.context.object.active_material_index = imat
            ops.object.material_slot_select()
            ops.mesh.region_to_loop()
            ops.mesh.mark_seam(clear=False)
            ops.mesh.select_all(action='DESELECT')
        ops.mesh.select_all(action='SELECT')
        self.report({'INFO'}, "Done!")
        return {'FINISHED'}


class UV_PT_uv_helper(bpy.types.Panel):
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "UV Helper"
    bl_idname = "UV_PT_uv_helper"
    bl_label = "UV Helper"

    @classmethod
    def poll(cls, context):
        return (context.object is not None)

    def draw(self, context):
        layout = self.layout
        
        layout.label(text="Quick Transforms")
        col = layout.column(align=True)
        row = col.row(align=True)
        row.scale_y = 1.5
        row.operator("uv.align", text="Al X").axis = 'ALIGN_X'
        row.operator("uv.align").axis = 'ALIGN_S'
        row.operator("uv.turn", icon='LOOP_FORWARDS').ccw = False
        row = col.row(align=True)
        row.scale_y = 1.5
        row.operator("uv.align", text="Al Y").axis = 'ALIGN_Y'
        if hasattr(bpy.types, "UV_OT_textools_island_align_edge"):
            row.operator("uv.textools_island_align_edge", text="Edge", icon='FILE_REFRESH')
        else:
            row.label(text="Textools missing", icon='ERROR')
        row.operator("uv.turn", icon='LOOP_BACK').ccw = True
        
        
        layout.label(text="Brush")
        col = layout.column(align=True)
        row = col.row(align=True)
        row.scale_y = 1.5
        row.operator("wm.tool_set_by_id", text="Select").name="builtin.select_box"
        row.operator("wm.tool_set_by_id", text="Grab").name="builtin_brush.Grab"
        row = col.row(align=True)
        row.scale_y = 1.5
        row.operator("wm.tool_set_by_id", text="Relax").name="builtin_brush.Relax"
        row.operator("wm.tool_set_by_id", text="Pinch").name="builtin_brush.Pinch"
        
        layout.label(text="Reshape Elements")
        col = layout.column(align=True)
        row = col.row(align=True)
        row.scale_y = 1.5
        if hasattr(bpy.types, "UV_OT_uv_squares_by_shape"):
            row.operator("uv.uv_squares_by_shape", text="Straighten")
        else:
            row.label(text="UV Squares missing", icon='ERROR')
        row.operator("uv.minimize_stretch", text="Relax").iterations=111
        
        layout.label(text="Stitch")
        col = layout.column(align=True)
        row = col.row(align=True)
        row.scale_y = 1.5
        prop = row.operator("uv.stitch", text="Target")
        prop.snap_islands=True
        prop.midpoint_snap=False
        prop = row.operator("uv.stitch", text="Average")
        prop.snap_islands=False
        prop.midpoint_snap=True
        
        layout.label(text="Explode")
        col = layout.column(align=True)
        row = col.row(align=True)
        row.scale_y = 1.5
        row.operator("uv.select_split", text="Split")
        row = col.row(align=True)
        row.scale_y = 1.5
        row.operator("uv.smart_project", text="Pol. Angle")
        row.operator("uv.split_by_smoothing", text="Smoothing")
        row.operator("uv.split_by_id", text="Mat. ID")
        
        row = col.row(align=True)
        row.scale_y = 1.5
        row.operator("uv.remove_doubles", text="Dist. merge")
        row.operator("uv.lightmap_pack", text="Lightmap")

        
        layout.label(text="Peel")
        col = layout.column(align=True)
        row = col.row(align=True)
        row.scale_y = 1.2
        row.prop(context.space_data.uv_editor, "use_live_unwrap")
        row = col.row(align=True)
        row.scale_y = 1.5
        row.operator("uv.unwrap")
        row = col.row(align=True)
        row.scale_y = 1.5
        row.operator("uv.pin").clear=False
        row.operator("uv.pin", text="Unpin").clear=True
        row.operator("uv.select_pinned", text="Select")
        row = col.row(align=True)
        row.scale_y = 1.5
        row.operator("uv.mark_seam", text="Mark").clear=False
        row.operator("uv.mark_seam", text="Clear").clear=True
        row.operator("uv.seams_from_islands", text="By Islands")
        
        layout.label(text="Arrange Elements")
        col = layout.column(align=True)
        row = col.row(align=True)
        row.scale_y = 1.5
        row.operator("uv.average_islands_scale", text="Average")
        row.operator("uv.pack_islands", text="Pack")
        
        layout.label(text="Proyection")
        col = layout.column(align=True)
        row = col.row(align=True)
        row.scale_y = 1.5
        row.operator("uv.cube_project", text="Cube", icon='CUBE')
        row.operator("uv.cylinder_project", text="Cylinder", icon='MESH_CYLINDER')
        row.operator("uv.sphere_project", text="Sphere", icon='SPHERE')
        row = col.row(align=True)
        row.scale_y = 1.5
        row.operator("uv.follow_active_quads", text="Active Quads")


# Add-ons Preferences Update Panel

# Define Panel classes for updating
panels = (
    UV_PT_uv_helper
)


def update_panel(self, context):
    message = "Select Panel: Updating Panel locations has failed"
    try:
        for panel in panels:
            if "bl_rna" in panel.__dict__:
                bpy.utils.unregister_class(panel)

        for panel in panels:
            panel.bl_category = context.preferences.addons[__name__].preferences.category
            bpy.utils.register_class(panel)

    except Exception as e:
        print("\n[{}]\n{}\n\nError:\n{}".format(__name__, message, e))
        pass


class UVPanelPreferences(AddonPreferences):
    # this must match the addon name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = __name__

    category: StringProperty(
        name="Tab Category",
        description="Choose a name for the category of the panel",
        default="Select",
        update=update_panel
    )

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        col = row.column()
        col.label(text="Tab Category:")
        col.prop(self, "category", text="")

        row = layout.row()
        row.label(text="Recommended addons")

        row = layout.row()
        if not hasattr(bpy.types, "UV_OT_textools_island_align_edge"):
            row.label(text="TexTools", icon='ERROR')
        else:
            row.label(text="TexTools", icon='CHECKMARK')
        row.operator("wm.url_open", text="URL", icon='URL').url = "https://github.com/SavMartin/TexTools-Blender"

        row = layout.row()
        if not hasattr(bpy.types, "UV_OT_uv_squares_by_shape"):
            row.label(text="UV Squares", icon='ERROR')
        else:
            row.label(text="UV Squares", icon='CHECKMARK')
        row.operator("wm.url_open", text="URL", icon='URL').url = "https://github.com/Radivarig/UvSquares"


classes = (
    UV_OT_SmoothSplit,
    UV_OT_IDSplit,
    UV_PT_uv_helper,
    UVPanelPreferences
)

# Register all operators and panels
def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    update_panel(None, bpy.context)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
