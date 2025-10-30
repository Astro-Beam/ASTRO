FROM dorowu/ubuntu-desktop-lxde-vnc:focal

USER root
# Fix Chrome repo key so apt works
RUN rm -f /etc/apt/sources.list.d/google-chrome.list || true \
    && rm -f /etc/apt/trusted.gpg.d/google-chrome.gpg || true

# Python + PyQt5 (apt) + GNU Radio + osmosdr + X11/Qt libs
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip python3-tk python3-dev build-essential \
    python3-pyqt5 python3-pyqt5.qtwebengine \
    gnuradio gnuradio-dev gr-osmosdr rtl-sdr \
    libx11-xcb1 libxcb1 libxcb-render0 libxcb-shm0 libxcb-xfixes0 \
    libxcb-cursor0 libxcb-randr0 libxcb-shape0 libxcb-util1 \
    libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-render-util0 \
    libxkbcommon0 libxkbcommon-x11-0 libfontconfig1 libfreetype6 \
    libglu1-mesa libgl1-mesa-glx x11-apps dbus-x11 \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/app
COPY requirements.txt /opt/app/requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt || true

COPY . /opt/app

COPY start.sh /usr/local/bin/start_app.sh
COPY launch_app.sh /usr/local/bin/launch_app.sh
RUN chmod +x /usr/local/bin/launch_app.sh
COPY app-supervisord.conf /etc/supervisor/conf.d/beam_app.conf
COPY launch_app.sh /usr/local/bin/launch_app.sh
RUN chmod +x /usr/local/bin/launch_app.sh
COPY app-supervisord.conf /etc/supervisor/conf.d/beam_app.conf
RUN chmod +x /usr/local/bin/start_app.sh

# noVNC on port 80 in this image
EXPOSE 80 5901
CMD ["/usr/local/bin/start_app.sh"]
