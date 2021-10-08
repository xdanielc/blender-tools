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

from bpy.ops import text
from bpy.props import StringProperty
from bpy.types import AddonPreferences
import bpy
bl_info = {
    "name": "UV panel",
    "author": "Daniel Calderón",
    "description": "UV Panel",
    "blender": (2, 80, 0),
    "version": (0, 1, 4),
    "location": "UV area > Toolbox",
    "warning": "",
    "doc_url": "https://github.com/xdanielc",
    "category": "UV"
}

class MyProperties(bpy.types.PropertyGroup):
    rotate_bool : bpy.props.BoolProperty(name="Rotate Option")


class UV_PT_uv_helper(bpy.types.Panel):
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "3DS Max"
    bl_idname = "UV_PT_uv_helper"
    bl_label = "Select Panel"
    

    @classmethod
    def poll(cls, context):
        return (context.object is not None)

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        rotar = scene.uv_helper
        
        layout.label(text="Quick Transforms")
        col = layout.column(align=True)
        row = col.row(align=True)
        row.scale_y = 2
        row.operator("uv.align", text="Al X").axis = 'ALIGN_X'
        row.operator("uv.align").axis = 'ALIGN_S'
        row.operator("uv.turn", icon='LOOP_FORWARDS').ccw = False
        row = col.row(align=True)
        row.scale_y = 2
        row.operator("uv.align", text="Al Y").axis = 'ALIGN_Y'
        row.operator("uv.textools_island_align_edge", text="Edge", icon='FILE_REFRESH')
        row.operator("uv.turn", icon='LOOP_BACK').ccw = True
        
        layout.label(text="Brush")
        col = layout.column(align=True)
        row = col.row(align=True)
        row.scale_y = 2
        row.operator("wm.tool_set_by_id", text="Grab").name="builtin_brush.Grab"
        row.operator("wm.tool_set_by_id", text="Relax").name="builtin_brush.Relax"
        row.operator("wm.tool_set_by_id", text="Pinch").name="builtin_brush.Pinch"
        
        layout.label(text="Reshape Elements")
        col = layout.column(align=True)
        row = col.row(align=True)
        row.scale_y = 2
        row.operator("uv.uv_squares_by_shape", text="Straighten")
        row.operator("uv.minimize_stretch", text="Relax").iterations=111
        row.label(text="Custom")
        
        layout.label(text="Stitch")
        col = layout.column(align=True)
        row = col.row(align=True)
        row.scale_y = 2
        prop = row.operator("uv.stitch", text="Target")
        prop.snap_islands=True
        prop.midpoint_snap=False
        prop.static_island=1
        prop = row.operator("uv.stitch", text="Average")
        prop.snap_islands=False
        prop.midpoint_snap=True
        prop = row.operator("uv.stitch", text="Source")
        prop.snap_islands=True
        prop.midpoint_snap=False
        prop.static_island=0
        row.label(text="Custom")
        
        layout.label(text="Explode")
        
        layout.label(text="Peel")
        
        layout.label(text="Arrange Elements")
        col = layout.column(align=True)
        row = col.row(align=True)
        row.scale_y = 2
        prop = row.operator("uv.pack_islands")
        if rotar.rotate_bool == True:
            prop.rotate=True
        else:
            prop.rotate=False
        row.prop(rotar, "rotate_bool")
        
        layout.label(text="Element Properties")

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
        if not hasattr(bpy.ops.mesh, "adj_verices"):
            row.label(text="Adjacent selection", icon='ERROR')
        else:
            row.label(text="Adjacent selection", icon='CHECKMARK')
        row.operator("wm.url_open", text="URL", icon='URL').url = "https://github.com/Borschberry/Adjacent-Selection"

        row = layout.row()
        if not hasattr(bpy.ops.mesh, "ext_deselect_boundary"):
            row.label(text="Edit Mesh Tools", icon='ERROR')
        else:
            row.label(text="Edit Mesh Tools", icon='CHECKMARK')
        row.label(text="Addon installed with blender", icon='INFO')

        row = layout.row()
        if not hasattr(bpy.ops.mesh, "pivot_set"):
            row.label(text="xdanic utilities", icon='ERROR')
        else:
            row.label(text="xdanic utilities", icon='CHECKMARK')
        row.operator("wm.url_open", text="URL", icon='URL').url = "https://github.com/xdanielc"

        col = layout.column()
        col.label(text="Shortchuts added:")
        col.label(text="Select islands with double click and shift double click")
        col.label(text="Select more or less with shift ctrl + mouse wheel")
        col.label(text="Select next or prev with shift + mouse wheel")


classes = (
    MyProperties,
    UV_PT_uv_helper,
    UVPanelPreferences
)

# Register all operators and panels
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Scene.uv_helper = bpy.props.PointerProperty(type=MyProperties)

    update_panel(None, bpy.context)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    del bpy.types.Scene.uv_helper


if __name__ == "__main__":
    register()
