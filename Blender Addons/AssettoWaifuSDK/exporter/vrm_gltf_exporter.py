import importlib
import bpy
import os
from bpy_extras.io_utils import ExportHelper


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

# Replaces the original VRM Exporter
class LegacyVrmExporter(vrm_export_scene.LegacyVrmExporter):

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

# types is needed to be defined for EXPORT_SCENE_OT_aw class
class VrmValidationError(bpy.types.PropertyGroup):  # type: ignore[misc]
    message: bpy.props.StringProperty()  # type: ignore[valid-type]
    severity: bpy.props.IntProperty(min=0)  # type: ignore[valid-type]

# rm_export_scene.export_vrm_update_addon_preferences,
class EXPORT_SCENE_OT_aw(vrm_export_scene.EXPORT_SCENE_OT_vrm):  # type: ignore[misc]
    bl_idname = "export_scene.aw"
    bl_label = "Export Assetto Waifu"
    bl_description = "Export Assetto Waifu"

    filename_ext = ".gltf"
    filter_glob: bpy.props.StringProperty(  # type: ignore[valid-type]
        default="*.gltf", options={"HIDDEN"}  # noqa: F722,F821
    )

    errors: bpy.props.CollectionProperty(type=VrmValidationError)  # type: ignore[valid-type]

    # Error msg diplay
    # Available icons types:
    # 'NONE', 'QUESTION', 'ERROR', 'CANCEL', 'TRIA_RIGHT', 'TRIA_DOWN', 'TRIA_LEFT', 'TRIA_UP', 'ARROW_LEFTRIGHT', 'PLUS', 'DISCLOSURE_TRI_DOWN', 'DISCLOSURE_TRI_RIGHT', 'RADIOBUT_ON', 'RADIOBUT_OFF', 'MENU_PANEL', 'BLENDER', 'GRIP', 'DOT', 'COLLAPSEMENU', 'X', 'GO_LEFT', 'PLUG', 'UI', 'NODE', 'NODE_SEL', 'FULLSCREEN', 'SPLITSCREEN', 'RIGHTARROW_THIN', 'DOWNARROW_HLT', 'DOTSUP', 'DOTSDOWN', 'LINK_AREA', 'LINK', 'INLINK', 'PLUGIN'
    icon = "NONE"
    msg = ""

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

