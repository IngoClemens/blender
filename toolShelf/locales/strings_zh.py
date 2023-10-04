# <pep8 compliant>

# ----------------------------------------------------------------------
# Label
# ----------------------------------------------------------------------

NAME_LABEL = "Tool Shelf"

# Preferences
LANGUAGE_LABEL = "语言"

ADD_GROUP_LABEL = "添加组"
ADD_TOOL_LABEL = "添加工具"
ADDON_TOGGLE_LABEL = "插件切换"
ADDON_LABEL = "插件"
AFTER_GROUP_LABEL = "组后"
AFTER_TOOL_LABEL = "工具后"
APPLY_ORDER_LABEL = "应用顺序"
AUTO_EXPAND_LABEL = "自动展开"
COMMAND_LABEL = "命令"
COMMANDS_LABEL = "命令"
DELETE_LABEL = "删除"
EDIT_LABEL = "编辑"
EDIT_SET_LABEL = "编辑设置"
GROUP_LABEL = "组"
ICON_LABEL = "图标"
ICONS_LABEL = "图标"
ICON_ONLY_LABEL = "仅图标"
IMPORT_LABEL = "导入"
LABELS_LABEL = "标签"
MOVE_ITEM_DOWN_LABEL = "下移项目"
MOVE_ITEM_UP_LABEL = "上移项目"
MODE_LABEL = "模式"
MOVE_DOWN_LABEL = "下移"
MOVE_UP_LABEL = "上移"
NEW_GROUP_LABEL = "新建组"
NEW_NAME_LABEL = "名称"
NEW_SET_LABEL = "新建集"
PROPERTY_LABEL = "属性"
PROPERTY_VALUE_LABEL = "值"
PROPERTY_CALLBACK_LABEL = "命令作为回调"
ROW_BUTTONS_LABEL = "行按钮"
SELECT_ITEM_LABEL = "––– 选择 –––"
SET_NAME_LABEL = "集名称"
SETUP_LABEL = "设置"
TOOL_LABEL = "工具"
TOOLTIP_LABEL = "工具提示"
VIEW_COMMAND_LABEL = "查看命令"

# ----------------------------------------------------------------------
# Description/Annotation
# ----------------------------------------------------------------------

# Preferences
ANN_LANGUAGE = "属性和消息的语言"

ANN_ADDON = "创建切换按钮的插件"
ANN_COMMAND = ("按钮的命令字符串。\n"
               "对于简单的命令，将自动添加bpy导入。\n"
               "留空以从文本编辑器获取内容")
ANN_EXECUTE_MODE = "执行当前模式"
ANN_EXPAND = "将组设置为默认展开"
ANN_IMPORT_FILE = "从中导入组或工具的配置文件"
ANN_IMPORT_ITEM = "要导入的组或工具"
ANN_GROUP = ("要将工具添加到的组。\n"
             "新组将在最后一个组或选定的组项目后创建")
ANN_ICON = ("32x32像素图标文件的名称或默认的Blender图标标识符，"
            "用单引号括起来或Unicode字符")
ANN_ICON_ONLY = "仅显示图标而不是按钮标签"
ANN_ITEM_ADD_NEW = "添加新组或工具"
ANN_ITEM_DELETE_EXISTING = "删除现有组或按钮"
ANN_ITEM_DISPLAY_COMMAND = "在文本编辑器中显示按钮命令"
ANN_ITEM_IMPORT = "从配置文件导入组或工具"
ANN_ITEM_OVERWRITE = ("覆盖现有按钮的命令。\n"
                      "使用星号*保留现有设置")
ANN_ITEM_REORDER = "重新排序组和按钮"
ANN_MODE = "切换编辑模式"
ANN_NAME = ("组或工具的名称。\n"
            "它需要在所有组中以小写形式是唯一的")
ANN_NEW_GROUP = "添加新组而不是新工具"
ANN_NEW_SET = "添加新工具集"
ANN_PROPERTY = "向工具添加数值、布尔或字符串属性"
ANN_PROPERTY_NAME = "属性名称"
ANN_PROPERTY_VALUE = "属性的默认值。要定义最小和最大值，请使用以下格式：值，值，值"
ANN_PROPERTY_CALLBACK = "将命令字符串用作所有属性的更新选项的回调函数的主体"
ANN_SELECT_GROUP = "选择一个组"
ANN_SET_COLUMNS = "一行中的按钮数"
ANN_SET_NAME = "按钮集的名称"
ANN_TOGGLE_ADDON = "创建按钮以启用或禁用插件"
ANN_TOOL = "要编辑的工具命令"
ANN_TOOLTIP = "按钮的工具提示"

# ----------------------------------------------------------------------
# Info
# ----------------------------------------------------------------------


# ----------------------------------------------------------------------
# Warning/Error
# ----------------------------------------------------------------------

WARNING_ADDON_INCOMPATIBLE = "插件不兼容，必须在首选项中启用/禁用："
WARNING_ADDON_MISSING = "不存在该名称的插件："
WARNING_BRACKETS_INCOMPLETE = "属性的括号不完整"
WARNING_GROUP_NAME_EXISTS = "组名已存在"
WARNING_IMAGE_MISSING = "路径中不存在该图像："
WARNING_LABEL_COMMAND_MISMATCH = "工具标签和命令的数量不匹配"
WARNING_NO_GROUP_SELECTED = "未选择任何组"
WARNING_NO_NAME = "未定义名称"
WARNING_NO_TEXT_EDITOR = "没有打开的文本编辑器以获取工具命令"
WARNING_NO_TEXT_EDITOR_TO_VIEW = "没有打开的文本编辑器以查看命令"
WARNING_NO_TOOL_IN_GROUP = "在选定的组中不存在工具"
WARNING_NO_TOOL_SELECTED = "未选择工具"
WARNING_PROPERTY_NAME_MISSING = "属性名称和/或默认值丢失"
WARNING_PROPERTY_VALUE_MISMATCH = "属性和值的数量不匹配"
WARNING_SELECT_CONFIG = "选择有效的配置文件"
WARNING_SELECT_TO_IMPORT = "选择要导入的组或工具"
WARNING_TOOL_EXISTS_IN_GROUP = "该组中已存在工具名称"
