# <pep8 compliant>

# ----------------------------------------------------------------------
# Label
# ----------------------------------------------------------------------

NAME_LABEL = "Tool Shelf"

# Preferences
LANGUAGE_LABEL = "Idioma (Requer reinício)"

ADD_GROUP_LABEL = "Adicionar Grupo"
ADD_TOOL_LABEL = "Adicionar Ferramenta"
ADDON_TOGGLE_LABEL = "Alternar Add-on"
ADDON_LABEL = "Add-on"
AFTER_GROUP_LABEL = "Após o Grupo"
AFTER_TOOL_LABEL = "Após a Ferramenta"
APPLY_ORDER_LABEL = "Ordem de Aplicação"
AUTO_EXPAND_LABEL = "Expandir Automaticamente"
COMMAND_LABEL = "Comando"
COMMANDS_LABEL = "Comandos"
DELETE_LABEL = "Apagar"
EDIT_LABEL = "Editar"
EDIT_SET_LABEL = "Editar Conjunto"
GROUP_LABEL = "Grupo"
ICON_LABEL = "Ícone"
ICONS_LABEL = "Ícones"
ICON_ONLY_LABEL = "Somente Ícone"
IMPORT_LABEL = "Importar"
LABELS_LABEL = "Rótulos"
MOVE_ITEM_DOWN_LABEL = "Mover Item para Baixo"
MOVE_ITEM_UP_LABEL = "Mover Item para Cima"
MODE_LABEL = "Modo"
MOVE_DOWN_LABEL = "Mover para Baixo"
MOVE_UP_LABEL = "Mover para Cima"
NEW_GROUP_LABEL = "Novo Grupo"
NEW_NAME_LABEL = "Nome"
NEW_SET_LABEL = "Novo Conjunto"
PROPERTY_LABEL = "Propriedade"
PROPERTY_VALUE_LABEL = "Valor"
PROPERTY_CALLBACK_LABEL = "Comando como Callback"
ROW_BUTTONS_LABEL = "Botões de Linha"
SELECT_ITEM_LABEL = "––– Selecionar –––"
SET_NAME_LABEL = "Nome do Conjunto"
SETUP_LABEL = "Configuração"
TOOL_LABEL = "Ferramenta"
TOOLTIP_LABEL = "Dica de Ferramenta"
VIEW_COMMAND_LABEL = "Ver Comando"

# ----------------------------------------------------------------------
# Description/Annotation
# ----------------------------------------------------------------------

# Preferences
ANN_LANGUAGE = "O idioma para propriedades e mensagens"

ANN_ADDON = "O add-on para criar um botão de alternância"
ANN_COMMAND = ("A string de comando para o botão.\n"
               "Para comandos simples, a importação bpy é adicionada automaticamente.\n"
               "Deixe em branco para obter o conteúdo do editor de texto")
ANN_EXECUTE_MODE = "Executar o modo atual"
ANN_EXPAND = "Definir o grupo para ser expandido por padrão"
ANN_IMPORT_FILE = ("O arquivo de configuração para importar grupos ou "
                   "ferramentas a partir de")
ANN_IMPORT_ITEM = "O grupo ou ferramenta a ser importado"
ANN_GROUP = ("O grupo ao qual adicionar a ferramenta.\n"
             "Um novo grupo será criado após o último ou após o item de grupo selecionado")
ANN_ICON = ("O nome do arquivo de ícone com 32x32 pixels ou um identificador de ícone padrão do Blender "
            "entre aspas simples ou um caractere Unicode")
ANN_ICON_ONLY = "Mostrar apenas o ícone em vez do rótulo do botão"
ANN_ITEM_ADD_NEW = "Adicionar um novo grupo ou ferramenta"
ANN_ITEM_DELETE_EXISTING = "Excluir um grupo ou botão existente"
ANN_ITEM_DISPLAY_COMMAND = "Exibir um comando de botão no editor de texto"
ANN_ITEM_IMPORT = "Importar um grupo ou ferramenta de um arquivo de configuração"
ANN_ITEM_OVERWRITE = ("Sobrescrever o comando de um botão existente.\nUse o asterisco * "
                      "para manter as configurações existentes")
ANN_ITEM_REORDER = "Reordenar grupos e botões"
ANN_MODE = "Alternar o modo de edição"
ANN_NAME = ("O nome do grupo ou ferramenta.\n"
            "Deve ser único em minúsculas em todos os grupos")
ANN_NEW_GROUP = "Adicionar um novo grupo em vez de uma nova ferramenta"
ANN_NEW_SET = "Adicionar um novo conjunto de ferramentas"
ANN_PROPERTY = "Adicionar uma propriedade numérica, booleana ou de string à ferramenta"
ANN_PROPERTY_NAME = "O nome da propriedade"
ANN_PROPERTY_VALUE = ("O valor padrão para a propriedade. Para definir valores mínimo e máximo, "
                      "use o formato: valor, valor, valor")
ANN_PROPERTY_CALLBACK = ("Usar a string de comando como o corpo de uma função de retorno de chamada para todas as "
                         "propriedades com sua opção de atualização definida")
ANN_SELECT_GROUP = "Selecionar um grupo"
ANN_SET_COLUMNS = "O número de botões em uma linha"
ANN_SET_NAME = "O nome do conjunto de botões"
ANN_TOGGLE_ADDON = "Criar um botão para ativar ou desativar um add-on"
ANN_TOOL = "O comando da ferramenta a ser editado"
ANN_TOOLTIP = "A dica de ferramenta para o botão"

# ----------------------------------------------------------------------
# Info
# ----------------------------------------------------------------------


# ----------------------------------------------------------------------
# Warning/Error
# ----------------------------------------------------------------------

WARNING_ADDON_INCOMPATIBLE = "O add-on é incompatível e deve ser ativado/desativado nas preferências: "
WARNING_ADDON_MISSING = "Um add-on com este nome não existe: "
WARNING_BRACKETS_INCOMPLETE = "Os parênteses das propriedades estão incompletos"
WARNING_GROUP_NAME_EXISTS = "O nome do grupo já existe"
WARNING_IMAGE_MISSING = "A imagem não existe no caminho: "
WARNING_LABEL_COMMAND_MISMATCH = "A quantidade de rótulos e comandos de ferramenta não coincide"
WARNING_NO_GROUP_SELECTED = "Nenhum grupo selecionado"
WARNING_NO_NAME = "Nenhum nome definido"
WARNING_NO_TEXT_EDITOR = "Não há um editor de texto aberto para obter o comando da ferramenta"
WARNING_NO_TEXT_EDITOR_TO_VIEW = "Não há um editor de texto aberto para ver o comando"
WARNING_NO_TOOL_IN_GROUP = "Não existe uma ferramenta no grupo selecionado"
WARNING_NO_TOOL_SELECTED = "Nenhuma ferramenta selecionada"
WARNING_PROPERTY_NAME_MISSING = "Falta o nome de uma propriedade e/ou valor padrão"
WARNING_PROPERTY_VALUE_MISMATCH = "A quantidade de propriedades e valores não coincide"
WARNING_SELECT_CONFIG = "Selecione um arquivo de configuração válido"
WARNING_SELECT_TO_IMPORT = "Selecione um grupo ou ferramenta para importar"
WARNING_TOOL_EXISTS_IN_GROUP = "O nome da ferramenta já existe no grupo"
