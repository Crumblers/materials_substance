Substance Textures Importer
------------------------------------


.. figure:: http://kos-design.com/images/wikipics/addon_pic.jpg
   :scale: 100 %
   :align: center


Description:
------------

Blender extension designed to import images textures made with Substance Painter or other similar surfacing tools into Blender 3D easily.
The script looks at all the images in the chosen directory and attempts to guess the corresponding shader input to plug them into.
According to the target materials names, the algorithm will look for a matching image name pattern to fill the selected map names enabled in the UI panel.
The extension panel is available via the File menu > Import > Substance textures and in the Shader Nodes Editor SideBar > STM Tab.
The texture maps names are editable and can include up to 3 multi-channel maps. The target shader input socket can be set from a drop-down list for better control.

.. figure:: http://kos-design.com/images/wikipics/import_panel.jpg
   :align: left

The texture files must have been exported using a pattern containing the material name and a map type (BaseColor, Metallic, Roughness, Normal etc.).

You can use the Split RGB option to connect the Red, Green and Blue channels individually if your textures include separate maps mixed in.
When 'Detect target socket' is enabled the script will parse the line name and fill in the input socket if a match is found and Line names like 'alpha_ior_metal' will be recognized as split-rgb.

.. figure:: http://kos-design.com/images/wikipics/panel_multi_sockets.gif
   :align: left

Note: 'Detect target socket' should be disabled to be able to manually select a target socket for a texture map or the drop-down list will overwritten and appear grayed out.

Various options are available for fine tuning such as adding RGB curves and color ramps, using custom shader nodes, inverting the Green channel of the normal map or even ignoring the .00x prefix in duplicated material names.
Manual assignment is also possible for a given material regardless of the texture file name pattern.

Installation:
-------------

`TLDR Add-on Installation Video Tutorial <https://youtu.be/lumrnhikSOg>`__

https://youtu.be/lumrnhikSOg

`Download the latest git release of Substance Textures Importer from here <https://github.com/Kos-Design/substance_textures_importer/releases/download/0.6.0/Substance_Textures_Importer.zip>`__
and install it in Blender via Edit > Preferences > Add-ons > Install an Addon.

Once installed, enable like the other add-ons by ticking the checkbox in front of “Substance Textures Importer”.
You can adjust the defaults in the extension preferences panel.
The user interface panel is available from the Material section in the Properties window.


How-to:
-------

`Basic Features & How-to Video tutorial <https://youtu.be/45rky8J_0us>`__

https://youtu.be/45rky8J_0us

The panel labeled "Substance Textures Importer" is displayed under the Shader Settings in the Material Tab.

First set the desired target in the 'Target' dropdown list at the top and choose the directory containing the textures files to be imported using the folder selection window or the field under the "Maps Folder" section of the Shader Node Editor Panel.
After setting the folder, modify the texture maps names ('Color','Roughness'...) to fit your naming pattern,
or use the '2-gears' button at the right of the list to attempt to auto-fill the line names if the current material name is detected in the folder content.
The button with the chip icon below restores the line names to a default set of values.

.. figure:: http://kos-design.com/images/wikipics/panel_lines.gif
   :align: left

You can enable/disable the textures maps type you wish to import by ticking the 'Active' checkmark under the maps list in the addon panel (you can also add/delete more lines and edit the texture map name if needed)

Then you can use the "Import Substance Maps" button to batch import the images into their associated shaders sockets.

.. figure:: http://kos-design.com/images/wikipics/import_maps.jpg
   :align: left

Or use the "Only Setup Nodes" button below to only create empty image nodes,

.. figure:: http://kos-design.com/images/wikipics/only_setup.jpg
   :align: left

and then use the "Only Assign Images" button next to it to fill these images nodes with the matching textures files.

.. figure:: http://kos-design.com/images/wikipics/only_assign.jpg
   :align: left

By default the script will import the images for all selected objects at once, there are also some options to import them for all visible objects, only the active object or only the active material of each selected object.


Options:
--------

.. figure:: http://kos-design.com/images/wikipics/preferences.jpg
   :align: left

---------------
Replace Shader:
---------------
When this option is enabled the shader node of the material will be replaced by the one displayed in the dropdown selector next to it.

--------------------------
Skip normal map detection:
--------------------------
By default a normal map node or bump map node is added when a normal map or height map is detected. Enable this option if you are using a custom shader that already include such conversion node in order to plug the image directly in the selected input socket.

--------------------------
OpenGL Normals:
--------------------------
Enabled by default, disable it to invert the green channel of a normal map to use directx-style format instead of the usual one.

----------------------
Enable Custom Shaders:
----------------------
Use this option to add your own NodeGroups to the Shaders list used by the "Replace Shaders" option.
Your custom shaders needs to have at least one input socket and a shader output socket in order to be added to the list.

--------------------------
Clear nodes from material:
--------------------------
Removes all existing nodes nodes from the target materials before processing them.

--------------------------
Attach Curves and Ramps:
--------------------------
Inserts a RGBCurve or a ColorRamp node between the images and their assigned sockets to enable fine tuning.

---------------------
Only active material:
---------------------
Process only the active material from the material slots for each target object.

----------------------------------
Duplicated material compatibility:
----------------------------------
Enable this option to ignore the .00x prefix from the target materials names.

--------------------------
Map names from files:
--------------------------
When enabled the script will try to fill the line names when the texture folder gets set. The current material name should be included in the images names from that folder for better chances of success.

------------
Manual Mode:
------------
Use this to be able to manually select a texture file instead of relying on the pattern detection algorithm of the addon.
When enabled, a new line labelled 'Overwrite file name' will appear under the maps table.
It can be activated for the required line and a file selection field will appear below that you can use to set the path of a texture file to import.
Note: When "Manual" and "Overwrite file name" are enabled in one of the Panel lines,
the addon will skip the name pattern detection and will use the path you select instead.


Presets:
--------
The icon in the top-right corner allows you to store and loads the parameters used in the UI panel.

.. figure:: http://kos-design.com/images/wikipics/preset.png
   :align: left

License
-------

This add-on is released under the `GNU/GPL v3.0 license <https://github.com/Kos-Design/substance_textures_importer/blob/master/LICENSE>`__

