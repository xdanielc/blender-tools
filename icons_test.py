import os

import bpy
import bpy.utils.previews
from bpy.types import Panel

# for entry in os.scandir(dir):
#     if entry.name.endswith(".png"):
#         name = os.path.splitext(entry.name)[0]
#         icons_dict.load(name.upper(), entry.path, "IMAGE")

class VIEW3D_PT_test(Panel):
    bl_label = "TEST"
    bl_category = "TEST"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.prop(scene, "use_gravity", text="Enable Layout")

        col = layout.column()
        col.enabled = scene.use_gravity
        col.operator("object.duplicate_move", text="Custom Icon", icon_value=pcoll["custom_icon"].icon_id)
        col.operator("object.duplicate_move", text="Built-in Icon", icon="OUTPUT")


pcoll = None # pcoll

def register():
    global pcoll
    pcoll = bpy.utils.previews.new()
    addon_path = os.path.dirname(__file__)
    # Para addons: directorio_script/icons
    icons_dir = os.path.join(addon_path, "icons")
    pcoll.load("custom_icon", os.path.join(icons_dir, "icon.png"), 'IMAGE')
    bpy.utils.register_class(VIEW3D_PT_test)

def unregister():
    bpy.utils.unregister_class(VIEW3D_PT_test)
    global pcoll
    bpy.utils.previews.remove(pcoll)

if __name__ == "__main__":
    register()
