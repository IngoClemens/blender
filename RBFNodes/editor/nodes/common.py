# <pep8 compliant>

import bpy
from mathutils import Matrix, Quaternion

from ... core import plugs, properties, shapeKeys
from ... import language, preferences, var


# Get the current language.
strings = language.getLanguage()


ROTATION_MODE = [('EULER', strings.EULER_LABEL, "", "", 1),
                 ('QUATERNION', strings.QUATERNION_LABEL, "", "", 2),
                 ('AXIS_ANGLE', strings.AXIS_ANGLE_LABEL, "", "", 3)]


# ----------------------------------------------------------------------
# Object
# ----------------------------------------------------------------------

def drawObjectProperties(node, context, layout):
    """Add the common object properties to the node.

    :param node: The object node.
    :type node: bpy.types.Node
    :param context: The current context.
    :type context: bpy.context
    :param layout: The current layout.
    :type layout: bpy.types.UILayout
    """
    # Set the editable state of the layout depending on the active state
    # of the RBF node.
    layout.enabled = node.editable

    layout.prop_search(node,
                       property="sceneObject",
                       search_data=context.scene,
                       search_property="objects",
                       text="")
    if node.sceneObject and node.sceneObject.type == 'ARMATURE':
        armature = node.sceneObject.data
        if armature:
            layout.prop_search(node,
                               property="bone",
                               search_data=armature,
                               search_property="bones",
                               text="")


def getObjectFromNode(node):
    """Return the selected object of the node.

    :param node: The object node.
    :type node: bpy.types.Node

    :return: The currently selected object.
    :rtype: bpy.types.Object
    """
    if node.sceneObject:
        if node.sceneObject.type == 'ARMATURE':
            if node.bone:
                return node.sceneObject.pose.bones[node.bone]
        return node.sceneObject


# ----------------------------------------------------------------------
# Location
# ----------------------------------------------------------------------

def drawTransformProperties(node, layout):
    """Add the common location properties to the node.

    :param node: The location node.
    :type node: bpy.types.Node
    :param layout: The current layout.
    :type layout: bpy.types.UILayout
    """
    # Set the editable state of the layout depending on the active state
    # of the RBF node.
    layout.enabled = node.editable

    row = layout.row(align=True)
    row.prop(node, "x_axis")
    row.prop(node, "y_axis")
    row.prop(node, "z_axis")


def getLocationProperties(node, obj):
    """Return the selected location properties and their values for the
    given object.

    :param node: The location node.
    :type node: bpy.types.Node
    :param obj: The object to query.
    :type obj: bpy.types.Object

    :return: A list with the selected location properties and their
             values as a tuple.
    :rtype: list(tuple(str, float))
    """
    result = []
    location = obj.location

    if node.x_axis:
        result.append(("location[0]", location[0], None))
    if node.y_axis:
        result.append(("location[1]", location[1], None))
    if node.z_axis:
        result.append(("location[2]", location[2], None))

    return result


def getTransformOutputProperties(node):
    """Return the selected output properties.

    :param node: The node.
    :type node: bpy.types.Node

    :return: A list with the selected output properties and their
             index as a tuple.
    :rtype: list(bpy.types.Node, int)
    """
    result = []

    if node.x_axis:
        result.append((node, 0))
    if node.y_axis:
        result.append((node, 1))
    if node.z_axis:
        result.append((node, 2))

    return result


# ----------------------------------------------------------------------
# Rotation
# ----------------------------------------------------------------------

def drawRotationProperties(node, layout):
    """Add the common rotation properties to the node.

    :param node: The rotation node.
    :type node: bpy.types.Node
    :param layout: The current layout.
    :type layout: bpy.types.UILayout
    """
    # Set the editable state of the layout depending on the active state
    # of the RBF node.
    layout.enabled = node.editable

    layout.prop(node, "rotationMode")

    row = layout.row(align=True)
    if node.rotationMode == 'EULER':
        # row.prop(node, "w_axis")
        row.prop(node, "x_axis")
        row.prop(node, "y_axis")
        row.prop(node, "z_axis")


def getCombinedLocalRotations(obj):
    """
    Calculates and returns the Object or Pose Bone's locally applied transforms -
    be it directly by user, or animation, or indirectly by constraints.
    Ignores parent transforms.
    
    :param obj: A blender Object or Pose Bone.
    :type obj: bpy.types.Object or bpy.types.PoseBone
    
    :return: A quaternion with the rotation of the Object or Pose Bone,
    excluding parent transforms, including transforms applied by constraints,
    in the Object or Pose Bone's local coordinates.
    :rtype: mathutils.Quaternion
    
    """
    combined_local_rotations_quat = Quaternion()
    if isinstance(obj, bpy.types.PoseBone):
        pbone = obj
        pbone_parent_matrix_channel:Matrix = Matrix.Identity(4)
        if pbone.parent:
            pbone_parent_matrix_channel = pbone.parent.matrix_channel
        
        pbone_parent_matrix_channel_in_world_coordinates_relative_to_pbone = \
            pbone_parent_matrix_channel.to_quaternion() @ \
            pbone.bone.matrix_local.to_quaternion()
        
        # convert source bone coordinates to world coordinates (for the matrix_channel)
        pbone_matrix_channel_in_world_coordinates = \
            pbone.matrix_channel.to_quaternion() @ \
            pbone.bone.matrix_local.to_quaternion()
        
        # calculate the rotation, which, apparently contradictingly, will now result in a rotation
        # in *local* pose bone coordinates.
        combined_local_rotations_quat = \
            pbone_parent_matrix_channel_in_world_coordinates_relative_to_pbone.\
            rotation_difference(
                pbone_matrix_channel_in_world_coordinates
            )
        
    else:   # code for regular Objects, use other kinds of matrices
        combined_local_rotations_quat = \
            obj.matrix_parent_inverse.to_quaternion().inverted() @ \
            obj.matrix_local.to_quaternion()
        
    return combined_local_rotations_quat


def getRotationProperties(node, obj):
    """Return the selected rotation properties and their values for the
    given object.

    :param node: The rotation node.
    :type node: bpy.types.Node
    :param obj: The object to query.
    :type obj: bpy.types.Object

    :return: A list with the selected rotation properties and their
             values as a tuple.
             The third element is None by default but may contain a
             value for restoring a pose in case this value is different
             from the value used for calculating the RBF.
             This is true for quaternion or axis angle rotations.
             Since quaternions are converted to an exponential map the
             resulting value is different from the quaternion value used
             to set the pose. To avoid confusion the original quaternion
             value is stored to be able to recall the pose exactly how
             it has been set.
    :rtype: list(tuple(str, float, float or None))
    """
    result = []
    
    if node.rotationMode == 'EULER':
        if node.include_external_rotations:
            rotation_quat = getCombinedLocalRotations(obj)
            rotation = rotation_quat.to_euler(obj.rotation_euler.order)
        else:
            rotation = obj.rotation_euler
            
        mode = var.ROTATIONS[node.rotationMode]
        if node.x_axis:
            result.append(("{}[{}]".format(mode, 0), rotation[0], None))
        if node.y_axis:
            result.append(("{}[{}]".format(mode, 1), rotation[1], None))
        if node.z_axis:
            result.append(("{}[{}]".format(mode, 2), rotation[2], None))
    elif node.rotationMode == 'AXIS_ANGLE':
        if node.include_external_rotations:
            rotation_quat = getCombinedLocalRotations(obj)
            rotation = rotation_quat.to_axis_angle()
        else:
            rotation = obj.rotation_axis_angle
        mode = var.ROTATIONS[node.rotationMode]
        for i in range(4):
            result.append(("{}[{}]".format(mode, i), rotation[i], None))
    else:
        
        if node.include_external_rotations:
            rotation = getCombinedLocalRotations(obj)
        else:
            rotation = obj.rotation_quaternion
        
        mode = var.ROTATIONS['QUATERNION']
        values = list(rotation.to_exponential_map()) + [0.0]
        
        for i in range(len(values)):
            # For quaternions store every channel individually.
            # Since quaternions are converted to an exponential map,
            # store the original quaternion value for restoring poses.
            if len(values) > 1:
                data = ("{}[{}]".format(mode, i), values[i], rotation[i])
            # For a single twist axis store only the twist value but
            # also add the quaternion values for restoring poses.
            else:
                data = (mode, values[i], [v for v in rotation])
            result.append(data)

    return result


# ----------------------------------------------------------------------
# Scale
# ----------------------------------------------------------------------

def getScaleProperties(node, obj):
    """Return the selected scale properties and their values for the
    given object.

    :param node: The scale node.
    :type node: bpy.types.Node
    :param obj: The object to query.
    :type obj: bpy.types.Object

    :return: A list with the selected scale properties and their values
             as a tuple.
    :rtype: list(tuple(str, float))
    """
    result = []
    scale = obj.scale

    if node.x_axis:
        result.append(("scale[0]", scale[0], None))
    if node.y_axis:
        result.append(("scale[1]", scale[1], None))
    if node.z_axis:
        result.append(("scale[2]", scale[2], None))

    return result


# ----------------------------------------------------------------------
# Object Property
# ----------------------------------------------------------------------

def propertyLabelCallback(node):
    """Callback for updating the node label based on the property
    selection.

    :param node: The object property node.
    :type node: bpy.types.Node
    """
    if preferences.getPreferences().autoLabel:
        node.label = "{}: {}".format(strings.PROPERTY_LABEL, node.propertyEnum)


def listObjectProperties(node, source=True):
    """Return a list with all object property names of the connected
    object.

    :param node: The object property node.
    :type node: bpy.types.Node
    :param source: True, if the object can be found on the source node.
    :type source: bool

    :return: A list with all object property names.
    :rtype: list(str)
    """
    if source:
        plug = node.inputs[0]
    else:
        plug = node.outputs[0]

    obj = plugs.getObjectFromSocket(plug, source)
    if obj:
        return properties.objectProperties(obj)

    return []


def propertyItemsCallback(node, source=True):
    """Callback for the property drop down menu to collect the names of
    all object properties of the connected object.

    :param node: The object property node.
    :type node: bpy.types.Node
    :param source: True, if the object can be found on the source node.
    :type source: bool

    :return: A list with tuple items for the enum property.
    :rtype: list(tuple(str))
    """
    props = [('NONE', strings.SELECT_LABEL, "")]

    for prop in listObjectProperties(node, source):
        props.append((prop, prop, ""))

    return props


def drawPropertyProperties(node, layout):
    """Add the common object properties to the node.

    :param node: The property node.
    :type node: bpy.types.Node
    :param layout: The current layout.
    :type layout: bpy.types.UILayout
    """
    # Set the editable state of the layout depending on the active state
    # of the RBF node.
    layout.enabled = node.editable

    layout.prop(node, "propertyEnum")


def getObjectProperties(node, obj):
    """Return the selected object property and the value for the given
    object.

    :param node: The object property node.
    :type node: bpy.types.Node
    :param obj: The object to query.
    :type obj: bpy.types.Object

    :return: A list with the selected object property and the value as a
             tuple.
    :rtype: list(tuple(str, float))
    """
    if node.propertyEnum != 'NONE':
        return properties.expandObjectProperty(obj, node.propertyEnum)

    return []


# ----------------------------------------------------------------------
# Custom Property
# ----------------------------------------------------------------------

def customLabelCallback(node):
    """Callback for updating the node label based on the property
    selection.

    :param node: The custom property node.
    :type node: bpy.types.Node
    """
    if preferences.getPreferences().autoLabel:
        if node.mode == 'LIST':
            node.label = "{}: {}".format(strings.CUSTOM_LABEL, node.propertyEnum)
        else:
            node.label = "{}: {}".format(strings.CUSTOM_LABEL, node.propertyName)


def listCustomProperties(node, source=True):
    """Return a list with all custom property names of the connected
    object.

    :param node: The custom property node.
    :type node: bpy.types.Node
    :param source: True, if the object can be found on the source node.
    :type source: bool

    :return: A list with all custom property names.
    :rtype: list(str)
    """
    if source:
        plug = node.inputs[0]
    else:
        plug = node.outputs[0]

    obj = plugs.getObjectFromSocket(plug, source)
    if obj:
        return properties.customProperties(obj)

    return []


def customItemsCallback(node, source=True):
    """Callback for the property drop down menu to collect the names of
    all custom properties of the connected object.

    :param node: The custom property node.
    :type node: bpy.types.Node
    :param source: True, if the object can be found on the source node.
    :type source: bool

    :return: A list with tuple items for the enum property.
    :rtype: list(tuple(str))
    """
    props = [('NONE', strings.SELECT_LABEL, "")]

    for prop in listCustomProperties(node, source):
        props.append((prop, prop, ""))

    return props


def drawCustomProperties(node, layout):
    """Add the common custom properties to the node.

    :param node: The custom property node.
    :type node: bpy.types.Node
    :param layout: The current layout.
    :type layout: bpy.types.UILayout
    """
    # Set the editable state of the layout depending on the active state
    # of the RBF node.
    layout.enabled = node.editable

    layout.prop(node, "mode", expand=True)
    if node.mode == 'LIST':
        layout.prop(node, "propertyEnum")
    else:
        layout.prop(node, "propertyName")


def getCustomProperties(node, obj):
    """Return the selected custom property and the value for the given
    object.

    :param node: The custom property node.
    :type node: bpy.types.Node
    :param obj: The object to query.
    :type obj: bpy.types.Object

    :return: A list with the selected custom property and the value as a
             tuple.
    :rtype: list(tuple(str, float))
    """
    if node.mode == 'LIST':
        if node.propertyEnum != 'NONE':
            return properties.expandProperty(obj, node.propertyEnum)
    else:
        if len(node.propertyName):
            return properties.expandProperty(obj, node.propertyName)

    return []


# ----------------------------------------------------------------------
# Shape Key
# ----------------------------------------------------------------------

def shapeKeyLabelCallback(node):
    """Callback for updating the node label based on the shape key
    selection.

    :param node: The shape key node.
    :type node: bpy.types.Node
    """
    if preferences.getPreferences().autoLabel:
        if node.mode == 'LIST':
            node.label = "{}: {}".format(strings.SHAPE_KEY_LABEL, node.shapeNameEnum)
        else:
            node.label = "{}: {}".format(strings.SHAPE_KEY_LABEL, node.shapeName)


def getObjectShapeKeys(node, source=True):
    """Return a list with all shape key names of the connected
    object.

    :param node: The shape key node.
    :type node: bpy.types.Node
    :param source: True, if the object can be found on the source node.
    :type source: bool

    :return: A list with all shape key names.
    :rtype: list(str)
    """
    if source:
        plug = node.inputs[0]
    else:
        plug = node.outputs[0]

    obj = plugs.getObjectFromSocket(plug, source)
    if obj:
        return [k for k, v in shapeKeys.shapeKeyProperties(obj).items()]
    return []


def shapeKeyItemsCallback(node, source=True):
    """Callback for the property drop down menu to collect the names
    of all shape keys of the connected object.

    :param node: The shape key node.
    :type node: bpy.types.Node
    :param source: True, if the object can be found on the source node.
    :type source: bool

    :return: A list with tuple items for the enum property.
    :rtype: list(tuple(str))
    """
    props = [('NONE', strings.SELECT_LABEL, "")]

    for prop in getObjectShapeKeys(node, source):
        props.append((prop, prop, ""))

    return props


def drawShapeKeyProperties(node, layout):
    """Add the common custom properties to the node.

    :param node: The shape key node.
    :type node: bpy.types.Node
    :param layout: The current layout.
    :type layout: bpy.types.UILayout
    """
    # Set the editable state of the layout depending on the active state
    # of the RBF node.
    layout.enabled = node.editable

    layout.prop(node, "mode", expand=True)
    if node.mode == 'LIST':
        layout.prop(node, "shapeNameEnum")
    else:
        layout.prop(node, "shapeName")


def getShapeKeyProperties(node, obj):
    """Return the selected shape key property and the value for the
    given object.

    :param node: The shape key node.
    :type node: bpy.types.Node
    :param obj: The object to query.
    :type obj: bpy.types.Object

    :return: The selected shape key name and the value as a tuple.
    :rtype: tuple(str, float)
    """
    if node.mode == 'LIST':
        if node.shapeNameEnum != 'NONE':
            name = "shapeKey:{}".format(node.shapeNameEnum)
            value = obj.data.shape_keys.key_blocks[node.shapeNameEnum].value
            return [(name, value, None)]
    else:
        if len(node.name):
            name = "shapeKey:{}".format(node.shapeName)
            value = obj.data.shape_keys.key_blocks[node.shapeName].value
            return [(name, value, None)]

    return []


# ----------------------------------------------------------------------
# Modifiers
# ----------------------------------------------------------------------

def modifierLabelCallback(node):
    """Callback for updating the node label based on the modifier
    selection.

    :param node: The modifier node.
    :type node: bpy.types.Node
    """
    if preferences.getPreferences().autoLabel:
        modifier = ""
        prop = ""
        if node.modifierEnum != 'NONE':
            modifier = node.modifierEnum
        if node.propertyEnum != 'NONE':
            prop = node.propertyEnum
        node.label = "{}: {}".format(strings.MODIFIER_LABEL, ".".join((modifier, prop)))


def listModifiers(node, source=True):
    """Return a list with all modifiers of the connected object.

    :param node: The modifier node.
    :type node: bpy.types.Node
    :param source: True, if the object can be found on the source node.
    :type source: bool

    :return: A list with all modifier names.
    :rtype: list(str)
    """
    if source:
        plug = node.inputs[0]
    else:
        plug = node.outputs[0]

    obj = plugs.getObjectFromSocket(plug, source)
    if obj:
        return properties.objectModifiers(obj)

    return []


def modifierItemsCallback(node, source=True):
    """Callback for the modifier drop down menu to collect the names of
    all modifiers of the connected object.

    :param node: The modifier node.
    :type node: bpy.types.Node
    :param source: True, if the object can be found on the source node.
    :type source: bool

    :return: A list with tuple items for the enum property.
    :rtype: list(tuple(str))
    """
    mods = [('NONE', strings.SELECT_LABEL, "")]

    for mod in listModifiers(node, source):
        mods.append((mod, mod, ""))

    return mods


def listModifierProperties(node, source=True):
    """Return a list with all modifier property names of the connected
    object.

    :param node: The modifier node.
    :type node: bpy.types.Node
    :param source: True, if the object can be found on the source node.
    :type source: bool

    :return: A list with all modifier property names.
    :rtype: list(str)
    """
    if source:
        plug = node.inputs[0]
    else:
        plug = node.outputs[0]

    obj = plugs.getObjectFromSocket(plug, source)
    if obj and node.modifierEnum != 'NONE':
        return properties.modifierProperties(obj.modifiers[node.modifierEnum])

    return []


def modifierPropertiesCallback(node, source=True):
    """Callback for the property drop down menu to collect the names of
    all modifier properties of the connected object.

    :param node: The modifier node.
    :type node: bpy.types.Node
    :param source: True, if the object can be found on the source node.
    :type source: bool

    :return: A list with tuple items for the enum property.
    :rtype: list(tuple(str))
    """
    props = [('NONE', strings.SELECT_LABEL, "")]

    for prop in listModifierProperties(node, source):
        props.append((prop, prop, ""))

    return props


def drawModifierProperties(node, layout):
    """Add the modifier properties to the node.

    :param node: The modifier node.
    :type node: bpy.types.Node
    :param layout: The current layout.
    :type layout: bpy.types.UILayout
    """
    # Set the editable state of the layout depending on the active state
    # of the RBF node.
    layout.enabled = node.editable

    layout.prop(node, "modifierEnum")
    if node.modifierEnum != 'NONE':
        layout.prop(node, "propertyEnum")


def getModifierProperties(node, obj):
    """Return the selected modifer and property and the value for the
    given object.

    :param node: The modifier node.
    :type node: bpy.types.Node
    :param obj: The object to query.
    :type obj: bpy.types.Object

    :return: A list with the selected modifier property and the value as
             a tuple.
    :rtype: list(tuple(str, float))
    """
    if node.modifierEnum != 'NONE' and node.propertyEnum != 'NONE':
        value = eval('obj.modifiers["{}"].{}'.format(node.modifierEnum, node.propertyEnum))
        return [("modifier:{}:{}".format(node.modifierEnum, node.propertyEnum), value, None)]

    return []


# ----------------------------------------------------------------------
# Node
# ----------------------------------------------------------------------

def getTreeNodeProperties(node):
    """Return a list with all custom property names of the connected
    object.

    :param node: The node.
    :type node: bpy.types.Node

    :return: A list with all custom property names.
    :rtype: list(str)
    """
    if len(node.parentName) and len(node.nodeName):
        if node.nodeParent == 'MATERIAL':
            node = bpy.data.materials[node.parentName].node_tree.nodes[node.nodeName]
        else:
            node = bpy.data.node_groups[node.parentName].nodes[node.nodeName]

        nodeProps = properties.nodeProperties(node, fromInput=True)
        if not nodeProps:
            nodeProps = properties.nodeProperties(node, fromInput=False)
        return nodeProps

    return []


def nodeItemsCallback(node, context):
    """Callback for the property drop down menu to collect the names
    of all custom properties of the connected object.

    :param node: The node.
    :type node: bpy.types.Node
    :param context: The current context.
    :type context: bpy.context

    :return: A list with tuple items for the enum property.
    :rtype: list(tuple(str))
    """
    props = [('NONE', strings.SELECT_LABEL, "")]

    for prop, plug in getTreeNodeProperties(node):
        props.append((prop, prop, ""))
        node.propertyPlugs[prop] = plug

    return props


def setPropertyPlugName(node, context):
    """Set the property plug name depending on the current property
    selection.

    :param node: The node.
    :type node: bpy.types.Node
    :param context: The current context.
    :type context: bpy.context
    """
    if node.propertyEnum != 'NONE':
        node.plugName = node.propertyPlugs[node.propertyEnum]
    else:
        node.plugName = ""

    # Set the label
    if preferences.getPreferences().autoLabel:
        node.label = ": ".join([node.nodeName, node.propertyEnum])


def drawNodeProperties(node, layout):
    """Add the common custom properties to the node.

    :param node: The node.
    :type node: bpy.types.Node
    :param layout: The current layout.
    :type layout: bpy.types.UILayout
    """
    # Set the editable state of the layout depending on the active state
    # of the RBF node.
    layout.enabled = node.editable

    layout.prop(node, "nodeParent")
    layout.prop(node, "parentName")
    layout.prop(node, "nodeName")
    layout.prop(node, "plugName")
    layout.prop(node, "propertyEnum")


def getNodeProperties(node):
    """Return the selected node property and the value for the given
    object.

    :param node: The node.
    :type node: bpy.types.Node

    :return: A list with the selected node property and the value
             as a tuple.
    :rtype: list(tuple(str, float))
    """
    if len(node.parentName) and len(node.nodeName) and len(node.plugName):
        if node.nodeParent == 'MATERIAL':
            nodeString = 'bpy.data.materials["{}"].node_tree.nodes["{}"]'.format(node.parentName, node.nodeName)
        else:
            nodeString = 'bpy.data.node_groups["{}"].nodes["{}"]'.format(node.parentName, node.nodeName)
        return properties.expandNodeProperty(nodeString, node.plugName)

    return []
