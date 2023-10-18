# <pep8 compliant>

# ----------------------------------------------------------------------
# Label
# ----------------------------------------------------------------------

NAME_LABEL = "Tool Shelf"

# Preferences
LANGUAGE_LABEL = "Idioma (Requiere reinicio)"

ADD_GROUP_LABEL = "Agregar Grupo"
ADD_TOOL_LABEL = "Agregar Herramienta"
ADDON_TOGGLE_LABEL = "Alternar Add-on"
ADDON_LABEL = "Add-on"
AFTER_GROUP_LABEL = "Después del Grupo"
AFTER_TOOL_LABEL = "Después de la Herramienta"
APPLY_ORDER_LABEL = "Orden de Aplicación"
AUTO_EXPAND_LABEL = "Expansión Automática"
COMMAND_LABEL = "Comando"
COMMANDS_LABEL = "Comandos"
DELETE_LABEL = "Eliminar"
EDIT_LABEL = "Editar"
EDIT_SET_LABEL = "Editar Conjunto"
GROUP_LABEL = "Grupo"
ICON_LABEL = "Ícono"
ICONS_LABEL = "Íconos"
ICON_ONLY_LABEL = "Solo Ícono"
IMPORT_LABEL = "Importar"
LABELS_LABEL = "Etiquetas"
MOVE_ITEM_DOWN_LABEL = "Mover Elemento Abajo"
MOVE_ITEM_UP_LABEL = "Mover Elemento Arriba"
MODE_LABEL = "Modo"
MOVE_DOWN_LABEL = "Mover Abajo"
MOVE_UP_LABEL = "Mover Arriba"
NEW_GROUP_LABEL = "Nuevo Grupo"
NEW_NAME_LABEL = "Nombre"
NEW_SET_LABEL = "Nuevo Conjunto"
PROPERTY_LABEL = "Propiedad"
PROPERTY_VALUE_LABEL = "Valor"
PROPERTY_CALLBACK_LABEL = "Comando como Devolución de Llamada"
ROW_BUTTONS_LABEL = "Botones de Fila"
SELECT_ITEM_LABEL = "––– Seleccionar –––"
SET_NAME_LABEL = "Nombre del Conjunto"
SETUP_LABEL = "Configuración"
TOOL_LABEL = "Herramienta"
TOOLTIP_LABEL = "Tooltip"
VIEW_COMMAND_LABEL = "Ver Comando"

# ----------------------------------------------------------------------
# Description/Annotation
# ----------------------------------------------------------------------

# Preferences
ANN_LANGUAGE = "El idioma para propiedades y mensajes"

ANN_ADDON = "El Add-on para crear un botón de alternancia"
ANN_COMMAND = ("La cadena de comando para el botón.\n"
               "Para comandos simples, la importación bpy se agrega automáticamente.\n"
               "Deje en blanco para obtener el contenido del editor de texto")
ANN_EXECUTE_MODE = "Ejecutar el modo actual"
ANN_EXPAND = "Establecer el grupo para que se expanda por defecto"
ANN_IMPORT_FILE = ("El archivo de configuración para importar grupos o "
                   "herramientas desde")
ANN_IMPORT_ITEM = "El grupo o herramienta a importar"
ANN_GROUP = ("El grupo al que agregar la herramienta.\n"
             "Se creará un nuevo grupo después del último o después del elemento de grupo seleccionado")
ANN_ICON = ("El nombre del archivo de ícono con 32x32 píxeles o un identificador de ícono de Blender predeterminado "
            "encerrado en comillas simples o un carácter Unicode")
ANN_ICON_ONLY = "Mostrar solo el ícono en lugar de la etiqueta del botón"
ANN_ITEM_ADD_NEW = "Agregar un nuevo grupo o herramienta"
ANN_ITEM_DELETE_EXISTING = "Eliminar un grupo o botón existente"
ANN_ITEM_DISPLAY_COMMAND = "Mostrar un comando de botón en el editor de texto"
ANN_ITEM_IMPORT = "Importar un grupo o herramienta desde un archivo de configuración"
ANN_ITEM_OVERWRITE = ("Sobrescribir el comando de un botón existente.\nUse el símbolo asterisco * "
                      "para mantener la configuración existente")
ANN_ITEM_REORDER = "Reordenar grupos y botones"
ANN_MODE = "Cambiar el modo de edición"
ANN_NAME = ("El nombre del grupo o herramienta.\n"
            "Debe ser único en minúsculas en todos los grupos")
ANN_NEW_GROUP = "Agregar un nuevo grupo en lugar de una nueva herramienta"
ANN_NEW_SET = "Agregar un nuevo conjunto de herramientas"
ANN_PROPERTY = "Agregar una propiedad numérica, booleana o de cadena a la herramienta"
ANN_PROPERTY_NAME = "El nombre de la propiedad"
ANN_PROPERTY_VALUE = ("El valor predeterminado de la propiedad. Para definir valores mínimo y máximo "
                      "utilice el formato: valor, valor, valor")
ANN_PROPERTY_CALLBACK = ("Usar la cadena de comando como cuerpo de una función de devolución de llamada para todas las "
                         "propiedades con su opción de actualización establecida")
ANN_SELECT_GROUP = "Seleccionar un grupo"
ANN_SET_COLUMNS = "El número de botones en una fila"
ANN_SET_NAME = "El nombre del conjunto de botones"
ANN_TOGGLE_ADDON = "Crear un botón para habilitar o deshabilitar un Add-on"
ANN_TOOL = "El comando de herramienta a editar"
ANN_TOOLTIP = "El tooltip del botón"

# ----------------------------------------------------------------------
# Info
# ----------------------------------------------------------------------


# ----------------------------------------------------------------------
# Warning/Error
# ----------------------------------------------------------------------

WARNING_ADDON_INCOMPATIBLE = "El Add-on no es compatible y debe habilitarse/deshabilitarse desde las preferencias: "
WARNING_ADDON_MISSING = "No existe un Add-on con este nombre: "
WARNING_BRACKETS_INCOMPLETE = "Los corchetes de las propiedades están incompletos"
WARNING_GROUP_NAME_EXISTS = "El nombre de grupo ya existe"
WARNING_IMAGE_MISSING = "La imagen no existe en la ruta: "
WARNING_LABEL_COMMAND_MISMATCH = "El número de etiquetas y comandos de herramienta no coincide"
WARNING_NO_GROUP_SELECTED = "Ningún grupo seleccionado"
WARNING_NO_NAME = "No se ha definido ningún nombre"
WARNING_NO_TEXT_EDITOR = "No hay un editor de texto abierto para obtener el comando de herramienta"
WARNING_NO_TEXT_EDITOR_TO_VIEW = "No hay un editor de texto abierto para ver el comando"
WARNING_NO_TOOL_IN_GROUP = "No existe una herramienta en el grupo seleccionado"
WARNING_NO_TOOL_SELECTED = "Ninguna herramienta seleccionada"
WARNING_PROPERTY_NAME_MISSING = "Falta el nombre de una propiedad y/o valor predeterminado"
WARNING_PROPERTY_VALUE_MISMATCH = "El número de propiedades y valores no coincide"
WARNING_SELECT_CONFIG = "Seleccione un archivo de configuración válido"
WARNING_SELECT_TO_IMPORT = "Seleccione un grupo o herramienta para importar"
WARNING_TOOL_EXISTS_IN_GROUP = "El nombre de la herramienta ya existe en el grupo"
