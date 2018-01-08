# -*- coding: utf-8 -*-

class Const:

    # GNU global コマンド.
    CMD_GLOBAL = 'global'

    # 対象ファイル名パターン(global -P の出力をフィルタ)
    TARGET_FNAME_PATTERN = r'.*\.(c|cc|cpp|cxx|c\+\+|java)$'

    # ソースファイルのエンコーディング
    SOURCE_ENCODING = 'utf-8'

    # 定義内の参照数最小値(これ未満は処理対象外)
    MIN_REFS_PER_DEF = 0

    # 統合するシンボル長(これ以下は UNIFIED_SYM_WORD に置換).
    UNIFIED_SYM_LENGTH = 2

    # 統合対象シンボルのワード.
    UNIFIED_SYM_WORD = '0_'

    # クラスタリング結果から抽出するクラスタ数(default).
    DEFAULT_NUM_OF_CLUSTERS = 10

    # (DEPRECATED)クラスタリング結果から抽出する linkage 数.
    DEFAULT_NUM_OF_LINKAGES = None

    # ラベル内フィールドの区切り文字.
    LABEL_FIELD_DELIMITER = '\t'

    # 文書内ワードの区切り文字.
    DOC_WORD_DELIMITER = ' '

    # デフォルト出力ディレクトリ.
    RESULT_DIR = './__analysis_result'

    # 処理対象ソースファイルリストのファイル名.
    TARGET_LIST_FNAME = 'target_list.txt'

    # タグファイル名(定義: global -f -d の出力)
    TAGS_DEF_FNAME = 'tags_def.txt'
    # タグファイル名(参照: global -f -r の出力)
    TAGS_REF_FNAME = 'tags_ref.txt'
    # タグファイル名(シンボル: global -f -s の出力)
    TAGS_SYM_FNAME = 'tags_sym.txt'

    # 文書集合ファイル名.
    DOCS_FNAME = 'docs.txt'
    # 文書集合のラベルファイル.
    LABELS_FNAME = 'labels.txt'

    # 文書集合生成時のデバグ出力ファイル名.
    DEBUG_FUNCS_FNAME = 'debug_funcs.txt'

    # ID MAP ファイル名.
    ID_MAP_FNAME = 'id_map.txt'

    # linkage_mat ファイル名.
    LINKAGE_MAT_FNAME = 'linkage_mat.csv'
    # linkage_mat ファイルの区切り文字.
    LINKAGE_MAT_DELIMITER = ','

    # 樹形図ファイル名.
    DENDROGRAM_FNAME = 'dendrogram.png'

    # 類似関数情報 pickleファイル名.
    SIMILAR_PKL_FNAME = 'similar.pkl'
    # 類似関数情報TEXTファイル名.
    SIMILAR_TEXT_FNAME = 'similar.txt'
    # 類似関数情報HTMLファイル名.
    SIMILAR_HTML_FNAME = 'similar.html'

    # HTML出力サブディレクトリ.
    HTML_SUB_DIR = 'html'
