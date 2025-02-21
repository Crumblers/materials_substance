import bpy
from pathlib import Path
from os.path import commonprefix

def props():
    return getattr(bpy.context.preferences.addons[__package__].preferences, "props", None)

def node_links():
    return getattr(bpy.context.preferences.addons[__package__].preferences, "node_links", None)

def shader_links():
    return getattr(bpy.context.preferences.addons[__package__].preferences, "shader_links", None)

def texture_importer():
    return getattr(bpy.context.preferences.addons[__package__].preferences, "maps", None)

def texture_index():
    return getattr(texture_importer(), "texture_index", None)

def lines():
    return getattr(texture_importer(), "textures", None)

def p_lines():
    return [line for line in lines() if line.line_on]

def line_index(line):
    for i,liner in enumerate(lines()) :
        if liner == line:
            return i
    return None

def set_wish():
    wish = {line.name: (line['input_sockets'],[ch['input_sockets'] for ch in line.channels.socket]) for line in lines()}
    return wish

def get_wish(wish):
    for name, value in wish.items():
        try:
            lines()[name]['input_sockets'] = value[0]
        except (TypeError,NameError,KeyError,ValueError,AttributeError,OverflowError):
            lines()[name]['input_sockets'] = 0
        for i,ch in enumerate(lines()[name].channels.socket):
            try:
                ch['input_sockets'] = value[1][i]
            except (TypeError,NameError,KeyError,ValueError,AttributeError,OverflowError):
                ch['input_sockets'] = 0

def sockets_holder(func):
    def wrapper(self, *args, **kwargs):
        wish = set_wish()
        result = func(self,*args, **kwargs)
        get_wish(wish)
        return result
    return wrapper

class MaterialHolder():
    def __init__(self):
        self.wish = {}
        self._mat = None
        self._tree = None
        self._nodes = None
        self._links = None

    @property
    def mat(self):
        if self._mat is None and bpy.context.object.active_material:
            try :
                self.mat = bpy.context.object.active_material
                return bpy.context.object.active_material
            except (TypeError,NameError,KeyError,ValueError,AttributeError,OverflowError):
                pass
        return self._mat

    @mat.setter
    def mat(self, value):
        if value is None or isinstance(value, bpy.types.Material):
            self._mat = value
        else:
            raise ValueError("mat must be a bpy.types.Material or None")
        self._update_tree_and_nodes()

    @property
    def tree(self):
        return self._tree

    @tree.setter
    def tree(self, value):
        self._tree = value

    @property
    def nodes(self):
        if not self._nodes and self.mat and self.mat.node_tree:
            self._nodes = self.mat.node_tree.nodes
        return self._nodes

    @nodes.setter
    def nodes(self, value):
        self._nodes = value

    @property
    def links(self):
        return self._links

    @links.setter
    def links(self, value):
        self._links = value

    def _update_tree_and_nodes(self):
        if self._mat is not None:
            self._tree = getattr(self._mat, 'node_tree', None)
            self._nodes = getattr(self._tree, 'nodes', None)
            self._links = getattr(self._tree, 'links', None)
        else:
            self._tree = None
            self._nodes = None
            self._links = None


class PropertiesHandler(MaterialHolder):

    def sicks(self):
        return [sc[0] for sc in self.get_sockets_enum_items()]

    def get_shaders_list_eve(self):
        shaders_list = [
            ('ShaderNodeVolumePrincipled', 'Principled Volume', ''),
            ('ShaderNodeVolumeScatter', 'Volume Scatter', ''),
            ('ShaderNodeVolumeAbsorption', 'Volume Absorption', ''),
            ('ShaderNodeEmission', 'Emission', ''),
            ('ShaderNodeBsdfDiffuse', 'Diffuse BSDF', ''),
            ('ShaderNodeBsdfGlass', 'Glass BSDF', ''),
            ('ShaderNodeBsdfGlossy', 'Glossy BSDF', ''),
            ('ShaderNodeBsdfRefraction', 'Refraction BSDF', ''),
            ('ShaderNodeSubsurfaceScattering', 'Subsurface Scattering BSSRDF', ''),
            ('ShaderNodeEeveeSpecular', 'Specular BSDF', ''),
            ('ShaderNodeBsdfTranslucent', 'Translucent BSDF', ''),
            ('ShaderNodeBsdfTransparent', 'Transparent BSDF', ''),
            ('ShaderNodeBsdfPrincipled', 'Principled BSDF', ''),
        ]
        if props().include_ngroups:
            for i in node_links():
                shaders_list.append((i.nodetype, i.nodetype, ''), )
        shaders_list.reverse()
        return shaders_list

    def get_shaders_list(self):
        if bpy.context.scene.render.engine == 'BLENDER_EEVEE_NEXT' :
            return self.get_shaders_list_eve()
        if bpy.context.scene.render.engine == 'CYCLES' :
            return self.get_shaders_list_cycles()
        return None

    def make_clean_channels(self,line):
        line.channels.socket.clear()
        for i in range(3):
            item = line.channels.socket.add()
            item.name = "RGB"[i]
            item.line_name = line.name
            item['input_sockets'] = 0

    def initialize_defaults(self):
        lines().clear()
        maps = ["Color","Metallic","Roughness","Normal"]
        for i in range(4):
            item = lines().add()
            item.name = f"{maps[i]}"
            self.make_clean_channels(item)
            self.default_sockets(item)

    @sockets_holder
    def safe_refresh(self,context=None):
        self.clean_input_sockets()
        self.refresh_shader_links()

    def get_shaders_list_cycles(self):
        shaders_list = [
            ('ShaderNodeBsdfHairPrincipled', 'Principled-Hair BSDF', ''),
            ('ShaderNodeVolumePrincipled', 'Principled Volume', ''),
            ('ShaderNodeVolumeScatter', 'Volume Scatter', ''),
            ('ShaderNodeVolumeAbsorption', 'Volume Absorption', ''),
            ('ShaderNodeEmission', 'Emission', ''),
            ('ShaderNodeBsdfDiffuse', 'Diffuse BSDF', ''),
            ('ShaderNodeBsdfGlass', 'Glass BSDF', ''),
            ('ShaderNodeBsdfGlossy', 'Glossy BSDF', ''),
            ('ShaderNodeBsdfRefraction', 'Refraction BSDF', ''),
            ('ShaderNodeSubsurfaceScattering', 'Subsurface Scattering BSSRDF', ''),
            ('ShaderNodeBsdfToon', 'Toon BSDF', ''),
            ('ShaderNodeBsdfTranslucent', 'Translucent BSDF', ''),
            ('ShaderNodeBsdfTransparent', 'Transparent BSDF', ''),
            ('ShaderNodeBsdfHair', 'Hair BSDF', ''),
            ('ShaderNodeBsdfSheen', 'Sheen BSDF', ''),
            ('ShaderNodeBsdfPrincipled', 'Principled BSDF', ''),
        ]
        if props().include_ngroups:
            for i in node_links():
                shaders_list.append((i.nodetype, i.nodetype, ''), )
        shaders_list.reverse()
        return shaders_list

    def set_nodes_groups(self):
        ng = bpy.data.node_groups
        node_links().clear()
        mat_tmp = bpy.data.materials.new(name="tmp_mat")
        mat_tmp.use_nodes = True
        for nd in ng:
            nw = mat_tmp.node_tree.nodes.new('ShaderNodeGroup')
            nw.node_tree = nd
            if len(nw.inputs) + len(nw.outputs) > 0:
                new_link = node_links().add()
                new_link.name = nd.name
                new_link.label = nd.name
                new_link.nodetype = nd.name
                for sk in [n.name for n in nw.inputs if n.type != "SHADER"]:
                    si = new_link.in_sockets.add()
                    si.name = sk
        mat_tmp.node_tree.nodes.clear()
        bpy.data.materials.remove(mat_tmp)

    def parse_dict_string(self, s):
        s = s.strip()
        if s.startswith("{") and s.endswith("}"):
            s = s[1:-1].strip()
        parsed_dict = {}
        key = None
        value = None
        in_list = False
        in_dict = False
        buffer = ""
        list_buffer = []
        i = 0
        while i < len(s):
            char = s[i]
            if char == ":" and not in_list and not in_dict:
                key = buffer.strip().strip("'").strip('"')
                buffer = ""
            elif char == "," and not in_list and not in_dict:
                if key is not None:
                    parsed_dict[key] = self.convert_value(buffer.strip())
                    key = None
                buffer = ""
            elif char == "[":
                in_list = True
                list_buffer = []
                buffer = ""
            elif char == "]":
                in_list = False
                list_buffer.append(self.convert_value(buffer.strip()))
                parsed_dict[key] = list_buffer
                key = None
                buffer = ""
            elif char == "{":
                in_dict = True
                nested_dict_start = i
                brace_count = 1
                while brace_count > 0 and i + 1 < len(s):
                    i += 1
                    if s[i] == "{":
                        brace_count += 1
                    elif s[i] == "}":
                        brace_count -= 1
                nested_dict = s[nested_dict_start:i + 1]
                parsed_dict[key] = self.parse_dict_string(nested_dict)
                key = None
                buffer = ""
            elif char == "'" or char == '"':
                pass
            else:
                if in_list and char == ",":
                    list_buffer.append(self.convert_value(buffer.strip()))
                    buffer = ""
                else:
                    buffer += char
            i += 1
        if key is not None and buffer.strip():
            parsed_dict[key] = self.convert_value(buffer.strip())
        return parsed_dict

    def convert_value(self, value):
        value = value.strip()
        if value.lower() == "true":
            return True
        elif value.lower() == "false":
            return False
        elif value.isdigit():
            return int(value)
        elif value.replace(".", "", 1).isdigit() and value.count(".") < 2:
            return float(value)
        return value

    def format_dict(self,data,level=0):
        if not isinstance(data, dict):
            return str(data)
        result = "{\n"
        for key, value in data.items():
            result += " " * (level + 1) * 4
            result += f'"{key}": '
            if isinstance(value, dict):
                result += self.format_dict(value, level + 1)
            else:
                result += str(value)
            result += ",\n"
        result = result.rstrip(",\n") + "\n"
        result += " " * level * 4 + "}"
        return result

    def load_props(self):
        args = self.parse_dict_string(props().stm_all)
        line_names = args['line_names']
        mismatch = len(line_names) - len(lines())
        if mismatch:
            self.adjust_lines_count(mismatch)
        for attr in args['attributes']:
            if isinstance(getattr(props(),attr),bool):
                setattr(props(),attr,args[attr])
            else:
                setattr(props(),attr,args[attr])
        self.refresh_inputs()
        for i,line in enumerate(lines()):
            line.name = line_names[i]
            try :
                line['line_on'],line['file_name'],line['manual'],line['split_rgb'],line['auto_mode'] = args[line.name]
                line['input_sockets'] = int(args["input_sockets"][i])
            except (TypeError,NameError,KeyError,ValueError,AttributeError,OverflowError) as e:
                print(e)
        for i,ch in enumerate(args['channels']):
            for j,k in enumerate(ch.split('-')):
                try:
                    lines()[i]['channels']['socket'][j]['input_sockets'] = int(k)
                    lines()[i]['channels']['socket'][j]['line_name'] = lines()[i].name
                except (TypeError,NameError,KeyError,ValueError,AttributeError,OverflowError) as e:
                    print(e)
                    continue

    def fill_settings(self):
        args = {}
        args["internals"] = ["type","rna_type","dir_content","poll_props","preset_enum","in_sockets","img_files","content","bl_rna","name","stm_all"]
        args["attributes"] = [attr for attr in props().bl_rna.properties.keys() if attr not in args["internals"] and attr[:2] != "__"]
        args["line_names"] = []
        args["input_sockets"] = [line["input_sockets"] for line in lines()]
        args["channels"] = [("-").join([str(line.channels.socket["RGB"[i]]["input_sockets"]) for i in range(3)]) for line in lines()]
        for attr in args["attributes"]:
            if isinstance(getattr(props(),attr),bool):
                args[attr] = f"{getattr(props(),attr)}"
            else:
                args[attr] = getattr(props(),attr)
        for line in lines():
            args["line_names"].append(line.name)
            args[line.name] = [f"{line.line_on}",line.file_name,f"{line.manual}", f"{line.split_rgb}",f"{line.auto_mode}"]
        try:
            return self.format_dict(args)

        except (TypeError,NameError,KeyError,ValueError,AttributeError,OverflowError) as e:
            print("An error occurred with the Preset File ",e)
        return '{"0":""}'

    def adjust_lines_count(self,difference):
        method = self.del_panel_line if difference < 0 else self.add_panel_lines
        for _i in range(abs(difference)):
            method()

    def del_panel_line(self):
        if 0 <= texture_index() < len(lines()):
            lines().remove(texture_index())
            texture_importer().texture_index = max(0, texture_index() - 1)

    def add_panel_lines(self):
        texture = lines().add()
        texture.name = self.get_available_name()
        texture_importer().texture_index = len(lines()) - 1
        self.make_clean_channels(texture)

    def get_available_name(self):
        new_index = 0
        new_name = "Custom map 1"
        while new_name in [item.name for item in lines()]:
            new_index += 1
            new_name = f"Custom map {new_index}"
        return new_name

    def refresh_shader_links(self):
        shader_links().clear()
        mat_tmp = bpy.data.materials.new(name="tmp_mat")
        mat_tmp.use_nodes = True
        for shader_enum in self.get_shaders_list_eve():
            node_type = str(shader_enum[0])
            if node_type is not None and node_type != '0' :
                if node_type in bpy.data.node_groups.keys():
                    new_node = mat_tmp.node_tree.nodes.new(type='ShaderNodeGroup')
                    new_node.node_tree = bpy.data.node_groups[str(shader_enum[1])]
                else:
                    new_node = mat_tmp.node_tree.nodes.new(type=node_type)
                new_shader_link = shader_links().add()
                new_shader_link.name = str(shader_enum[1])
                new_shader_link.shadertype = node_type
                for sk in [i for i in new_node.inputs.keys() if not i == 'Weight']:
                    si = new_shader_link.in_sockets.add()
                    #print(sk)
                    si.name = sk

        for shader_enum in self.get_shaders_list_cycles():
            node_type = str(shader_enum[0])
            if node_type is not None and node_type != '0' :
                if node_type in bpy.data.node_groups.keys():
                    new_node = mat_tmp.node_tree.nodes.new(type='ShaderNodeGroup')
                    new_node.node_tree = bpy.data.node_groups[str(shader_enum[1])]
                else:
                    new_node = mat_tmp.node_tree.nodes.new(type=node_type)
                new_shader_link = shader_links().add()
                new_shader_link.name = str(shader_enum[1])
                new_shader_link.shadertype = node_type
                for sk in [i for i in new_node.inputs.keys() if not i == 'Weight']:
                    si = new_shader_link.in_sockets.add()
                    si.name = sk

        mat_tmp.node_tree.nodes.clear()
        bpy.data.materials.remove(mat_tmp)

    def get_hard_sockets(self):
        return [ "Base Color", "Metallic","Roughness","IOR", "Alpha",
                "Normal", "Diffuse Roughness", "Subsurface Weight", "Subsurface Radius",
                "Subsurface Scale", "Subsurface IOR","Subsurface Anisotropy","Specular IOR Level",
                "Specular Tint","Anisotropic", "Anisotropic Rotation", "Tangent",
                "Transmission Weight", "Coat Weight","Coat Roughness","Coat IOR", "Coat Tint",
                "Coat Normal","Sheen Weight", "Sheen Roughness","Sheen Tint", "Emission Color",
                "Emission Strength", "Thin Film Thickness", "Thin Film IOR" ]

    def refresh_inputs(self):
        self.clean_input_sockets()
        if props().include_ngroups:
            node_links().clear()
            self.set_nodes_groups()
        self.refresh_shader_links()

    def set_enum_sockets_items(self):
        if not self.mat :
            try:
                self.mat = bpy.context.object.active_material
            except (TypeError,NameError,KeyError,ValueError,AttributeError,OverflowError):
                print("No material")
                return
        rawdata = []
        if not props().replace_shader:
            rawdata = self.get_shader_inputs()
        else:
            selectedshader = props().shaders_list
            shaders = [sh.in_sockets for sh in shader_links() if sh.shadertype in selectedshader]
            if len(shaders) > 0:
                rawdata = [sk.name for sk in shaders[0]]
            customs = [sh.in_sockets for sh in node_links() if sh.nodetype in selectedshader]
            if props().include_ngroups and len(customs) > 0:
                rawdata = [sk.name for sk in customs[0]]
            if not len(rawdata) > 0 :
                rawdata = self.get_hard_sockets()

        if not rawdata:
            self.clean_input_sockets()
            rawdata = [sh.name for sh in props().in_sockets]
        else:
            rawdata.append('Ambient Occlusion')
        props().in_sockets.clear()
        for sk in rawdata:
            si = props().in_sockets.add()
            si.name = sk

    def get_sockets_enum_items(self):
        if len(props().in_sockets) == 0:
            self.set_enum_sockets_items()
        return self.format_enum([sh.name for sh in props().in_sockets])

    def get_linked_node(self, _socket):
        if _socket and _socket.is_linked:
            return _socket.links[0].from_node
        return None

    def node_finder(self, node):
        if not node:
            return None
        if node.type in {"MIX_SHADER", "ADD_SHADER"}:
            return self.node_finder(self.get_linked_node(node.inputs[1])) or \
                   self.node_finder(self.get_linked_node(node.inputs[2]))
        if node.type in "SEPARATE_COLOR":
            return None
        if node.type in "GROUP" and not props().include_ngroups:
            return None
        return node

    def get_shader_node(self):
        shader_node = None
        output_node = self.get_output_node()
        if output_node :
            shader_node = self.node_finder(self.get_linked_node(output_node.inputs["Surface"]))
        return shader_node

    def get_output_node(self):
        if not self.nodes:
            return None
        out_nodes = [n for n in self.nodes if n.type in "OUTPUT_MATERIAL"]
        for node in out_nodes:
            if node.is_active_output:
                return node
        return None

    def check_special_keywords(self,term):
        if props().separators_list in term:
            return ""
        #no spaces
        matcher = { "Color":["color","col","colore","colour","couleur", "basecolor",
                             "emit", "emission", "albedo"],
                    "Ambient Occlusion":["ambientocclusion","ambientocclusion","ambient",
                                            "occlusion","ao","ambocc","ambient_occlusion"],
                    "Displacement":["relief","displacement","displace","displace_map"],
                    "Disp Vect":["dispvect","dispvector","disp_vector","vector_disp",
                                    "vectordisplacement","displacementvector",
                                    "displacement_vector", "vector_displacement"],
                    "Normal":["normal","normalmap","normalmap", "norm", "tangent"],
                    "bump":["bump","bumpmap","bump map", "height","heightmap","weight","weight map"]
                    }
        for k,v in matcher.items():
            if self.find_in_sockets(term.strip(),v):
                return k
        return ""

    def mat_name_cleaner(self):
        return self.mat.name.split(".0")[0] if props().dup_mat_compatible else self.mat.name

    def synch_names(self):
        liners = []
        props().img_files.clear()
        exts = set(bpy.path.extensions_image)
        dir_content = [x.name for x in Path(props().usr_dir).glob('*.*') if x.suffix.lower() in exts]
        if len(dir_content) :
            for img in dir_content:
                i = props().img_files.add()
                i.name = img
            if self.mat_name_cleaner() in [i.name for i in props().img_files]:
                mat_related = [Path(_img).stem.lower() for _img in dir_content if self.mat_name_cleaner() in _img]
                prefix = commonprefix(mat_related)
                suffix = commonprefix([s[::-1] for s in mat_related])
                liners = sorted(list({i.replace(prefix,"").replace(suffix[::-1],"") for i in mat_related}))
        if len(liners) > 1 :
            self.adjust_lines_count(len(liners)-len(lines()))
            for i,l in enumerate(lines()) :
                l.name = liners[i]

    def find_in_sockets(self,term,target_list=None):
        if term in "":
            return None
        if not target_list:
            target_list = self.sicks()
        for sock in target_list:
            match = term.replace(" ", "").lower() in sock.replace(" ", "").lower()
            if match:
                return sock
        return None

    def detect_multi_socket(self,line):
        splitted = line.name.split(props().separators_list)
        if not len(splitted) > 1 :
            line['split_rgb'] = False
            return False
        line['split_rgb'] = True
        if len(splitted) != 3 :
            for i in range(3-len(splitted)):
                splitted.append("no_socket")
        for i,_sock in enumerate(splitted):
            if i > 2:
                return False
            sock = self.find_in_sockets(_sock)
            if not sock:
                sock = self.check_special_keywords(_sock)
                if not sock:
                    sock = self.sicks()[0]
                if sock in "bump" :
                    sock = 'Normal'
            if (sock in self.sicks() and line.auto_mode) or (not line.auto_mode and sock in 'no_socket'):
                line.channels.socket[i]['input_sockets'] = self.sicks().index(sock)
        return True


    def default_sockets(self,line):
        if not line.auto_mode :
            return
        if self.detect_multi_socket(line):
            return
        sock = self.find_in_sockets(line.name)
        if not sock:
            sock = self.check_special_keywords(line.name)
            if not sock:
                sock = self.sicks()[0]
            if "bump" in sock:
                sock = 'Normal'
        if sock in self.sicks():
            line['input_sockets'] = self.sicks().index(sock)

    def guess_sockets(self):
        for line in p_lines():
            self.default_sockets(line)

    def clean_input_sockets(self):
        #required to avoid warning errors
        for line in lines():
            line['input_sockets'] = 0
            for ch in line.channels.socket:
                ch['input_sockets'] = 0

    def get_shader_inputs(self):
        shd = self.get_shader_node()
        if shd and shd.inputs:
            return shd.inputs.keys()
        return None

    def read_preset(self):
        if not props().preset_enum in '0':
            try:
                with open(f"{props().preset_enum}", "r", encoding="utf-8") as w:
                    props().stm_all = w.read().replace("'",'"')
                    self.load_props()
                    return f"Applied preset: {Path(props().preset_enum).stem}"
            except (TypeError,NameError,KeyError,ValueError,AttributeError,OverflowError) as e:
                print(e)
                return f"Error {e}"
        return "Error"

    def get_preset_list(self):
        presets = [('0','-Select Preset-', ''),]
        p_dir = Path(bpy.utils.extension_path_user(f'{__package__}',
                                    path="stm_presets", create=True))
        for file in sorted(p_dir.glob("*.py")):
            presets.append((f"{file}", f"{file.stem}", ""))
        return presets

    def format_enum(self,rawdata):
        default = ('no_socket', '-- Unmatched Socket --', '')
        if rawdata == []:
            return [default]
        dispitem = [('Disp Vector', 'Disp Vector', ''), ('Displacement', 'Displacement', '')]
        items = [(item, item, '') for item in rawdata]
        items.extend(dispitem)
        items.reverse()
        items.append(default)
        items.reverse()
        return items
