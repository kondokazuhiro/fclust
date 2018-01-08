#!/bin/sh

if [ $# -ne 2 ]; then
    echo "usage: $0 target_src_dir result_dir" 1>&2
    exit 1
fi

# target source dir.
FCLS_TARGET=$1
# result dir.
FCLS_RESULT=$2

# this script dir.
FCLS_HOME=${FCLS_HOME-$(dirname $0)}
FCLS_SCRIPT=${FCLS_SCRIPT-$FCLS_HOME/script}

_err() {
    echo "failed." 1>&2
    exit 1
}


echo "(0) run gtags in $FCLS_TARGET"
(cd "$FCLS_TARGET" && gtags) || _err

echo "(1) make target source file list."
python "$FCLS_SCRIPT/gl_target_list.py" "$FCLS_TARGET" -o "$FCLS_RESULT" || _err

echo "(2) extract tags(definitions, references, symbols)"
python "$FCLS_SCRIPT/gl_extract_tags.py" "$FCLS_TARGET" -o "$FCLS_RESULT" || _err

echo "(3) make document-set from extracted tags."
python "$FCLS_SCRIPT/tags_to_docs.py" --by-file -o "$FCLS_RESULT" || _err

echo "(4-1) doc2vec training"
python "$FCLS_SCRIPT/doc2vec_train.py" -o "$FCLS_RESULT" || _err

echo "(4-2) doc2vec clustering"
python "$FCLS_SCRIPT/doc2vec_cluster.py" -o "$FCLS_RESULT" || _err

echo "make a dendrogram image (optional)."
python "$FCLS_SCRIPT/dendrogram.py" -o "$FCLS_RESULT"

echo "(5) resolve similar functions/definitions."
python "$FCLS_SCRIPT/resolve_similar.py" -o "$FCLS_RESULT" || _err

echo "(6) make html."
python "$FCLS_SCRIPT/make_html.py" -s "$FCLS_TARGET" -o "$FCLS_RESULT" || _err


echo 'successful.'
