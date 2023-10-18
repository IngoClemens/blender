# <pep8 compliant>

# ----------------------------------------------------------------------
# Label
# ----------------------------------------------------------------------

NAME_LABEL = "Tool Shelf"

# Preferences
LANGUAGE_LABEL = "Langue (Nécessite un redémarrage)"

ADD_GROUP_LABEL = "Ajouter un Groupe"
ADD_TOOL_LABEL = "Ajouter un Outil"
ADDON_TOGGLE_LABEL = "Basculer l'Add-on"
ADDON_LABEL = "Add-on"
AFTER_GROUP_LABEL = "Après le Groupe"
AFTER_TOOL_LABEL = "Après l'Outil"
APPLY_ORDER_LABEL = "Ordre d'Application"
AUTO_EXPAND_LABEL = "Expansion Automatique"
COMMAND_LABEL = "Commande"
COMMANDS_LABEL = "Commandes"
DELETE_LABEL = "Supprimer"
EDIT_LABEL = "Éditer"
EDIT_SET_LABEL = "Éditer l'Ensemble"
GROUP_LABEL = "Groupe"
ICON_LABEL = "Icône"
ICONS_LABEL = "Icônes"
ICON_ONLY_LABEL = "Icône Seule"
IMPORT_LABEL = "Importer"
LABELS_LABEL = "Étiquettes"
MOVE_ITEM_DOWN_LABEL = "Déplacer l'Élément vers le Bas"
MOVE_ITEM_UP_LABEL = "Déplacer l'Élément vers le Haut"
MODE_LABEL = "Mode"
MOVE_DOWN_LABEL = "Descendre"
MOVE_UP_LABEL = "Monter"
NEW_GROUP_LABEL = "Nouveau Groupe"
NEW_NAME_LABEL = "Nom"
NEW_SET_LABEL = "Nouvel Ensemble"
PROPERTY_LABEL = "Propriété"
PROPERTY_VALUE_LABEL = "Valeur"
PROPERTY_CALLBACK_LABEL = "Commande comme Rappel"
ROW_BUTTONS_LABEL = "Boutons de Ligne"
SELECT_ITEM_LABEL = "––– Sélectionner –––"
SET_NAME_LABEL = "Nom de l'Ensemble"
SETUP_LABEL = "Configuration"
TOOL_LABEL = "Outil"
TOOLTIP_LABEL = "Info-bulle"
VIEW_COMMAND_LABEL = "Voir la Commande"

# ----------------------------------------------------------------------
# Description/Annotation
# ----------------------------------------------------------------------

# Preferences
ANN_LANGUAGE = "La langue des propriétés et des messages"

ANN_ADDON = "L'Add-on pour créer un bouton basculant"
ANN_COMMAND = ("La chaîne de commande pour le bouton.\n"
               "Pour les commandes simples, l'importation bpy est ajoutée automatiquement.\n"
               "Laissez vide pour obtenir le contenu de l'éditeur de texte")
ANN_EXECUTE_MODE = "Exécuter le mode actuel"
ANN_EXPAND = "Définir le groupe comme étant déployé par défaut"
ANN_IMPORT_FILE = ("Le fichier de configuration pour importer des groupes ou "
                   "des outils à partir de")
ANN_IMPORT_ITEM = "Le groupe ou l'outil à importer"
ANN_GROUP = ("Le groupe où ajouter l'outil.\n"
             "Un nouveau groupe sera créé après le dernier ou après l'élément de groupe sélectionné")
ANN_ICON = ("Le nom du fichier d'icône avec une résolution de 32x32 pixels ou un identifiant d'icône Blender par défaut "
            "encadré par des guillemets simples ou un caractère Unicode")
ANN_ICON_ONLY = "Afficher uniquement l'icône au lieu de l'étiquette du bouton"
ANN_ITEM_ADD_NEW = "Ajouter un nouveau groupe ou un nouvel outil"
ANN_ITEM_DELETE_EXISTING = "Supprimer un groupe ou un bouton existant"
ANN_ITEM_DISPLAY_COMMAND = "Afficher une commande de bouton dans l'éditeur de texte"
ANN_ITEM_IMPORT = "Importer un groupe ou un outil à partir d'un fichier de configuration"
ANN_ITEM_OVERWRITE = ("Écraser la commande d'un bouton existant.\nUtilisez le symbole astérisque * "
                      "pour conserver les paramètres existants")
ANN_ITEM_REORDER = "Réorganiser les groupes et les boutons"
ANN_MODE = "Changer le mode d'édition"
ANN_NAME = ("Le nom du groupe ou de l'outil.\n"
            "Il doit être unique en minuscules dans tous les groupes")
ANN_NEW_GROUP = "Ajouter un nouveau groupe au lieu d'un nouvel outil"
ANN_NEW_SET = "Ajouter un nouvel ensemble d'outils"
ANN_PROPERTY = "Ajouter une propriété numérique, booléenne ou de chaîne à l'outil"
ANN_PROPERTY_NAME = "Le nom de la propriété"
ANN_PROPERTY_VALUE = ("La valeur par défaut de la propriété. Pour définir des valeurs minimales et maximales, "
                      "utilisez le format : valeur, valeur, valeur")
ANN_PROPERTY_CALLBACK = ("Utiliser la chaîne de commande comme corps d'une fonction de rappel pour toutes les "
                         "propriétés avec leur option de mise à jour définie")
ANN_SELECT_GROUP = "Sélectionner un groupe"
ANN_SET_COLUMNS = "Le nombre de boutons par ligne"
ANN_SET_NAME = "Le nom de l'ensemble de boutons"
ANN_TOGGLE_ADDON = "Créer un bouton pour activer ou désactiver un Add-on"
ANN_TOOL = "La commande de l'outil à éditer"
ANN_TOOLTIP = "L'info-bulle du bouton"

# ----------------------------------------------------------------------
# Info
# ----------------------------------------------------------------------


# ----------------------------------------------------------------------
# Warning/Error
# ----------------------------------------------------------------------

WARNING_ADDON_INCOMPATIBLE = "L'Add-on n'est pas compatible et doit être activé/désactivé depuis les préférences : "
WARNING_ADDON_MISSING = "Aucun Add-on portant ce nom n'existe : "
WARNING_BRACKETS_INCOMPLETE = "Les parenthèses pour les propriétés ne sont pas complètes"
WARNING_GROUP_NAME_EXISTS = "Le nom du groupe existe déjà"
WARNING_IMAGE_MISSING = "L'image n'existe pas dans le chemin : "
WARNING_LABEL_COMMAND_MISMATCH = "Le nombre d'étiquettes d'outils et de commandes ne correspond pas"
WARNING_NO_GROUP_SELECTED = "Aucun groupe sélectionné"
WARNING_NO_NAME = "Aucun nom défini"
WARNING_NO_TEXT_EDITOR = "Aucun éditeur de texte ouvert pour obtenir la commande de l'outil"
WARNING_NO_TEXT_EDITOR_TO_VIEW = "Aucun éditeur de texte ouvert pour afficher la commande"
WARNING_NO_TOOL_IN_GROUP = "Aucun outil n'existe dans le groupe sélectionné"
WARNING_NO_TOOL_SELECTED = "Aucun outil sélectionné"
WARNING_PROPERTY_NAME_MISSING = "Un nom de propriété et/ou une valeur par défaut sont manquants"
WARNING_PROPERTY_VALUE_MISMATCH = "Le nombre de propriétés et de valeurs ne correspond pas"
WARNING_SELECT_CONFIG = "Sélectionnez un fichier de configuration valide"
WARNING_SELECT_TO_IMPORT = "Sélectionnez un groupe ou un outil à importer"
WARNING_TOOL_EXISTS_IN_GROUP = "Le nom de l'outil existe déjà dans le groupe"
