# <pep8 compliant>

# ----------------------------------------------------------------------
# Label
# ----------------------------------------------------------------------

NAME_LABEL = "Tool Shelf"

# Preferences
LANGUAGE_LABEL = "言語（再起動が必要）"

ADD_GROUP_LABEL = "グループを追加"
ADD_TOOL_LABEL = "ツールを追加"
ADDON_TOGGLE_LABEL = "アドオン トグル"
ADDON_LABEL = "アドオン"
AFTER_GROUP_LABEL = "グループの後"
AFTER_TOOL_LABEL = "ツールの後"
APPLY_ORDER_LABEL = "適用順"
AUTO_EXPAND_LABEL = "自動展開"
COMMAND_LABEL = "コマンド"
COMMANDS_LABEL = "コマンド"
DELETE_LABEL = "削除"
EDIT_LABEL = "編集"
EDIT_SET_LABEL = "セットを編集"
GROUP_LABEL = "グループ"
ICON_LABEL = "アイコン"
ICONS_LABEL = "アイコン"
ICON_ONLY_LABEL = "アイコンのみ"
IMPORT_LABEL = "インポート"
LABELS_LABEL = "ラベル"
MOVE_ITEM_DOWN_LABEL = "アイテムを下へ移動"
MOVE_ITEM_UP_LABEL = "アイテムを上へ移動"
MODE_LABEL = "モード"
MOVE_DOWN_LABEL = "下へ移動"
MOVE_UP_LABEL = "上へ移動"
NEW_GROUP_LABEL = "新規グループ"
NEW_NAME_LABEL = "名前"
NEW_SET_LABEL = "新規セット"
PROPERTY_LABEL = "プロパティ"
PROPERTY_VALUE_LABEL = "値"
PROPERTY_CALLBACK_LABEL = "コールバックとしてコマンドを使用"
ROW_BUTTONS_LABEL = "行ボタン"
SELECT_ITEM_LABEL = "––– 選択 –––"
SET_NAME_LABEL = "セット名"
SETUP_LABEL = "セットアップ"
TOOL_LABEL = "ツール"
TOOLTIP_LABEL = "ツールチップ"
VIEW_COMMAND_LABEL = "コマンドを表示"

# ----------------------------------------------------------------------
# Description/Annotation
# ----------------------------------------------------------------------

# Preferences
ANN_LANGUAGE = "プロパティとメッセージの言語"

ANN_ADDON = "トグルボタンを作成するアドオン"
ANN_COMMAND = ("ボタンのコマンド文字列。\n"
               "簡単なコマンドの場合、bpyインポートが自動的に追加されます。\n"
               "空白の場合はテキストエディタから内容を取得します")
ANN_EXECUTE_MODE = "現在のモードを実行"
ANN_EXPAND = "グループをデフォルトで展開するように設定"
ANN_IMPORT_FILE = "グループまたはツールをインポートする構成ファイル"
ANN_IMPORT_ITEM = "インポートするグループまたはツール"
ANN_GROUP = ("ツールを追加するグループ。\n"
             "新しいグループは、最後または選択したグループアイテムの後に作成されます")
ANN_ICON = ("32x32ピクセルのアイコンファイルの名前またはデフォルトのBlenderアイコン識別子、"
            "シングルクォートで囲まれたUnicode文字")
ANN_ICON_ONLY = "ボタンのラベルの代わりにアイコンのみ表示"
ANN_ITEM_ADD_NEW = "新しいグループまたはツールを追加"
ANN_ITEM_DELETE_EXISTING = "既存のグループまたはボタンを削除"
ANN_ITEM_DISPLAY_COMMAND = "ボタンコマンドをテキストエディタに表示"
ANN_ITEM_IMPORT = "構成ファイルからグループまたはツールをインポート"
ANN_ITEM_OVERWRITE = ("既存のボタンのコマンドを上書きします。\n"
                      "存在する設定を保持するには、アスタリスク*記号を使用します")
ANN_ITEM_REORDER = "グループとボタンの並べ替え"
ANN_MODE = "編集モードを切り替え"
ANN_NAME = ("グループまたはツールの名前。\n"
            "すべてのグループで一意の小文字である必要があります")
ANN_NEW_GROUP = "新しいツールではなく新しいグループを追加"
ANN_NEW_SET = "新しいツールセットを追加"
ANN_PROPERTY = "ツールに数値、ブール値、または文字列プロパティを追加"
ANN_PROPERTY_NAME = "プロパティの名前"
ANN_PROPERTY_VALUE = ("プロパティのデフォルト値。最小値と最大値を定義するには、"
                      "値、値、値の形式を使用します")
ANN_PROPERTY_CALLBACK = ("更新オプションが設定されたすべてのプロパティに対して、"
                         "コマンド文字列をコールバック関数の本文として使用します")
ANN_SELECT_GROUP = "グループを選択"
ANN_SET_COLUMNS = "1行のボタンの数"
ANN_SET_NAME = "ボタンセットの名前"
ANN_TOGGLE_ADDON = "アドオンを有効または無効にするボタンを作成"
ANN_TOOL = "編集するツールコマンド"
ANN_TOOLTIP = "ボタンのツールチップ"

# ----------------------------------------------------------------------
# Info
# ----------------------------------------------------------------------


# ----------------------------------------------------------------------
# Warning/Error
# ----------------------------------------------------------------------

WARNING_ADDON_INCOMPATIBLE = "このアドオンは互換性がなく、設定から有効または無効にする必要があります："
WARNING_ADDON_MISSING = "この名前のアドオンは存在しません："
WARNING_BRACKETS_INCOMPLETE = "プロパティの括弧が不完全です"
WARNING_GROUP_NAME_EXISTS = "グループ名はすでに存在します"
WARNING_IMAGE_MISSING = "パスに画像が存在しません："
WARNING_LABEL_COMMAND_MISMATCH = "ツールのラベルとコマンドの数が一致しません"
WARNING_NO_GROUP_SELECTED = "グループが選択されていません"
WARNING_NO_NAME = "名前が定義されていません"
WARNING_NO_TEXT_EDITOR = "ツールコマンドを取得するためのテキストエディタが開いていません"
WARNING_NO_TEXT_EDITOR_TO_VIEW = "コマンドを表示するためのテキストエディタが開いていません"
WARNING_NO_TOOL_IN_GROUP = "選択したグループにツールが存在しません"
WARNING_NO_TOOL_SELECTED = "ツールが選択されていません"
WARNING_PROPERTY_NAME_MISSING = "プロパティ名と/またはデフォルト値が不足しています"
WARNING_PROPERTY_VALUE_MISMATCH = "プロパティと値の数が一致しません"
WARNING_SELECT_CONFIG = "有効な構成ファイルを選択してください"
WARNING_SELECT_TO_IMPORT = "インポートするグループまたはツールを選択してください"
WARNING_TOOL_EXISTS_IN_GROUP = "ツール名は既にグループ内に存在します"
