#!/usr/bin/env bash
# wait for the virtual display :1
for i in {1..30}; do
  [ -S /tmp/.X11-unix/X1 ] && break
  sleep 1
done
mkdir -p /tmp/runtime-root && chmod 700 /tmp/runtime-root

export XDG_RUNTIME_DIR=/tmp/runtime-root
export DISPLAY=:1
export QT_QPA_PLATFORM=xcb
export QT_X11_NO_MITSHM=1
export LIBGL_ALWAYS_INDIRECT=1
export QTWEBENGINE_DISABLE_SANDBOX=1
export PYTHONUNBUFFERED=1

cd /opt/app || exit 1
exec python3 -u main.py
