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

echo "(4) modify words."
python "$FCLS_SCRIPT/modify_words.py" -o "$FCLS_RESULT" || _err

echo "(5) LDA."
python "$FCLS_SCRIPT/lda_work.py" --with-ldavis -o "$FCLS_RESULT" || _err


echo 'successful.'
