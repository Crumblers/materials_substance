import bpy
from pathlib import Path

from . nodeshandler import NodeHandler as nha

from bpy.types import (
    Operator, PropertyGroup, UIList, WindowManager,
    Scene, Menu,
)
from bpy.props import (
    StringProperty, IntProperty, BoolProperty,
    PointerProperty, CollectionProperty,
    FloatProperty, FloatVectorProperty,
    EnumProperty,
)

from . propertieshandler import PropertiesHandler as ph
                                    
from bpy.utils import (register_class, unregister_class)


def ShowMessageBox(message="", title="Message", icon='INFO'):
    def draw(self, context):
        self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)


class sub_poll():
    bl_options = {'INTERNAL', 'UNDO'}

    @classmethod
    def poll(cls, context):

        if context.object is not None:
            if context.object.active_material is not None:
                return True
        return False


class BSM_OT_make_nodes(sub_poll,Operator):
    bl_idname = "bsm.make_nodes"
    bl_label = "Only Setup Nodes"
    bl_description = "Setup empty Texture Nodes"

    fromimportbutton: bpy.props.BoolProperty(default=False)

    def execute(self, context):
        ndh = nha()
        scene = context.scene
        props = scene.bsmprops
        if len(scene.shader_links) == 0:
            bpy.ops.bsm.make_nodetree()
        og_selection = list(context.view_layer.objects.selected)
        activeobj = context.view_layer.objects.active
        selected = ndh.selector(context)
        already_done = []
        for obj in og_selection:
            obj.select_set(False)
        for obj in selected:
            obj.select_set(True)
            context.view_layer.objects.active = obj
            props.prefix = obj.name
            mat_params = {'ops':self, 'context':context, 'selection':obj, 'already_done':already_done, 'caller':"make_nodes"}
            already_done = ndh.process_materials(**mat_params)
           
            obj.select_set(False)

        for obj in og_selection:
            obj.select_set(True)
        context.view_layer.objects.active = activeobj

        if not self.fromimportbutton:
            ShowMessageBox("Check Shader nodes panel", "Nodes created", 'FAKE_USER_ON')

        return {'FINISHED'}


class BSM_OT_name_maker(sub_poll,Operator):
    bl_idname = "bsm.name_maker"
    bl_label = ""
    bl_description = "Assume a probable filename "

    line_num: bpy.props.IntProperty(default=0)

    @classmethod
    def poll(cls, context):
        # return (context.object is not None)
        return True

    def execute(self, context):
        k = self.line_num
        scene = context.scene
        panel_line = eval(f"scene.panel_line{k}")
        bsmprops = scene.bsmprops
        lefolder = bsmprops.usr_dir
        prefix = bsmprops.prefix
        fullext = panel_line.map_ext
        mapname = panel_line.map_label
        propper = ph()
        matname = propper.mat_name_cleaner(context)[1]
        
        args = {'prefix':prefix, 'map_name':mapname, 'ext':fullext, 'mat_name':matname}
        file_name = propper.find_file(context,**args)
        if file_name is not None :
            panel_line.file_name = panel_line.probable = file_name
               
        propper.update_file_is_real(context=panel_line)

        return {'FINISHED'}


class BSM_OT_name_checker(sub_poll,Operator):
    bl_idname = "bsm.name_checker"
    bl_label = ""
    bl_description = "Check if a file containing the Map Name keyword matches the Pattern"

    line_number: bpy.props.IntProperty(default=0)
    lorigin: bpy.props.StringProperty(default="Not Set")
    called: bpy.props.BoolProperty(default=True)

    def execute(self, context):
        
        scene = context.scene
        bsmprops = scene.bsmprops
        line_number = self.line_number
        propper = ph()
        panel_line = eval(f"scene.panel_line{line_number}")
        manual = panel_line.manual
        advanced_mode = bsmprops.advanced_mode
        args = {'prefix':bsmprops.prefix}
        sel = context.object
        mat = sel.active_material
        mat.use_nodes = True
        args['map_name'] = panel_line.map_label
        args['ext'] = panel_line.map_ext
        args['mat_name'] = propper.mat_name_cleaner(context)[1]

        file_name = propper.find_file(context,**args)
        if file_name is not None and propper.file_tester(panel_line):
            panel_line.file_name = panel_line.probable = file_name
              
        if not propper.file_tester(panel_line) and self.called :
            toreport = panel_line.probable + " not found "
            self.report({'INFO'}, toreport)
            __class__.bl_description = f"No Image containing the keyword {panel_line.map_label} found , verify the Prefix, the Map name and/or the Maps Folder"
            """
            if not prefix.isalnum():
                toreport = "Prefix is empty"
                self.report({'INFO'}, toreport)
            """
            __class__.bl_description = "Set a non-empty Prefix in the Preferences (of this Addon Tab)"
        # necessary in order to update description
        unregister_class(__class__)
        register_class(__class__)

        if propper.file_tester(panel_line):
            panel_line.file_is_real = True
            if self.called:
                toreport = panel_line.probable + " detected in Maps Folder"
                self.report({'INFO'}, toreport)

        return {'FINISHED'}

class BSM_OT_assign_nodes(sub_poll,Operator):
    bl_idname = "bsm.assign_nodes"
    bl_label = "Only Assign Images"
    bl_description = "import maps for all selected objects"

    fromimportbutton: bpy.props.BoolProperty(default=False)

    def execute(self, context):
        ndh = nha()
        scene = context.scene
        props = scene.bsmprops
        if len(scene.shader_links) == 0:
            bpy.ops.bsm.make_nodetree()
        og_selection = list(context.view_layer.objects.selected)
        activeobj = context.view_layer.objects.active
        selected = ndh.selector(context)
        already_done = []
        for obj in og_selection:
            obj.select_set(False)
        for obj in selected:
            obj.select_set(True)
            context.view_layer.objects.active = obj
            props.prefix = obj.name
            mat_params = {'ops':self, 'context':context, 'selection':obj, 'already_done':already_done, 'caller':"assign_nodes"}
            already_done = ndh.process_materials(**mat_params)
            print("mat preocessed - make_nodes")
            obj.select_set(False)

        for obj in og_selection:
            obj.select_set(True)
        context.view_layer.objects.active = activeobj
        if not self.fromimportbutton:
            pass
            # ShowMessageBox("All images loaded sucessfully", "Image Textures assigned", 'FAKE_USER_ON')
        return {'FINISHED'}


class BSM_OT_import_textures(sub_poll, Operator):
    bl_idname = "bsm.import_textures"
    bl_label = "Import Substance Maps"
    bl_description = "Import Texture Maps for active object"

    def execute(self, context):
        bpy.ops.bsm.make_nodes(fromimportbutton=True)
        bpy.ops.bsm.assign_nodes(fromimportbutton=True)
        return {'FINISHED'}


class BSM_OT_add_map_line(sub_poll, Operator):
    bl_idname = "bsm.add_map_line"
    bl_label = ""
    bl_description = "Add a new map line below"

    line_number: IntProperty(default=0)

    def execute(self, context):
        if len(context.scene.shader_links) == 0:
            bpy.ops.bsm.make_nodetree()
        context.scene.bsmprops.panel_rows += 1

        return {'FINISHED'}


class BSM_OT_del_map_line(sub_poll, Operator):
    bl_idname = "bsm.del_map_line"
    bl_label = ""
    bl_description = "Remove last Map from the list"

    marked: StringProperty(name="line n", default="BSM_PT_PaneLine1")

    def execute(self, context):
        if len(context.scene.shader_links) == 0:
            bpy.ops.bsm.make_nodetree()
        scene = context.scene
        context.scene.bsmprops.panel_rows -= 1
        panel_line = eval(f"scene.panel_line{scene.bsmprops.panel_rows}")
        panel_line.manual = False
        panel_line.line_on = False

        context.view_layer.update()
        return {'FINISHED'}


class BSM_presetbase:
    #    """Base preset class, only for subclassing
    #    subclasses must define
    #     - preset_values
    #     - preset_subdir """
    # bl_idname = "script.preset_base_add"
    # bl_label = "Add a Python Preset"

    # only because invoke_props_popup requires. Also do not add to search menu.
    bl_options = {'REGISTER', 'INTERNAL'}

    name: StringProperty(
        name="Name",
        description="Name of the preset, used to make the path name",
        maxlen=64,
        options={'SKIP_SAVE'},
    )
    remove_name: BoolProperty(
        default=False,
        options={'HIDDEN', 'SKIP_SAVE'},
    )
    remove_active: BoolProperty(
        default=False,
        options={'HIDDEN', 'SKIP_SAVE'},
    )

    @staticmethod
    def as_filename(name):  # could reuse for other presets

        # lazy init maketrans
        def maketrans_init():
            cls = BSM_presetbase
            attr = "_as_filename_trans"

            trans = getattr(cls, attr, None)
            if trans is None:
                trans = str.maketrans({char: "_" for char in " !@#$%^&*(){}:\";'[]<>,.\\/?"})
                setattr(cls, attr, trans)
            return trans

        name = name.lower().strip()
        name = bpy.path.display_name_to_filepath(name)
        trans = maketrans_init()
        return name.translate(trans)

    def execute(self, context):
        import os
        from bpy.utils import is_path_builtin
        bpy.ops.bsm.save_all()
        if hasattr(self, "pre_cb"):
            self.pre_cb(context)

        preset_menu_class = getattr(bpy.types, self.preset_menu)

        is_xml = getattr(preset_menu_class, "preset_type", None) == 'XML'

        if is_xml:
            ext = ".xml"
        else:
            ext = ".py"

        name = self.name.strip()
        if not (self.remove_name or self.remove_active):

            if not name:
                return {'FINISHED'}

            # Reset preset name
            wm = bpy.data.window_managers[0]
            if name == wm.preset_name:
                wm.preset_name = 'New Preset'
            filename = self.as_filename(name)
            pathlibbed = str(Path("presets").joinpath(self.preset_subdir))
            target_path = bpy.utils.user_resource('SCRIPTS',
                                                  path=pathlibbed,
                                                  create=True)
            if not target_path:
                self.report({'WARNING'}, "Failed to create presets path")
                return {'CANCELLED'}
            filepath = str(Path(target_path).joinpath(filename)) + ext

            if hasattr(self, "add"):
                self.add(context, filepath)
            else:
                if is_xml:
                    import rna_xml
                    rna_xml.xml_file_write(context,
                                           filepath,
                                           preset_menu_class.preset_xml_map)
                else:

                    def rna_recursive_attr_expand(value, rna_path_step, level):
                        if isinstance(value, bpy.types.PropertyGroup):
                            for sub_value_attr in value.bl_rna.properties.keys():
                                if sub_value_attr == "rna_type":
                                    continue
                                sub_value = getattr(value, sub_value_attr)
                                rna_recursive_attr_expand(sub_value, "%s.%s" % (rna_path_step, sub_value_attr), level)
                        elif type(value).__name__ == "bpy_prop_collection_idprop":  # could use nicer method
                            file_preset.write("%s.clear()\n" % rna_path_step)
                            for sub_value in value:
                                file_preset.write("item_sub_%d = %s.add()\n" % (level, rna_path_step))
                                rna_recursive_attr_expand(sub_value, "item_sub_%d" % level, level + 1)
                        else:
                            # convert thin wrapped sequences
                            # to simple lists to repr()
                            try:
                                value = value[:]
                            except:
                                pass

                            file_preset.write("%s = %r\n" % (rna_path_step, value))

                    file_preset = open(filepath, 'w', encoding="utf-8")
                    file_preset.write("import bpy\n")

                    if hasattr(self, "preset_defines"):
                        for rna_path in self.preset_defines:
                            exec(rna_path)
                            file_preset.write("%s\n" % rna_path)
                        file_preset.write("\n")

                    for rna_path in self.preset_values:
                        value = eval(rna_path)
                        rna_recursive_attr_expand(value, rna_path, 1)

                    file_preset.close()

            preset_menu_class.bl_label = bpy.path.display_name(filename)

        else:
            if self.remove_active:
                name = preset_menu_class.bl_label

            # fairly sloppy but convenient.
            filepath = bpy.utils.preset_find(name,
                                             self.preset_subdir,
                                             ext=ext)

            if not filepath:
                filepath = bpy.utils.preset_find(name,
                                                 self.preset_subdir,
                                                 display_name=True,
                                                 ext=ext)

            if not filepath:
                return {'CANCELLED'}

            if is_path_builtin(filepath):
                self.report({'WARNING'}, "You can't remove the default presets")
                return {'CANCELLED'}

            try:
                if hasattr(self, "remove"):
                    self.remove(context, filepath)
                else:
                    Path(filepath).unlink()
            except Exception as e:
                self.report({'ERROR'}, "Unable to remove preset: %r" % e)
                import traceback
                traceback.print_exc()
                return {'CANCELLED'}

            preset_menu_class.bl_label = "Presets"

        if hasattr(self, "post_cb"):
            self.post_cb(context)

        return {'FINISHED'}


class BSM_OT_add_preset(BSM_presetbase, Operator):
    bl_idname = 'bsm.add_preset'
    bl_label = 'Add A preset'
    preset_menu = 'BSM_MT_presetsmenu'

    # Common variable used for all preset values
    preset_defines = ['scene = bpy.context.scene',
                      'bsmprops = scene.bsmprops',
                      ]
    # Properties to store in the preset
    preset_values = [
                     'bsmprops.advanced_mode',
                     'bsmprops.bsm_all',
                     'bsmprops.usr_dir', 'bsmprops.separator',
                     'bsmprops.panel_rows',
                     'bsmprops.apply_to_all', 'bsmprops.clear_nodes',
                     'bsmprops.tweak_levels',
                     'bsmprops.only_active_obj', 'bsmprops.skip_normals',
                     'bsmprops.only_active_mat',
                     'bsmprops.fix_name',
                     'bsmprops.prefix',
                     'bsmprops.patterns'

                     ]
    # Directory to store the presets
    preset_subdir = 'bsm_presets'


class BSM_OT_make_nodetree(sub_poll, Operator):
    bl_idname = "bsm.make_nodetree"
    bl_label = "tree creator"
    bl_description = "used to initialize some dynamic props"

    def execute(self, context):
        context.scene.shader_links.clear()

        fetchedOutputs = []  #
        fetchedInputs = []  #
        fetchedShaders = []  #
        fetchedNodes = []  #
        fetchedObjects = []  #
        scene = context.scene
        scenename = str(scene.name_full)
        bsmprops = scene.bsmprops
        propper = ph()
        shaders_list = propper.get_shaders_list(context)
        for obj in context.view_layer.objects.selected:
            fetchedObjects.append(obj)
        bpy.ops.object.select_all(action='DESELECT')
        activeobj = context.view_layer.objects.active

        view_layer = context.view_layer
        mesh = bpy.data.meshes.new("mesh")
        lecubetmp = bpy.data.objects.new(mesh.name, mesh)
        collecto = bpy.data.collections.new("latmpcollect")
        collecto.objects.link(lecubetmp)
        vieww = view_layer.active_layer_collection
        vieww.collection.children.link(collecto)
        lecubetmp.select_set(True)
        view_layer.objects.active = lecubetmp
        lematcree = bpy.data.materials.new(name="MaterialName")
        lecubetmp.data.materials.append(lematcree)
        mattemp = lecubetmp.material_slots[-1].material
        mattemp.use_nodes = True
        shaders_list_raw = []

        leshaderoutputnodes = []
        allshaderstnodes = []
        # only create nodes for the initial shaders_list populated by ph.get_shaders_list
        lenghtlist = 11  
        for lesnods in range(lenghtlist):
            laligne = shaders_list[lesnods]
            lID = int(lesnods)
            letyp = str(laligne[0])
            lename = str(laligne[1])
            fetchedShaders.append((lename, letyp), )
            shaders_list_raw.append(laligne)
            lanewnode = mattemp.node_tree.nodes.new(type=letyp)
            lanewnode.name = lename
            lanewnode.label = lanewnode.name
            leszinputs = mattemp.node_tree.nodes[lanewnode.name].inputs
            leszoutputs = mattemp.node_tree.nodes[lanewnode.name].outputs
            lalistsizeI = len(leszinputs)
            lalistsizeO = len(leszoutputs)
            fetchedInputs = []
            fetchedOutputs = []
            for inp in range(0, lalistsizeI):
                leyley = leszinputs[inp].name
                leinpname = (leyley, leyley, "",)
                leshaderoutputnodes.append(leinpname)
                fetchedInputs.append(leyley)
            for inp in range(0, lalistsizeO):
                loyloy = leszoutputs[inp].name
                leoutname = (loyloy, loyloy, "",)
                fetchedOutputs.append(loyloy)

            newentry = context.scene.shader_links.add()
            newentry.name = lename
            newentry.shadertype = letyp
            newentry.input_sockets = "@-¯\(°_o)/¯-@".join(str(x) for x in fetchedInputs)
            newentry.outputsockets = "@-¯\(°_o)/¯-@".join(str(x) for x in fetchedOutputs)

            allshaderstnodes.append(leshaderoutputnodes)

        bpy.data.materials.remove(lematcree)
        bpy.data.objects.remove(lecubetmp)
        bpy.data.collections.remove(collecto)

        for obj in fetchedObjects:
            bpy.data.scenes[scenename].objects[obj.name].select_set(True)
        context.view_layer.objects.active = activeobj
        return {'FINISHED'}


class BSM_OT_save_all(sub_poll, Operator):
    bl_idname = 'bsm.save_all'
    bl_label = 'save all values'
    bl_description = 'Save all relevant vars'

    def execute(self, context):
        scene = context.scene
        bsmprops = scene.bsmprops
        arey = []
        for i in range(10):
            map_label = eval(f"scene.panel_line{i}").map_label
            lechan = eval(f"scene.panel_line{i}").input_sockets
            enabled = str(eval(f"scene.panel_line{i}").line_on)
            exts = eval(f"scene.panel_line{i}").map_ext
            lesfilenames = eval(f"scene.panel_line{i}").file_name
            probables = eval(f"scene.panel_line{i}").probable
            manuals = str(eval(f"scene.panel_line{i}").manual)

            lineitems = [str(eval(f"scene.panel_line{i}").name), map_label, lechan, enabled, exts, lesfilenames, probables, manuals ]
            lineraw = "@\_/@".join(str(lx) for lx in lineitems)
            arey.append(lineraw)

        bsmprops.bsm_all = "@-¯\(°_o)/¯-@".join(str(lx) for lx in arey)

        return {'FINISHED'}


class BSM_OT_load_all(sub_poll, Operator):
    bl_idname = 'bsm.load_all'
    bl_label = 'save all values'
    bl_description = 'load preset '

    def execute(self, context):

        scene = context.scene
        bsmprops = scene.bsmprops
        allraw = bsmprops.bsm_all.split("@-¯\(°_o)/¯-@")
        allin = []
        for allitems in allraw:
            zob = allitems.split("@\_/@")
            allin.append(zob)
        for i in range(10):
            PaneLine = eval(f"scene.panel_line{i}")
            PaneLine.map_label = allin[i][1]
            try :
                PaneLine.input_sockets = allin[i][2]
            except TypeError :
                PaneLine.input_sockets = '0'
            PaneLine.line_on = bool(int(eval(allin[i][3])))
            PaneLine.map_ext = allin[i][4]
            PaneLine.file_name = allin[i][5]
            PaneLine.probable = allin[i][6]
            PaneLine.manual = bool(int(eval(allin[i][7])))

        return {'FINISHED'}


class BSM_MT_presetsmenu(Menu):
    # bl_idname = 'my.presetmenu'
    bl_label = 'Presets Menu'
    preset_subdir = 'bsm_presets'
    preset_operator = 'bsm.execute_preset'
    draw = Menu.draw_preset


class BSM_OT_execute_preset(Operator):
    # """Execute a preset"""
    bl_idname = "bsm.execute_preset"
    bl_label = "Execute a Python Preset"

    filepath: StringProperty(
        subtype='FILE_PATH',
        options={'SKIP_SAVE'},
    )
    menu_idname: StringProperty(
        name="Menu ID Name",
        description="ID name of the menu this was called from",
        options={'SKIP_SAVE'},
    )

    def execute(self, context):
        filepath = self.filepath

        # change the menu title to the most recently chosen option
        preset_class = BSM_MT_presetsmenu  # getattr(bpy.types, self.menu_idname)
        preset_class.bl_label = bpy.path.display_name(Path(filepath).stem)
        ext = str(Path(filepath).suffix).lower()
        if ext not in {".py", ".xml"}:
            self.report({'ERROR'}, "unknown filetype: %r" % ext)
            return {'CANCELLED'}

        if hasattr(preset_class, "reset_cb"):
            preset_class.reset_cb(context)

        if ext == ".py":
            try:
                bpy.utils.execfile(filepath)
            except Exception as ex:
                self.report({'ERROR'}, "Failed to execute the preset: " + repr(ex))

        elif ext == ".xml":
            import rna_xml
            rna_xml.xml_file_run(context,
                                 filepath,
                                 preset_class.preset_xml_map)

        if hasattr(preset_class, "post_cb"):
            preset_class.post_cb(context)
        bpy.ops.bsm.load_all()
        return {'FINISHED'}
