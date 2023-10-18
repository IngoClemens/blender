# <pep8 compliant>

# ----------------------------------------------------------------------
# Label
# ----------------------------------------------------------------------

NAME_LABEL = "Tool Shelf"

# Preferences
LANGUAGE_LABEL = "Sprache (Erfordert Neustart)"

ADD_GROUP_LABEL = "Gruppe hinzufügen"
ADD_TOOL_LABEL = "Tool hinzufügen"
ADDON_TOGGLE_LABEL = "Add-on Umschalten"
ADDON_LABEL = "Add-on"
AFTER_GROUP_LABEL = "Nach Gruppe"
AFTER_TOOL_LABEL = "Nach Tool"
APPLY_ORDER_LABEL = "Reihenfolge Ändern"
AUTO_EXPAND_LABEL = "Automatisch Aufklappen"
COMMAND_LABEL = "Befehl"
COMMANDS_LABEL = "Befehle"
DELETE_LABEL = "Löschen"
EDIT_LABEL = "Bearbeiten"
EDIT_SET_LABEL = "Set Bearbeiten"
GROUP_LABEL = "Gruppe"
ICON_LABEL = "Icon"
ICONS_LABEL = "Icon"
ICON_ONLY_LABEL = "Nur Icon"
IMPORT_LABEL = "Importieren"
LABELS_LABEL = "Beschriftungen"
MOVE_ITEM_DOWN_LABEL = "Element nach unten verschieben"
MOVE_ITEM_UP_LABEL = "Element nach oben verschieben"
MODE_LABEL = "Modus"
MOVE_DOWN_LABEL = "Nach unten"
MOVE_UP_LABEL = "Nach oben"
NEW_GROUP_LABEL = "Neue Gruppe"
NEW_NAME_LABEL = "Name"
NEW_SET_LABEL = "Neues Set"
PROPERTY_LABEL = "Eigenschaft"
PROPERTY_VALUE_LABEL = "Wert"
PROPERTY_CALLBACK_LABEL = "Befehl als Callback"
ROW_BUTTONS_LABEL = "Schaltflächen Reihe"
SELECT_ITEM_LABEL = "––– Wählen –––"
SET_NAME_LABEL = "Set-Name"
SETUP_LABEL = "Einrichtung"
TOOL_LABEL = "Tool"
TOOLTIP_LABEL = "Quickinfo"
VIEW_COMMAND_LABEL = "Befehl anzeigen"

# ----------------------------------------------------------------------
# Description/Annotation
# ----------------------------------------------------------------------

# Preferences
ANN_LANGUAGE = "Die Sprache für Eigenschaften und Meldungen"

ANN_ADDON = "Das Add-on zum Erstellen eines Umschaltknopfs"
ANN_COMMAND = ("Die Befehlszeichenfolge für die Schaltfläche.\n"
               "bpy import wird für einfache Befehle automatisch hinzugefügt.\n"
               "Leer lassen, um den Inhalt des Texteditors zu nutzen")
ANN_EXECUTE_MODE = "Den aktuellen Modus ausführen"
ANN_EXPAND = "Die Gruppe standardmäßig aufklappen"
ANN_IMPORT_FILE = "Die Konfigurationsdatei zum Importieren von Gruppen oder Tools"
ANN_IMPORT_ITEM = "Die zu importierende Gruppe oder das Tool"
ANN_GROUP = ("Die Gruppe, zu der das Tool hinzugefügt werden soll.\n"
             "Eine neue Gruppe wird nach der letzten oder nach dem ausgewählten Gruppenelement erstellt")
ANN_ICON = ("Der Dateiname des Icons mit 32x32 Pixeln oder ein Standard-Blender-Symbolname "
            "in einfachen Anführungszeichen oder ein Unicode-Zeichen")
ANN_ICON_ONLY = "Nur das Symbol anzeigen, anstelle der Schaltflächenbeschriftung"
ANN_ITEM_ADD_NEW = "Eine neue Gruppe oder ein neues Tool hinzufügen"
ANN_ITEM_DELETE_EXISTING = "Eine vorhandene Gruppe oder Schaltfläche löschen"
ANN_ITEM_DISPLAY_COMMAND = "Einen Schaltflächenbefehl im Texteditor anzeigen"
ANN_ITEM_IMPORT = "Eine Gruppe oder ein Tool aus einer Konfigurationsdatei importieren"
ANN_ITEM_OVERWRITE = ("Den Befehl einer vorhandenen Schaltfläche überschreiben.\nMit Sternchen * "
                      "Symbol werden bestehende Einstellungen behalten")
ANN_ITEM_REORDER = "Gruppen und Schaltflächen neu anordnen"
ANN_MODE = "Den Bearbeitungsmodus ändern"
ANN_NAME = ("Der Name der Gruppe oder des Tools.\n"
            "Er muss in Kleinbuchstaben in allen Gruppen eindeutig sein")
ANN_NEW_GROUP = "Eine neue Gruppe anstelle eines neuen Tools hinzufügen"
ANN_NEW_SET = "Ein neues Toolset hinzufügen"
ANN_PROPERTY = "Eine numerische, boolesche oder String-Eigenschaft zum Werkzeug hinzufügen"
ANN_PROPERTY_NAME = "Der Name der Eigenschaft"
ANN_PROPERTY_VALUE = ("Der Standardwert für die Eigenschaft. Um Mindest- und Höchstwerte festzulegen, "
                      "sollten die Werte auf folgende Weise eingegeben werden: Wert, Wert, Wert")
ANN_PROPERTY_CALLBACK = ("Der Befehls-Code wird als Update-Callback-Funktion für alle "
                         "Eigenschaften verwendet")
ANN_SELECT_GROUP = "Eine Gruppe auswählen"
ANN_SET_COLUMNS = "Die Anzahl der Schaltflächen in einer Zeile"
ANN_SET_NAME = "Der Name des Schaltflächensatzes"
ANN_TOGGLE_ADDON = "Eine Schaltfläche erstellen, um ein Add-on zu aktivieren oder zu deaktivieren"
ANN_TOOL = "Der Tool-Befehl zum Bearbeiten"
ANN_TOOLTIP = "Die Quickinfo für die Schaltfläche"

# ----------------------------------------------------------------------
# Info
# ----------------------------------------------------------------------


# ----------------------------------------------------------------------
# Warning/Error
# ----------------------------------------------------------------------

WARNING_ADDON_INCOMPATIBLE = "Das Add-on ist nicht kompatibel und muss in den Einstellungen manuell aktiviert/deaktiviert werden: "
WARNING_ADDON_MISSING = "Ein Add-on mit diesem Namen existiert nicht: "
WARNING_BRACKETS_INCOMPLETE = "Die Klammern für die Eigenschaften sind unvollständig"
WARNING_GROUP_NAME_EXISTS = "Der Gruppenname existiert bereits"
WARNING_IMAGE_MISSING = "Das Bild existiert nicht im angegebenen Pfad: "
WARNING_LABEL_COMMAND_MISMATCH = "Die Anzahl der Tool-Beschriftungen und -befehle stimmt nicht überein"
WARNING_NO_GROUP_SELECTED = "Keine Gruppe ausgewählt"
WARNING_NO_NAME = "Kein Name definiert"
WARNING_NO_TEXT_EDITOR = "Es ist kein Texteditor geöffnet, um den Tool-Befehl abzurufen"
WARNING_NO_TEXT_EDITOR_TO_VIEW = "Es ist kein Texteditor geöffnet, um den Befehl anzuzeigen"
WARNING_NO_TOOL_IN_GROUP = "In der ausgewählten Gruppe existiert kein Tool"
WARNING_NO_TOOL_SELECTED = "Kein Tool ausgewählt"
WARNING_PROPERTY_NAME_MISSING = "Ein Eigenschaftsname und/oder ein Standardwert fehlen"
WARNING_PROPERTY_VALUE_MISMATCH = "Die Anzahl der Eigenschaften und Werte stimmt nicht überein"
WARNING_SELECT_CONFIG = "Eine gültige Konfigurationsdatei muss ausgewählt sein"
WARNING_SELECT_TO_IMPORT = "Eine Gruppe oder ein Tool zum Importieren auswählen"
WARNING_TOOL_EXISTS_IN_GROUP = "Der Tool-Name existiert bereits in der Gruppe"
