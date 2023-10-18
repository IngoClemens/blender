# <pep8 compliant>

# ----------------------------------------------------------------------
# Label
# ----------------------------------------------------------------------

NAME_LABEL = "Tool Shelf"

# Preferences
LANGUAGE_LABEL = "언어 (재시작 필요)"

ADD_GROUP_LABEL = "그룹 추가"
ADD_TOOL_LABEL = "도구 추가"
ADDON_TOGGLE_LABEL = "애드온 전환"
ADDON_LABEL = "애드온"
AFTER_GROUP_LABEL = "그룹 이후"
AFTER_TOOL_LABEL = "도구 이후"
APPLY_ORDER_LABEL = "적용 순서"
AUTO_EXPAND_LABEL = "자동 확장"
COMMAND_LABEL = "명령"
COMMANDS_LABEL = "명령들"
DELETE_LABEL = "삭제"
EDIT_LABEL = "편집"
EDIT_SET_LABEL = "집합 편집"
GROUP_LABEL = "그룹"
ICON_LABEL = "아이콘"
ICONS_LABEL = "아이콘들"
ICON_ONLY_LABEL = "아이콘만"
IMPORT_LABEL = "가져오기"
LABELS_LABEL = "라벨"
MOVE_ITEM_DOWN_LABEL = "아이템 아래로 이동"
MOVE_ITEM_UP_LABEL = "아이템 위로 이동"
MODE_LABEL = "모드"
MOVE_DOWN_LABEL = "아래로 이동"
MOVE_UP_LABEL = "위로 이동"
NEW_GROUP_LABEL = "새 그룹"
NEW_NAME_LABEL = "이름"
NEW_SET_LABEL = "새로운 집합"
PROPERTY_LABEL = "프로퍼티"
PROPERTY_VALUE_LABEL = "값"
PROPERTY_CALLBACK_LABEL = "콜백으로 명령 사용"
ROW_BUTTONS_LABEL = "행 버튼들"
SELECT_ITEM_LABEL = "––– 선택 –––"
SET_NAME_LABEL = "집합 이름"
SETUP_LABEL = "설정"
TOOL_LABEL = "도구"
TOOLTIP_LABEL = "툴팁"
VIEW_COMMAND_LABEL = "명령 보기"

# ----------------------------------------------------------------------
# Description/Annotation
# ----------------------------------------------------------------------

# Preferences
ANN_LANGUAGE = "속성과 메시지에 대한 언어"

ANN_ADDON = "전환 버튼을 생성하는 애드온"
ANN_COMMAND = ("버튼에 대한 명령 문자열.\n"
               "단순한 명령의 경우 자동으로 bpy 가져오기가 추가됩니다.\n"
               "내용을 얻으려면 비워두십시오.")
ANN_EXECUTE_MODE = "현재 모드 실행"
ANN_EXPAND = "그룹을 기본적으로 확장하도록 설정"
ANN_IMPORT_FILE = "그룹 또는 도구를 가져 오기 위한 설정 파일"
ANN_IMPORT_ITEM = "가져올 그룹 또는 도구"
ANN_GROUP = ("도구를 추가 할 그룹.\n"
             "마지막 또는 선택한 그룹 항목 이후에 새로운 그룹이 만들어집니다.")
ANN_ICON = "32x32 픽셀 아이콘 파일 이름 또는 작은 따옴표로 묶인 Blender 기본 아이콘 식별자 또는 유니코드 문자"
ANN_ICON_ONLY = "버튼 레이블 대신 아이콘만 표시"
ANN_ITEM_ADD_NEW = "새로운 그룹 또는 도구 추가"
ANN_ITEM_DELETE_EXISTING = "기존 그룹 또는 버튼 삭제"
ANN_ITEM_DISPLAY_COMMAND = "텍스트 편집기에서 버튼 명령 표시"
ANN_ITEM_IMPORT = "구성 파일에서 그룹 또는 도구 가져 오기"
ANN_ITEM_OVERWRITE = "기존 버튼의 명령 덮어 쓰기.\n기존 설정 유지에는 별표 *를 사용하십시오."
ANN_ITEM_REORDER = "그룹 및 버튼 재정렬"
ANN_MODE = "편집 모드 전환"
ANN_NAME = ("그룹 또는 도구의 이름.\n"
            "모든 그룹에서 고유해야합니다.")
ANN_NEW_GROUP = "새 도구 대신 새 그룹 추가"
ANN_NEW_SET = "새로운 도구 세트 추가"
ANN_PROPERTY = "도구에 숫자, 부울 또는 문자열 속성 추가"
ANN_PROPERTY_NAME = "속성 이름"
ANN_PROPERTY_VALUE = "속성의 기본 값. 최소값 및 최대값을 정의하려면 다음 형식을 사용하십시오 : 값, 값, 값"
ANN_PROPERTY_CALLBACK = "모든 속성에 대해 업데이트 옵션을 갖는 콜백 함수의 본문으로 명령 문자열을 사용하십시오."
ANN_SELECT_GROUP = "그룹 선택"
ANN_SET_COLUMNS = "한 행에 버튼 수"
ANN_SET_NAME = "버튼 세트 이름"
ANN_TOGGLE_ADDON = "애드온을 활성화 또는 비활성화하기 위한 버튼 생성"
ANN_TOOL = "편집 할 도구 명령"
ANN_TOOLTIP = "버튼의 툴팁"

# ----------------------------------------------------------------------
# Info
# ----------------------------------------------------------------------


# ----------------------------------------------------------------------
# Warning/Error
# ----------------------------------------------------------------------

WARNING_ADDON_INCOMPATIBLE = "애드온이 호환되지 않으며 환경 설정에서 활성화/비활성화해야합니다 : "
WARNING_ADDON_MISSING = "이름으로 된 이 애드온이 없습니다: "
WARNING_BRACKETS_INCOMPLETE = "속성의 괄호가 불완전합니다"
WARNING_GROUP_NAME_EXISTS = "그룹 이름이 이미 존재합니다"
WARNING_IMAGE_MISSING = "경로에 이미지가 존재하지 않습니다: "
WARNING_LABEL_COMMAND_MISMATCH = "도구 레이블 및 명령의 수가 일치하지 않습니다"
WARNING_NO_GROUP_SELECTED = "선택한 그룹이 없습니다"
WARNING_NO_NAME = "이름이 정의되지 않았습니다"
WARNING_NO_TEXT_EDITOR = "도구 명령을 가져 오기위한 열린 텍스트 편집기가 없습니다"
WARNING_NO_TEXT_EDITOR_TO_VIEW = "명령을 볼 텍스트 편집기가 열려 있지 않습니다"
WARNING_NO_TOOL_IN_GROUP = "선택한 그룹에 도구가 없습니다"
WARNING_NO_TOOL_SELECTED = "도구가 선택되지 않았습니다"
WARNING_PROPERTY_NAME_MISSING = "속성 이름 및/또는 기본 값이 누락되었습니다"
WARNING_PROPERTY_VALUE_MISMATCH = "속성 및 값의 수가 일치하지 않습니다"
WARNING_SELECT_CONFIG = "유효한 구성 파일을 선택하십시오"
WARNING_SELECT_TO_IMPORT = "가져올 그룹 또는 도구를 선택하십시오"
WARNING_TOOL_EXISTS_IN_GROUP = "그룹에 이미 도구 이름이 있습니다"
