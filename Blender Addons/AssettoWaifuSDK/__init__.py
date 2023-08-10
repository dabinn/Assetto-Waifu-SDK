bl_info = {
    "name":     "Assetto Waifu SDK",
    "version":  (0, 1, 0),
    "blender":  (3, 4, 0),
    "author":      "Dabinn Huang",
    "description": "Tools for creating Assetto Waifu characters",
    # location的作用是將此插件放在哪個選單下，例如：File、Object、Material等等
    # 這個選單會顯示在3D View > Tool Shelf > Create中
    # 如果要將此插件放在自己的選單下，可以在blender\scripts\startup\bl_ui\space_view3d.py中加入自己的選單
    "location":    "File Export menu, Object properties, Material properties",
    # category的作用是將此插件歸類到哪個分類下，例如：Mesh、Object、Animation、Import-Export等等
    # 這個分類會顯示在User Preferences > Add-ons > Categories中
    # 如果要將此插件歸類到自己的分類下，可以在blender\scripts\startup\bl_ui\space_userpref.py中加入自己的分類
    "category": "Object",
    # support的作用是支援哪些版本的blender，例如：(2, 7, 0)、(2, 8, 0)、(2, 9, 0)、(3, 0, 0)等等
    # 這個支援會顯示在User Preferences > Add-ons > Categories > Support中
    # 如果要支援自己的版本，可以在blender\scripts\startup\bl_ui\space_userpref.py中加入自己的版本
    # support為COMMUNITY時，表示此插件為社群開發，不屬於blender官方支援
    "support":     "COMMUNITY",
    "doc_url":     "https://github.com/dabinn/Assetto-Waifu-SDK",
}

# todos:
# Export FBX with dedicated parameters for Aseetto Waifu.
# Export FBX.ini for KsEditor
# Add an option to disable FBX.ini overwrite

import importlib

# deal with blender submodules reload
# https://blender.stackexchange.com/questions/28504/blender-ignores-changes-to-python-scripts
if "bpy" in locals():
    if "vrm_gltf_exporter" in locals():
        importlib.reload(vrm_gltf_exporter)
    print("AWSDK: Reloaded Modules.")

import bpy

### import submodules
from .exporter import vrm_gltf_exporter





class bt_exportVRM(bpy.types.Operator):
    bl_idname = "object.bt_export_vrm"
    bl_label = "Export VRM"
    bl_description = "Export VRM"

    def execute(self, context):

        # # Not working
        # export_settings = bpy.context.scene.vrm_export_settings
        # # debug export_settings
        # print(f"export_settings: {export_settings}")
        # # export_settings.file_format = 'GLB'


        # 執行匯出操作
        bpy.ops.export_scene.aw(
            'INVOKE_DEFAULT',
            armature_object_name="",
            ignore_warning=False,
        )
        # bpy.ops.export_scene.aw('INVOKE_DEFAULT')
        # bpy.ops.export_scene.aw('INVOKE_DEFAULT', export_only_selections=True)

        return {'FINISHED'}



class bt_printBoneName(bpy.types.Operator):
    # bl_idname中，若使用object.開頭，則會顯示在物件的右鍵選單中
    # 寫成object.bt_printBoneName時，執行時會出現錯誤
    bl_idname = "object.bt_print_bone_name"
    bl_label = "Test Button 4"

    def execute(self, context):
        armature = context.active_object
        if armature.type == 'ARMATURE':
            pose_bones = armature.pose.bones
            for pbone in pose_bones:
                print(pbone.name)
        else:
            print("No armature object selected")

        return {'FINISHED'}


class bt_vrmTestButton(bpy.types.Operator):
    bl_idname = "object.bt_vrm_test_button"
    bl_label = "List sub classes"

    def execute(self, context):




        return {'FINISHED'}

# an example to list all attribute of bpy.context.window_manager
class bt_vrmTestButton3(bpy.types.Operator):
    bl_idname = "object.bt_vrm_test_button3"
    bl_label = "Test Button 3"

    def execute(self, context):
        for attr in dir(bpy.context.window_manager):
            print(attr)

        return {'FINISHED'}
# an example to read data from 'VRM_Addon_for_Blender'
class bt_vrmTestButton2(bpy.types.Operator):
    bl_idname = "object.bt_vrm_test_button2"
    bl_label = "VRM test"

    def execute(self, context):
        # get the vrm addon
        vrmAddon = bpy.context.window_manager.vrm
        print(vrmAddon)
        # get the vrm model
        vrmModel = vrmAddon.model
        print(vrmModel)
        # get the vrm human bones
        vrmHumanBones = vrmModel.humanoid_bones
        print(vrmHumanBones)
        # get the vrm human bones' left hand
        vrmHumanBonesLeftHand = vrmHumanBones.left_hand
        print(vrmHumanBonesLeftHand)

        return {'FINISHED'}

class pn_AssettoWaifuSDK(bpy.types.Panel):
    # Panel的ID，必須是唯一的
    # blender的console會顯示register_class時，bl_idname缺少_PT_的Warning
    # 加上_PT_後，會再顯示必需是upper case alpha-numeric prefix的Warning
    bl_idname = "PN_PT_AssettoWaifuSDK"

    # Panel顯示的名稱
    bl_label = "Develop Tools"
    # N面板顯示的名稱，同名稱的Panel會被放在同一個N面板下
    # 也代表同一個addon可以產生多個N面板
    bl_category = "Assetto Waifu SDK"
    # (?)顯示在哪個空間，可用參數有：'EMPTY'、'VIEW_3D'、'GRAPH_EDITOR'、'DOPESHEET_EDITOR'、'NLA_EDITOR'、'IMAGE_EDITOR'、'SEQUENCE_EDITOR'、'CLIP_EDITOR'、'TEXT_EDITOR'、'NODE_EDITOR'、'LOGIC_EDITOR'、'PROPERTIES'、'OUTLINER'、'USER_PREFERENCES'、'INFO'、'FILE_BROWSER'、'CONSOLE'、'TOPBAR'、'STATUSBAR'、'HEADER'、'NAVIGATION_BAR'、'TEMPORARY'、'TOOL_PROPS'、'TOOL_HEADER'、'PREVIEW'、'HUD'、'UI'、'TOOLS'、'VIEWPORT'、'TOOL_PROPS_REGION'、'TOOL_HEADER_REGION'、'MODAL'、'POPUP'、'NONE'
    bl_space_type = 'VIEW_3D'
    # (?)顯示在哪個區域，可用參數有：'WINDOW'、'HEADER'、'CHANNELS'、'TEMPORARY'、'UI'、'TOOLS'、'TOOL_PROPS'、'PREVIEW'、'HUD'、'NAVIGATION_BAR'、'EXECUTE'、'FOOTER'、'TOOL_HEADER'、'TOOL_HEADER'、'MODAL'、'POPUP'、'NONE'
    bl_region_type = 'UI'
    # (?)顯示在哪個模式，可用參數有：'OBJECT'、'EDIT'、'SCULPT'、'VERTEX_PAINT'、'WEIGHT_PAINT'、'TEXTURE_PAINT'、'PARTICLE_EDIT'、'POSE'、'EDIT_GPENCIL'、'SCULPT_GPENCIL'、'WEIGHT_GPENCIL'、'PAINT_GPENCIL'、'VERTEX_GPENCIL'、'OBJECT_GPENCIL'
    # (上面的註釋有點奇怪，一般是寫objectmode)
    # (?)顯示在哪個模式，可用參數有：'objectmode'、'editmode'、'sculptmode'、'vertex_paint'、'weight_paint'、'texture_paint'、'particlemode'、'posemode'、'edit_gpencil'、'sculpt_gpencil'、'weight_gpencil'、'paint_gpencil'、'vertex_gpencil'、'object_gpencil'
    # 如果要在多個模式下顯示，可以用list的方式，例如：bl_context = ["objectmode", "editmode"]
    # x 如果要在所有模式下顯示，可以用all的方式，例如：bl_context = "all" <-- 這看起來是AI唬爛
    # v 如果要在所有模式下顯示，直接把bl_context拿掉即可
    # bl_context = "objectmode"
    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.operator("object.bt_print_bone_name")
        # put another button here
        row = layout.row()
        row.operator("object.bt_vrm_test_button")
        row = layout.row()
        row.operator("vrm.assign_vrm0_humanoid_human_bones_automatically")
        row = layout.row()
        row.operator("vrm.load_human_bone_mappings")
        # export vrm
        row = layout.row()
        row.operator("object.bt_export_vrm")
        
        
        # head mapping
        # bpy.data.armatures["Armature"].vrm_addon_extension.vrm0.humanoid.human_bones[10].node.bone_name


class pn_AssettoWaifuSDK2(bpy.types.Panel):
    bl_idname = "PN_PT_AssettoWaifuSDK2"
    bl_label = "Another Panel"
    bl_category = "Assetto Waifu SDK"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    # bl_context = "objectmode"
    

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        # add a button form the test_reload.py file
        # row.operator("object.bt_test_reload")


classes = [
    vrm_gltf_exporter.VrmValidationError,
    vrm_gltf_exporter.EXPORT_SCENE_OT_aw,
    bt_exportVRM,
    bt_printBoneName,
    bt_vrmTestButton,
    pn_AssettoWaifuSDK,
    pn_AssettoWaifuSDK2,
]
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
 
def unregister():
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except RuntimeError:
            print(f"AWSDK: Failed to Unregister {cls}")
 
if __name__ == "__main__":
    register()
