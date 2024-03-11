#!/bin/bash
set -e
set -o pipefail

make -C doc dist LATEXMKOPTS=-halt-on-error SPHINXOPTS=-T 2>&1 | tee doc-log.txt

affected_doc_warnings() {
    files=$(git diff --name-only origin/master...HEAD)
    # Look for sphinx warnings only in files affected by the PR
    if [ -n "$files" ]
    then
        for af in ${files[@]}
        do
          warn+=`grep WARNING doc-log.txt | grep $af`
        done
    fi
    echo "$warn"
}

echo "The following documentation warnings have been generated:"
warnings=$(affected_doc_warnings)
if [ -z "$warnings" ]
then
    warnings="no warnings"
fi
echo "$warnings"
