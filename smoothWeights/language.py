# <pep8 compliant>

import bpy

import importlib


NAME = "smoothWeights"
LANGUAGE_FILES = {"ENGLISH": "strings_en",
                  "FRENCH": "strings_fr",
                  "GERMAN": "strings_de",
                  "JAPANESE": "strings_jp",
                  "KOREAN": "strings_ko",
                  "PORTUGUESE": "strings_pt",
                  "CHINESE": "strings_zh",
                  "SPANISH": "strings_es"}
LANGUAGE_ITEMS = (("ENGLISH", "English (English)", ""),
                  ("FRENCH", "French (Français)", ""),
                  ("GERMAN", "German (Deutsch)", ""),
                  ("JAPANESE", "Japanese (日本人)", ""),
                  ("KOREAN", "Korean (한국어)", ""),
                  ("PORTUGUESE", "Portuguese (Português)", ""),
                  ("CHINESE", "Simplified Chinese (简体中文）", ""),
                  ("SPANISH", "Spanish (Español)", ""))


def getLanguage():
    """Return the language module.

    :return: The language module.
    :rtype: module
    """
    addons = bpy.context.preferences.addons
    if NAME in addons and hasattr(addons[NAME].preferences, "language"):
        language = addons[NAME].preferences.language

        if language in LANGUAGE_FILES:
            modPath = "{}.locales.{}".format(NAME, LANGUAGE_FILES[language])
            return importlib.import_module(modPath)

    modPath = "{}.locales.{}".format(NAME, LANGUAGE_FILES["ENGLISH"])
    return importlib.import_module(modPath)


def reloadDependencies():
    """Reload the modules which are affected by a language change.
    """
    mods = ["constants", "panel", "pies", "preferences", "smoothWeights", "symmetryMap"]
    for mod in mods:
        moduleName = ".".join([NAME, mod])
        try:
            module = __import__(moduleName, fromlist=[""])
            importlib.reload(module)

        except (Exception, ):
            pass
