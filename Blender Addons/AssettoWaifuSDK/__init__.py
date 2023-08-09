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
# - 輸出設定由glb改為gltf

import importlib

# deal with blender submodules reload
# https://blender.stackexchange.com/questions/28504/blender-ignores-changes-to-python-scripts
if "bpy" in locals():
    if "test_reload" in locals():
        importlib.reload(test_reload)
    print("AWSDK: Reloaded Modules.")

import bpy
import os
from bpy_extras.io_utils import ExportHelper



### import modules
from . import test_reload

### external modules
# 搜尋VRM Addon的目錄名稱(即Addon名稱)
# todo: VRM插件不存在時報錯
addons_path = os.path.join(bpy.utils.user_resource('SCRIPTS'), "addons")
for vrmAddonName in os.listdir(addons_path):
    # print(f"addonName: {addonName}")
    if vrmAddonName.startswith("VRM_Addon_for_Blender"):
        print("AWSDK: Found VRM addon: {}".format(vrmAddonName))
        break
else:
    # 如果未找到 VRM 插件的路径，则使用默认路径
    print("AWSDK: VRM addon not found, using default path")
    vrmAddonName = "VRM_Addon_for_Blender_2_17_7"
vrm_export_scene = importlib.import_module(".exporter.export_scene", vrmAddonName)



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

from typing import Optional
from VRM_Addon_for_Blender_2_17_7.editor import migration, search
from VRM_Addon_for_Blender_2_17_7.common.mtoon_unversioned import MtoonUnversioned
from VRM_Addon_for_Blender_2_17_7.common.gltf import (
    FLOAT_NEGATIVE_MAX,
    FLOAT_POSITIVE_MAX,
    TEXTURE_INPUT_NAMES,
    pack_glb,
)
import json
from VRM_Addon_for_Blender_2_17_7.common.deep import Json
def pack_gltf(json_dict: dict[str, Json]) -> bytes:
    ## Original pack_glb()
    # magic = b"glTF" + struct.pack("<I", 2)
    # json_str = json.dumps(json_dict).encode("utf-8")
    # if len(json_str) % 4 != 0:
    #     json_str += b"\x20" * (4 - len(json_str) % 4)
    # json_size = struct.pack("<I", len(json_str))
    # if len(binary_chunk) % 4 != 0:
    #     binary_chunk += b"\x00" * (4 - len(binary_chunk) % 4)
    # bin_size = struct.pack("<I", len(binary_chunk))
    # total_size = struct.pack(
    #     "<I", len(json_str) + len(binary_chunk) + 28
    # )  # include header size
    # return (
    #     magic
    #     + total_size
    #     + json_size
    #     + b"JSON"
    #     + json_str
    #     + bin_size
    #     + b"BIN\x00"
    #     + binary_chunk
    # )
    json_str = json.dumps(json_dict).encode("utf-8")
    return (
        json_str
    )

class awGltfExporter(vrm_export_scene.LegacyVrmExporter):

    #### properties整理

    ## 父class: AbstractBaseVrmExporter
    # self.saved_current_pose_matrix_basis_dict: dict[str, Matrix] = {}
    # self.saved_current_pose_matrix_dict: dict[str, Matrix] = {}
    # self.saved_pose_position: Optional[str] = None
    # self.export_id = "BlenderVrmAddonExport" + (
    #     "".join(secrets.choice(string.digits) for _ in range(10))
    # )

    ## 本class: LegacyVrmExporter

    # 外部參數
    # self.export_objects = export_objects
    # self.export_fb_ngon_encoding = export_fb_ngon_encoding

    # 內部參數
    # self.use_dummy_armature = False

    ## gltf2_addon_export_settings
    #  這主要是VRM1在用的，但LegacyVrmExporter在這些圖片及材質處理時也有用到
    #   image_to_bin()
    #   material_to_dict() --> gltf2_io_material
    # ------
    # self.gltf2_addon_export_settings = (
    #     io_scene_gltf2_support.create_export_settings()
    # )

    # json資料，主要要匯出的資料都在這
    # self.json_dict: dict[str, Json] = {}

    # mesh名稱和index的對應
    # self.mesh_name_to_index: dict[str, int] = {}

    ## (glb_bin_collector) image_to_bin()的結果儲存在此
    # self.glb_bin_collector = GlbBinCollection()

    ## 把某部份export_object的modifier的visibility記錄下來？
    # self.outline_modifier_visibilities: dict[str, dict[str, tuple[bool, bool]]] = {}
    
    # 骨架
    # armatures = [obj for obj in self.export_objects if obj.type == "ARMATURE"]

    # 最後return的結果
    # self.result: Optional[bytes] = None

    def pack(self) -> None:
        # bin_chunk: bytes(), 所有vertex_attribute_bins和image_bin的組合
        # bin_json: txt格式的json，主要是描述bin的資料
        # 內容範例：
        # "bufferViews": [
        #     {
        #         "buffer": 0,
        #         "byteOffset": 0,
        #         "byteLength": 7104
        #     },
        #     ...
        # ],
        # "accessors": [
        #     {
        #         "bufferView": 0,
        #         "byteOffset": 0,
        #         "type": "MAT4",
        #         "componentType": 5126,
        #         "count": 111,
        #         "normalized": False
        #     },
        #     ...
        # ],
        # "images": [
        #     {
        #     "name": "_01",
        #     "bufferView": 144,
        #     "mimeType": "image/png"
        #     },
        #     ...
        # ],
        # "buffers": [
        #     {
        #         "byteLength": 13978130
        #     }
        # ]

        # 把glb_bin_collector的binary資料輸出成json和一大塊bin
        bin_json, bin_chunk = self.glb_bin_collector.pack_all()
        # 更新json_dict
        self.json_dict.update(bin_json)

        # 若鍵值為空，則刪除
        if not self.json_dict["meshes"]:
            del self.json_dict["meshes"]
        if not self.json_dict["materials"]:
            del self.json_dict["materials"]

        # 製作最終glb binary
        # self.result = pack_glb(self.json_dict, bin_chunk)          
        self.result = pack_gltf(self.json_dict)          

    def export_gltf(self) -> Optional[bytes]:
        print("AWSDK: Exporting gltf...")
        wm = self.context.window_manager
        wm.progress_begin(0, 11)
        blend_shape_previews = self.clear_blend_shape_proxy_previews(self.armature)
        object_name_and_modifier_names = self.hide_mtoon1_outline_geometry_nodes()
        try:
            self.setup_pose(
                self.armature,
                self.armature.data.vrm_addon_extension.vrm0.humanoid.pose_library,
                self.armature.data.vrm_addon_extension.vrm0.humanoid.pose_marker_name,
            )
            wm.progress_update(1)

            #--> self.glb_bin_collector
            self.image_to_bin() 
            wm.progress_update(2)

            #--> self.json_dict : "scenes", "nodes", "skins", 
            # (沒寫到的還有)：
            # "images", "animations", "cameras", "extensionsUsed"
            self.armature_to_node_and_scenes_dict()
            wm.progress_update(3)

            # 先從glb_bin_collector讀出image_bin，再寫入json_dict
            #--> self.json_dict : "samplers", "textures", "materials", "extensions":"VRM":"materialProperties"
            # 這邊也有加入一些image到glb_bin_collector
            self.material_to_dict()
            wm.progress_update(4)

            ## 把某部份export_object的modifier的visibility記錄下來？
            #--> modifier_dict (?)
            #--> self.outline_modifier_visibilities
            self.hide_outline_modifiers()
            wm.progress_update(5)
            
            # 這邊會把mesh的資料寫入json_dict
            #--> self.json_dict : "meshes"
            #--> self.mesh_name_to_index[mesh.name] = mesh_index
            # mesh_dicts = self.json_dict.get("meshes")
            # 有作is_skin_mesh判斷，會無視transform (node_dict["translation"]歸零)
            self.mesh_to_bin_and_dict()
            wm.progress_update(6)

            #--> self.modifier_dict
            # 不太清楚作用
            self.restore_outline_modifiers()
            wm.progress_update(7)
            
            #--> self.json_dict.update(gltf_meta_dict)
            # 看起來是把json_dict拉出來，加入一些meta資料，再塞回去
            self.json_dict["scene"] = 0
            self.gltf_meta_to_dict()
            wm.progress_update(8)
            
            # VRM的meta資料，裏面有很多東西
            # 主要也是塞進json_dict
            # 包含：...太多了
            # 後面的日文註解是說："collider" 和 "meta" 之類的東西....
            self.vrm_meta_to_dict()  # colliderとかmetaとか....
            wm.progress_update(9)
            
            # 裏面的注釋寫：
            # 在cluster中，不允许没有材质的基本元素，因此需要分配一个空材质。
            self.fill_empty_material()
            wm.progress_update(10)
            
            #--> self.result
            self.pack()
        finally:
            ## 一些復原工作
            try:
                self.restore_pose(self.armature)
                self.restore_mtoon1_outline_geometry_nodes(
                    object_name_and_modifier_names
                )
                self.restore_blend_shape_proxy_previews(
                    self.armature, blend_shape_previews
                )
                self.cleanup()
            finally:
                wm.progress_end()
        print("AWSDK: gltf OK.")
        return self.result


class VrmValidationError(bpy.types.PropertyGroup):  # type: ignore[misc]
    message: bpy.props.StringProperty()  # type: ignore[valid-type]
    severity: bpy.props.IntProperty(min=0)  # type: ignore[valid-type]

class EXPORT_SCENE_OT_aw(bpy.types.Operator, ExportHelper):  # type: ignore[misc]
    bl_idname = "export_scene.aw"
    bl_label = "Export Assetto Waifu"
    bl_description = "Export Assetto Waifu"
    bl_options = {"REGISTER", "UNDO"}

    filename_ext = ".gltf"
    filter_glob: bpy.props.StringProperty(  # type: ignore[valid-type]
        default="*.gltf", options={"HIDDEN"}  # noqa: F722,F821
    )

    export_invisibles: bpy.props.BoolProperty(  # type: ignore[valid-type]
        name="Export Invisible Objects",  # noqa: F722
        update=vrm_export_scene.export_vrm_update_addon_preferences,
    )
    export_only_selections: bpy.props.BoolProperty(  # type: ignore[valid-type]
        name="Export Only Selections",  # noqa: F722
        update=vrm_export_scene.export_vrm_update_addon_preferences,
    )
    enable_advanced_preferences: bpy.props.BoolProperty(  # type: ignore[valid-type]
        name="Enable Advanced Options",  # noqa: F722
        update=vrm_export_scene.export_vrm_update_addon_preferences,
    )
    export_fb_ngon_encoding: bpy.props.BoolProperty(  # type: ignore[valid-type]
        name="Try the FB_ngon_encoding under development (Exported meshes can be corrupted)",  # noqa: F722
        update=vrm_export_scene.export_vrm_update_addon_preferences,
    )
    errors: bpy.props.CollectionProperty(type=VrmValidationError)  # type: ignore[valid-type]
    armature_object_name: bpy.props.StringProperty(  # type: ignore[valid-type]
        options={"HIDDEN"},  # noqa: F821
    )
    ignore_warning: bpy.props.BoolProperty(  # type: ignore[valid-type]
        options={"HIDDEN"},  # noqa: F821
    )

    # icon可用的參數有：
    # 'NONE', 'QUESTION', 'ERROR', 'CANCEL', 'TRIA_RIGHT', 'TRIA_DOWN', 'TRIA_LEFT', 'TRIA_UP', 'ARROW_LEFTRIGHT', 'PLUS', 'DISCLOSURE_TRI_DOWN', 'DISCLOSURE_TRI_RIGHT', 'RADIOBUT_ON', 'RADIOBUT_OFF', 'MENU_PANEL', 'BLENDER', 'GRIP', 'DOT', 'COLLAPSEMENU', 'X', 'GO_LEFT', 'PLUG', 'UI', 'NODE', 'NODE_SEL', 'FULLSCREEN', 'SPLITSCREEN', 'RIGHTARROW_THIN', 'DOWNARROW_HLT', 'DOTSUP', 'DOTSDOWN', 'LINK_AREA', 'LINK', 'INLINK', 'PLUGIN'
    icon = "NONE"
    msg = ""



    def execute(self, context: bpy.types.Context) -> set[str]:
        if not self.filepath:
            return {"CANCELLED"}

        if bpy.ops.vrm.model_validate(
            "INVOKE_DEFAULT",
            show_successful_message=False,
            armature_object_name=self.armature_object_name,
        ) != {"FINISHED"}:
            return {"CANCELLED"}

        preferences = vrm_export_scene.get_preferences(context)
        export_invisibles = bool(preferences.export_invisibles)
        export_only_selections = bool(preferences.export_only_selections)
        if preferences.enable_advanced_preferences:
            export_fb_ngon_encoding = bool(preferences.export_fb_ngon_encoding)
        else:
            export_fb_ngon_encoding = False

        export_objects = vrm_export_scene.search.export_objects(
            context,
            export_invisibles,
            export_only_selections,
            self.armature_object_name,
        )
        is_vrm1 = any(
            obj.type == "ARMATURE" and obj.data.vrm_addon_extension.is_vrm1()
            for obj in export_objects
        )

        if is_vrm1:
            vrm_exporter: vrm_export_scene.AbstractBaseVrmExporter = vrm_export_scene.Gltf2AddonVrmExporter(
                context, export_objects
            )
        else:
            vrm_exporter = awGltfExporter(
            # vrm_exporter = vrm_export_scene.LegacyVrmExporter(
                context,
                export_objects,
                export_fb_ngon_encoding,
            )

        # vrm_bin = vrm_exporter.export_vrm()
        vrm_bin = vrm_exporter.export_gltf()
        if vrm_bin is None:
            return {"CANCELLED"}
        vrm_export_scene.Path(self.filepath).write_bytes(vrm_bin)
        return {"FINISHED"}

    def invoke(self, context: bpy.types.Context, event: bpy.types.Event) -> set[str]:
        # self.icon = "ERROR"
        # self.msg = "123"

        preferences = vrm_export_scene.get_preferences(context)
        (
            self.export_invisibles,
            self.export_only_selections,
            self.enable_advanced_preferences,
            self.export_fb_ngon_encoding,
        ) = (
            bool(preferences.export_invisibles),
            bool(preferences.export_only_selections),
            bool(preferences.enable_advanced_preferences),
            bool(preferences.export_fb_ngon_encoding),
        )
        if not vrm_export_scene.use_legacy_importer_exporter() and "gltf" not in dir(
            bpy.ops.export_scene
        ):
            return vrm_export_scene.cast(
                set[str],
                bpy.ops.wm.vrm_gltf2_addon_disabled_warning(
                    "INVOKE_DEFAULT",
                ),
            )

        export_objects = vrm_export_scene.search.export_objects(
            context,
            bool(self.export_invisibles),
            bool(self.export_only_selections),
            self.armature_object_name,
        )

        armatures = [obj for obj in export_objects if obj.type == "ARMATURE"]
        if len(armatures) > 1:
            bpy.ops.wm.vrm_export_armature_selection("INVOKE_DEFAULT")
            return {"CANCELLED"}
        if len(armatures) == 1 and armatures[0].data.vrm_addon_extension.is_vrm0():
            armature = armatures[0]
            vrm_export_scene.Vrm0HumanoidPropertyGroup.fixup_human_bones(armature)
            vrm_export_scene.Vrm0HumanoidPropertyGroup.check_last_bone_names_and_update(
                armature.data.name,
                defer=False,
            )
            humanoid = armature.data.vrm_addon_extension.vrm0.humanoid
            if all(
                b.node.bone_name not in b.node_candidates for b in humanoid.human_bones
            ):
                bpy.ops.vrm.assign_vrm0_humanoid_human_bones_automatically(
                    armature_name=armature.name
                )
            if not humanoid.all_required_bones_are_assigned():
                bpy.ops.wm.vrm_export_human_bones_assignment(
                    "INVOKE_DEFAULT", armature_object_name=self.armature_object_name
                )
                return {"CANCELLED"}
        elif len(armatures) == 1 and armatures[0].data.vrm_addon_extension.is_vrm1():
            armature = armatures[0]
            vrm_export_scene.Vrm1HumanBonesPropertyGroup.fixup_human_bones(armature)
            vrm_export_scene.Vrm1HumanBonesPropertyGroup.check_last_bone_names_and_update(
                armature.data.name,
                defer=False,
            )
            human_bones = armature.data.vrm_addon_extension.vrm1.humanoid.human_bones
            if all(
                human_bone.node.bone_name not in human_bone.node_candidates
                for human_bone in human_bones.human_bone_name_to_human_bone().values()
            ):
                bpy.ops.vrm.assign_vrm1_humanoid_human_bones_automatically(
                    armature_name=armature.name
                )
            if not human_bones.all_required_bones_are_assigned():
                bpy.ops.wm.vrm_export_human_bones_assignment(
                    "INVOKE_DEFAULT", armature_object_name=self.armature_object_name
                )
                return {"CANCELLED"}

        if bpy.ops.vrm.model_validate(
            "INVOKE_DEFAULT",
            show_successful_message=False,
            armature_object_name=self.armature_object_name,
        ) != {"FINISHED"}:
            return {"CANCELLED"}

        vrm_export_scene.validation.WM_OT_vrm_validator.detect_errors(
            context,
            self.errors,
            self.armature_object_name,
        )
        if not self.ignore_warning and any(
            error.severity <= 1 for error in self.errors
        ):
            bpy.ops.wm.vrm_export_confirmation(
                "INVOKE_DEFAULT", armature_object_name=self.armature_object_name
            )
            return {"CANCELLED"}

        return vrm_export_scene.cast(set[str], ExportHelper.invoke(self, context, event))

    def draw(self, context: bpy.types.Context) -> None:
        # These codes are copied from export_scene.VRM_PT_export_error_messages()
        # It's poll fucntion is set to str(context.space_data.active_operator.bl_idname) == "EXPORT_SCENE_OT_vrm"
        # So the options are only displayed in EXPORT_SCENE_OT_vrm, not in EXPORT_SCENE_OT_aw
        layout = self.layout

        operator = context.space_data.active_operator

        layout.prop(operator, "export_invisibles")
        layout.prop(operator, "export_only_selections")
        layout.prop(operator, "enable_advanced_preferences")
        if operator.enable_advanced_preferences:
            advanced_options_box = layout.box()
            advanced_options_box.prop(operator, "export_fb_ngon_encoding")

        if operator.errors:
            vrm_export_scene.validation.WM_OT_vrm_validator.draw_errors(
                operator.errors, False, layout.box()
            )

        if self.msg:
            row = layout.row()
            row.emboss = "NONE"
            row.box().label(text=self.msg, icon=self.icon)


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
    VrmValidationError,
    EXPORT_SCENE_OT_aw,
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
