import bpy
from bpy.types import Panel
from bl_ui.utils import PresetPanel
from . propertieshandler import props, texture_importer, texture_index, lines

def draw_panel(self,context):
    layout = self.layout
    row = layout.row()
    row.template_list(
        "NODE_UL_stm_list", "Textures",
        texture_importer(), "textures",
        texture_importer(), "texture_index",
        type="GRID",
        columns=1,
        rows=6,
    )
    button_col = row.column(align=True)
    button_col.operator("node.stm_add_item", icon="ADD", text="")
    button_col.operator("node.stm_remove_item", icon="REMOVE", text="")
    button_col.separator(factor=.5)
    button_col.operator("node.stm_move_line", icon="TRIA_UP", text="").down= False
    button_col.operator("node.stm_move_line", icon="TRIA_DOWN", text="").down= True
    button_col.separator(factor=.5)
    button_col.operator("node.stm_fill_names", icon="SETTINGS", text="")
    button_col.separator(factor=2)
    button_col.operator("node.stm_reset_substance_textures", icon="MEMORY", text="")
    if lines() and texture_index() < len(lines()):
        item = lines()[texture_index()]
        layout.prop(item, "line_on")
        sub_layout = layout.column()
        sub_layout.enabled = item.line_on
        sub_layout.prop(item, "auto_mode")
        sub_sub_layout = layout.column()
        sub_sub_layout.enabled = not item.auto_mode
        sub_sub_layout.prop(item, "split_rgb")
        if item.split_rgb:
            if item.channels.socket :
                sl = sub_layout.column()
                sl.enabled = not item.auto_mode and item.line_on
                for i,sk in enumerate(item.channels.socket):
                    sl.prop(sk, "input_sockets",text=sk.name,icon=f"SEQUENCE_COLOR_0{((i*3)%9+1)}")
        if props().advanced_mode :
            sub_sub_layout = sub_layout.column()
            sub_sub_layout.prop(item, "manual")
            if item.manual :
                sub_sub_sub_layout = sub_sub_layout.column()
                sub_sub_sub_layout.prop(item, "file_name")
        if not item.split_rgb:
            sub_layout_2 = layout.column()
            sub_layout_2.enabled = not item.auto_mode and item.line_on
            sub_layout_2.prop(item, "input_sockets")

class TexImporterPanel():
    bl_context = "material"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "STM"

    @classmethod
    def poll(cls, context):
        try:
            return context.preferences.addons[__package__].preferences.display_in_editor
        except (TypeError,NameError,KeyError,ValueError,AttributeError,OverflowError):
            return False


class NODE_PT_stm_presets(PresetPanel, Panel):
    bl_label = 'Presets'
    preset_subdir = 'stm_presets'
    preset_operator = 'node.stm_execute_preset'
    preset_add_operator = 'node.stm_add_preset'


class NODE_PT_stm_importpanel(TexImporterPanel, Panel):
    bl_idname = "NODE_PT_stm_importpanel"
    bl_label = "Substance Texture Importer"

    def draw_header_preset(self, _context):
        l = self.layout
        l.operator("node.stm_presets_dialog", text="",icon='PRESET',emboss=False)

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(props(), "target")


class NODE_PT_stm_params(TexImporterPanel, Panel):

    bl_idname = "NODE_PT_stm_params"
    bl_label = "Maps Folder:"
    bl_parent_id = "NODE_PT_stm_importpanel"

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(props(), "usr_dir")


class NODE_PT_stm_panel_liner(TexImporterPanel,Panel):
    bl_label = "Textures:"
    bl_idname = "NODE_PT_stm_substance_texture_importer"
    bl_parent_id = "NODE_PT_stm_importpanel"

    def draw(self, context):
        draw_panel(self,context)


class NODE_PT_stm_prefs(TexImporterPanel,Panel):

    bl_idname = "NODE_PT_stm_prefs"
    bl_label = ""
    bl_parent_id = "NODE_PT_stm_importpanel"
    bl_options = {'HIDE_HEADER'}

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.alignment = 'LEFT'
        row.prop(props(), "advanced_mode", text="Manual Mode ", )


class NODE_PT_stm_buttons(TexImporterPanel, Panel):

    bl_idname = "NODE_PT_stm_buttons"
    bl_label = "Options"
    bl_parent_id = "NODE_PT_stm_importpanel"
    bl_options = {'HIDE_HEADER'}

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        col = row.column(align = True)
        col.operator("node.stm_import_textures")
        col.separator()
        row = col.row(align = True)
        col = layout.column(align = True)
        row = col.row(align = True)
        row.operator("node.stm_assign_nodes")
        row.separator()
        row.operator("node.stm_make_nodes")


class NODE_PT_stm_options(TexImporterPanel, Panel):

    bl_idname = "NODE_PT_stm_options"
    bl_label = "Options"
    bl_parent_id = "NODE_PT_stm_importpanel"

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        col = row.column(align = True)
        row = col.row(align = True)
        row.prop(props(), "replace_shader", text="Replace Shader",)
        row = row.split()
        if props().replace_shader :
            row.prop(props(), "shaders_list", text="")
        row = layout.row()
        row.prop(props(), "skip_normals", )
        row = layout.row()
        row.prop(props(), "mode_opengl", )
        row = layout.row()
        row.prop(props(), "include_ngroups", text="Enable Custom Shaders", )
        row = layout.row()
        row.prop(props(), "clear_nodes", text="Clear nodes from material", )
        row = layout.row()
        row.prop(props(), "tweak_levels", text="Attach Curves and Ramps ", )
        row = layout.row()
        row.prop(props(), "only_active_mat", text="Only active Material",)
        row = layout.row()
        row.prop(props(), "dup_mat_compatible", text="Duplicated material compatibility",)
        row = layout.row()
        row.prop(props(), "lines_from_files", text="Map names from files",)
        row = layout.row()
        row.separator()
