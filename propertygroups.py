import bpy
from pathlib import Path
from bpy.props import (StringProperty,IntProperty,BoolProperty,EnumProperty,CollectionProperty)
from bpy.types import PropertyGroup
from bpy.utils import (register_class,unregister_class)
from . propertieshandler import PropertiesHandler,props,node_links,lines,p_lines,set_wish,get_wish
from . nodeshandler import NodeHandler

propper = PropertiesHandler()
ndh = NodeHandler()
_msgbus_owner = None

def line_on_up(self, context):
    propper.default_sockets(self)
    propper.safe_refresh()
    propper.wish = set_wish()

def material_update_callback():
    if not props().replace_shader:
        if set_wish() != propper.wish:
            get_wish(propper.wish)
    try:
        propper.mat = ndh.mat = bpy.context.object.active_material
        refresh_props(props(),bpy.context)
    except (TypeError,NameError,KeyError,ValueError,AttributeError,OverflowError):
        return

def unregister_msgbus():
    global _msgbus_owner
    if _msgbus_owner:
        bpy.msgbus.clear_by_owner(_msgbus_owner)
        _msgbus_owner = None

def register_msgbus():
    global _msgbus_owner
    _msgbus_owner = object()

    bpy.msgbus.subscribe_rna(
        key=(bpy.types.Object, "active_material"),
        owner=_msgbus_owner,
        args=(),
        notify=material_update_callback
    )
    bpy.msgbus.subscribe_rna(
        key=(bpy.types.Object, "active_material_index"),
        owner=_msgbus_owner,
        args=(),
        notify=material_update_callback
    )
    bpy.msgbus.subscribe_rna(
        key=(bpy.types.LayerObjects, "active"),
        owner=_msgbus_owner,
        args=(),
        notify=material_update_callback
    )
    bpy.msgbus.subscribe_rna(
        key=(bpy.types.MaterialSlot, "link"),
        owner=_msgbus_owner,
        args=(),
        notify=material_update_callback
    )
    bpy.msgbus.subscribe_rna(
        key=(bpy.types.MaterialSlot, "material"),
        owner=_msgbus_owner,
        args=(),
        notify=material_update_callback
    )
    bpy.msgbus.subscribe_rna(
        key=(bpy.types.Object, "material_slots"),
        owner=_msgbus_owner,
        args=(),
        notify=material_update_callback
    )
    #not sure
    bpy.msgbus.subscribe_rna(
        key=(bpy.types.Material, "node_tree"),
        owner=_msgbus_owner,
        args=(),
        notify=material_update_callback
    )



def target_list_cb(self,context):
    targets = [('selected_objects', 'Selected Objects materials', '',0),
                ('all_visible', 'All visible Objects materials', '',1),
                ('all_objects', 'All Objects materials', '',2),
                ('all_materials', 'All scene materials', '',3),
                ('active_obj', 'Only Active Object in selection', '',4),
            ]
    return targets

def get_presets(self, context):
    return propper.get_preset_list()

def apply_preset(self,context):
    propper.read_preset()

def preset_enum_up(self, context):
    apply_preset(self,context)

def target_list_up(self,context):
    match self.target:
        case "selected_objects":
            set_operator_description("selected objects materials.")
        case "all_visible":
            set_operator_description("all visible objects materials.")
        case "all_objects":
            set_operator_description("all objects materials in the current viewlayer.")
        case "all_materials":
            set_operator_description("all the materials in the blend.")
            self.only_active_mat = False
        case "active_obj":
            pass

def set_operator_description(target):
    bpy.types.NODE_OT_stm_import_textures.bl_description = "Setup nodes and load textures\
                                                            \n maps on " + target
    bpy.types.NODE_OT_stm_make_nodes.bl_description = "Setup Nodes on " + target
    bpy.types.NODE_OT_stm_assign_nodes.bl_description = "Load textures maps on " + target
    liste = [
        bpy.types.NODE_OT_stm_import_textures,
        bpy.types.NODE_OT_stm_make_nodes,
        bpy.types.NODE_OT_stm_assign_nodes
    ]
    for cls in liste:
        laclasse = cls
        unregister_class(cls)
        register_class(laclasse)

def split_rgb_up(self,context):
    if not (len(self.channels.socket) and len(self.channels.socket) == 3):
        propper.make_clean_channels(self)
    if self.auto_mode:
        propper.default_sockets(self)
    ch_sockets_up(self,context) if self.split_rgb else enum_sockets_up(self,context)
    propper.wish = set_wish()

def include_ngroups_up(self, context):
    if props().include_ngroups:
        propper.set_nodes_groups()
    else:
        node_links().clear()
    propper.set_enum_sockets_items()
    propper.safe_refresh()
    propper.guess_sockets()
    propper.wish = set_wish()

def enum_sockets_cb(self, context):
    inp_list = None
    try:
        inp_list = propper.get_sockets_enum_items()
    except (TypeError,NameError,KeyError,ValueError,AttributeError,OverflowError):
        if not inp_list or len(inp_list) < 5:
            return [('no_socket','-- Unmatched Socket --',''),('Base Color','Base Color',''),
                    ('Metallic','Metallic',''),('Roughness','Roughness',''),
                    ('IOR','IOR',''),('Alpha','Alpha',''),('Normal','Normal',''),
                    ('Diffuse Roughness','Diffuse Roughness',''),
                    ('Subsurface Weight','Subsurface Weight',''),
                    ('Subsurface Radius','Subsurface Radius',''),
                    ('Subsurface Scale','Subsurface Scale',''),
                    ('Subsurface IOR','Subsurface IOR',''),
                    ('Subsurface Anisotropy','Subsurface Anisotropy',''),
                    ('Specular IOR Level','Specular IOR Level',''),
                    ('Specular Tint','Specular Tint',''),('Anisotropic','Anisotropic',''),
                    ('Anisotropic Rotation','Anisotropic Rotation',''),('Tangent','Tangent',''),
                    ('Transmission Weight','Transmission Weight',''),
                    ('Coat Weight','Coat Weight',''),('Coat Roughness','Coat Roughness',''),
                    ('Coat IOR','Coat IOR',''),('Coat Tint','Coat Tint',''),
                    ('Coat Normal','Coat Normal',''),('Sheen Weight','Sheen Weight',''),
                    ('Sheen Roughness','Sheen Roughness',''),('Sheen Tint','Sheen Tint',''),
                    ('Emission Color','Emission Color',''),
                    ('Emission Strength','Emission Strength',''),
                    ('Thin Film Thickness','Thin Film Thickness',''),
                    ('Thin Film IOR','Thin Film IOR',''),
                    ('Disp Vector','Disp Vector',''),('Displacement','Displacement',''),
                    ('Ambient Occlusion','Ambient Occlusion',''),]
    return inp_list

def enum_sockets_up(self, context):
    if self.input_sockets not in propper.sicks():
        self['input_sockets'] = 0
        return
    for line in p_lines():
        if line.split_rgb:
            for sk in line.channels.socket:
                if sk.input_sockets in self.input_sockets and not 'no_socket' in self.input_sockets and not sk.line_name in self.name:
                    sk['input_sockets'] = 0
                    print("from mono")
                    line.auto_mode = False
        elif line.input_sockets in self.input_sockets and not 'no_socket' in self.input_sockets and not line == self:
            line['input_sockets'] = 0
            line.auto_mode = False

def ch_sockets_up(self, context):
    if not self.input_sockets in propper.sicks():
        self['input_sockets'] = 0
        return
    for line in p_lines():
        if line.split_rgb:
            for sk in line.channels.socket:
                if sk.input_sockets in self.input_sockets and not 'no_socket' in self.input_sockets and not self == sk and not sk.line_name in line.name:
                    sk['input_sockets'] = 0
                    print("from multi")
                    line.auto_mode = False
        elif line.input_sockets in self.input_sockets and not 'no_socket' in self.input_sockets and not self.line_name in line.name:
            line['input_sockets'] = 0
            line.auto_mode = False

def shaders_list_cb(self, context):
    return propper.get_shaders_list()

def shaders_list_up(self, context):
    #forces rebuilding the sockets list
    self.replace_shader = not self.replace_shader
    self.replace_shader = not self.replace_shader
    propper.wish = set_wish()
    context.view_layer.update()

def manual_up(self, context):
    if self.manual:
        props().target = 'active_obj'
        props().only_active_mat = True
    else:
        ndh.detect_a_map(self)

def advanced_mode_up(self, context):
    propper.safe_refresh()
    if not self.advanced_mode:
        for line in lines():
            line.manual = False
    propper.wish = set_wish()

def usr_dir_up(self, context):
    if self.lines_from_files:
        propper.synch_names()
    self.dir_content = ""
    if not Path(self.usr_dir).is_dir():
        self.usr_dir = str(Path(self.usr_dir).parent)
        if not Path(self.usr_dir).is_dir():
            self.usr_dir = Path(bpy.utils.extension_path_user(f'{__package__}', create=True))
    exts = set(bpy.path.extensions_image)
    dir_content = [x.name for x in Path(self.usr_dir).glob('*.*') if x.suffix.lower() in exts]
    if len(dir_content) :
        for img in dir_content:
            i = props().img_files.add()
            i.name = img
    if self.include_ngroups:
        node_links().clear()
        include_ngroups_up(self,context)
    propper.guess_sockets()
    propper.wish = set_wish()
    context.view_layer.update()

def dup_mat_compatible_up(self,context):
    ndh.detect_relevant_maps()
    propper.wish = set_wish()

def clear_nodes_up(self, context):
    if self.clear_nodes:
        self.replace_shader = True
    propper.wish = set_wish()

def auto_mode_up(self,context):
    if self.auto_mode:
        propper.default_sockets(self)
    propper.wish = set_wish()

def only_active_mat_up(self, context):
    if "all_materials" in self.target and self.only_active_mat:
        self.target = "selected_objects"
    propper.safe_refresh()
    propper.wish = set_wish()

def refresh_props(self,context):
    propper.set_enum_sockets_items()
    if self.include_ngroups:
        node_links().clear()
        include_ngroups_up(self,context)
    propper.safe_refresh()
    propper.guess_sockets()

def replace_shader_up(self, context):
    refresh_props(self,context)
    propper.wish = set_wish()
    context.view_layer.update()

def separators_cb(self,context):
    return [("_","_","(underscore)"),("-","-","(minus sign)"),(",",",","(comma)"),(";",";","(semicolon)"),(".",".","(dot)"),("+","+","(plus sign)"),("&","&","(ampersand)")]

def stm_all_up(self,context):
    propper.load_props()

class StringItem(PropertyGroup):

    name: StringProperty(
        name="sock",
        default=""
    )

class ShaderLinks(PropertyGroup):

    ID: IntProperty(
        name="ID",
        default=0
    )
    name: StringProperty(
        name="named",
        default="Principled BSDF"
    )
    shadertype: StringProperty(
        name="internal name",
        default='ShaderNodeBsdfPrincipled'
    )
    in_sockets : CollectionProperty(type=StringItem)

class NodesLinks(PropertyGroup):

    ID: IntProperty(
        name="ID",
        default=0
    )
    name: StringProperty(
        name="named",
        default="Unknown name"
    )
    nodetype: StringProperty(
        name="internal name",
        default="{'0':''}"
    )
    in_sockets : CollectionProperty(type=StringItem)


class StmProps(PropertyGroup):

    include_ngroups: BoolProperty(
        name="Enable or Disable",
        description=" Append your own Nodegroups in the 'Replace Shader' list above \
                    \n\
                    \n Allows to use Custom Shader nodes\
                    \n Custom NodeGroups must have a valid Surface Shader output socket \
                    \n and at least one input socket to appear in the list \
                    \n (Experimental !!!)",
        default=False,
        update=include_ngroups_up
    )
    clear_nodes: BoolProperty(
        name="Enable or Disable",
        description=" Clear existing nodes \
                     \n Removes all nodes from the material shader \
                     \n before setting up the nodes trees",
        default=True,
        update=clear_nodes_up
    )
    target: EnumProperty(
        name="Target ",
        description=" Objects or materials affected by the operations ",
        items=target_list_cb,
        update=target_list_up
    )
    tweak_levels: BoolProperty(
        name="Enable or Disable",
        description=" Attach RGB Curves and Color Ramps nodes\
                        \n\
                        \n Inserts a RGB Curve if the Texture map type is RGB \
                        \n or a Color ramp if the texture map type is Black & White\
                        \n between the Image texture node and the Shader Input Socket\
                        \n during Nodes Trees setup",
        default=False
    )
    mode_opengl: BoolProperty(
        name="OpenGL Normals",
        description=" Disable to use DirectX™ normal map format instead of OpenGL.\
                        \n\
                        \n When this option is disabled, the script inverts the Y channel\
                        \n of the normal map to match blender format by adding a RGBCurve\
                        \n node with the green channel curve inverted before a normal map\
                        \n is plugged during Nodes Trees setup",
        default=True
    )

    usr_dir: StringProperty(
        name="",
        description="Folder containing the Textures Images to be imported",
        subtype="DIR_PATH",
        default=bpy.utils.extension_path_user(f'{__package__}', create=True),
        update=usr_dir_up
    )
    stm_all: StringProperty(
        name="all_settings",
        description="string dict of all settings, used internally for preset saving",
        default="{'0':'0'}",
        update=stm_all_up
    )
    in_sockets : CollectionProperty(type=StringItem)
    img_files: CollectionProperty(type=StringItem)

    skip_normals: BoolProperty(
        name="Skip normal map detection",
        description=" Skip Normal maps and Height maps detection.\
                            \n\
                            \n Usually the script inserts a Normal map converter node \
                            \n or a Bump map converter node according to the texture maps name.\
                            \n Tick to link the texture map directly",
        default=False
    )
    replace_shader: BoolProperty(
        description=" Enable to replace the Material Shader with the one in the list \
                       \n\
                       \n (Enabled by default if 'Apply to all' is activated)",
        default=True,
        update=replace_shader_up
    )
    shaders_list: EnumProperty(
        name="shaders_list:",
        description=" Base Shader node selector \
                        \n Used to select a replacement for the current Shader node\
                        \n if 'Replace Shader' is enabled or if no valid Shader node is detected.",

        items=shaders_list_cb,
        update=shaders_list_up
    )
    separators_list: EnumProperty(
        name="separators_list:",
        description=" Selector for the separator used to detect multi-sockets.\
                        \n If your texture map name contains multiple keywords like\
                        \n material_bump,metallic,ambient.exr , material_bump-metallic-ambient.exr\
                        \n or material_bump;metallic;ambient.exr etc. \
                        \n Adjust this to fit the separator character between your maps keywords.",

        items=separators_cb,
    )
    lines_from_files: BoolProperty(
        description=" Attempt to auto rename the map lines names according to\
                    \n the images names detected in the texture folder when updating the directory\
                    \n if they match the current material name.",
        default=True,
    )
    advanced_mode: BoolProperty(
        description=" Allows Manual setup of the Maps filenames, \
                    \n  (Tick the checkbox between Map Name and Sockets \
                                        to enable manual file selection)",
        default=False,
        update=advanced_mode_up
    )
    only_active_mat: BoolProperty(
        description=" Apply on active material only, \
                        \n  (By default the script iterates through all materials\
                        \n  presents in the Material Slots.)\
                        \n Enable this to only use the active Material Slot.",
        default=False,
        update=only_active_mat_up
    )
    dup_mat_compatible: BoolProperty(
        description=" Process duplicated materials names like the originals, \
                        \n  Use this to treat materials with suffix .001\
                        \n  as the original ones (ignores the .00x suffix)",
        default=True
    )
    custom_preset_name: StringProperty(
        name="Preset Name",
        description="Name of the preset.",
        default="New Preset"
    )
    preset_enum: EnumProperty(name="Presets",items=get_presets,update=preset_enum_up)
