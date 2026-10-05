#!/bin/bash
cd "$(dirname "$0")" || exit 1

pick_python() {
  local c
  local list=(
    /usr/local/bin/python3
    /opt/homebrew/bin/python3
  )
  shopt -s nullglob
  list+=(/Library/Frameworks/Python.framework/Versions/*/bin/python3)
  list+=("$HOME"/Library/Frameworks/Python.framework/Versions/*/bin/python3)
  if command -v python3 >/dev/null 2>&1; then
    list+=("$(command -v python3)")
  fi
  for c in "${list[@]}"; do
    [ -x "$c" ] || continue
    if "$c" -c "import tkinter" >/dev/null 2>&1; then
      echo "$c"
      return 0
    fi
  done
  return 1
}

PY="$(pick_python)" || {
  echo "Чтобы открыть ПВК, нужен Python 3 с tkinter."
  read -r
  exit 1
}
"$PY" -u main.py
code=$?
if [ "$code" -ne 0 ]; then
  echo
  echo "Окно не открылось, код $code"
  read -r
fi
exit "$code"
