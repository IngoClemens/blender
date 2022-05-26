# <pep8 compliant>

import bpy

from . import node


class RBFObjectOutputNode(node.RBFNode):
    """Driver object source.
    """
    bl_idname = "RBFObjectOutputNode"
    bl_label = "Object"
    bl_icon = 'OBJECT_DATA'

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    sceneObject : bpy.props.PointerProperty(type=bpy.types.Object)
    bone : bpy.props.StringProperty()

    def init(self, context):
        """Initialize the node and add the sockets.

        :param context: The current context.
        :type context: bpy.context
        """
        self.addOutput("RBFPropertySocket", "Properties", link_limit=0)
        self.addInput("RBFObjectSocket", "Object")

    def draw(self, context, layout):
        """Draw the content of the node.

        :param context: The current context.
        :type context: bpy.context
        :param layout: The current layout.
        :type layout: bpy.types.UILayout
        """
        layout.prop_search(self, property="sceneObject", search_data=context.scene, search_property="objects", text="")
        if self.sceneObject and self.sceneObject.type == 'ARMATURE':
            armature = self.sceneObject.data
            if armature:
                layout.prop_search(self, property="bone", search_data=armature, search_property="bones", text="")

    # ------------------------------------------------------------------
    # Getter
    # ------------------------------------------------------------------

    def getObject(self):
        """Return the selected object of the node.

        :return: The currently selected object.
        :rtype: bpy.types.Object
        """
        if self.sceneObject:
            if self.sceneObject.type == 'ARMATURE':
                if self.bone:
                    return self.sceneObject.pose.bones[self.bone]
            return self.sceneObject
