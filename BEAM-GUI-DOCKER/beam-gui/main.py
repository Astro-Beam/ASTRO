from PyQt5 import QtWidgets, QtGui
import sys
import sun_radiometer


class ObservationApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Radiometer Control Panel")
        self.resize(400, 500)
        self.setWindowIcon(QtGui.QIcon("icon.ico"))

        layout = QtWidgets.QVBoxLayout(self)

        # --- Observation Parameters ---
        self.freqInput = QtWidgets.QLineEdit("1.45e9")
        self.freqInput.setToolTip("Center frequency in Hz (e.g., 1.42e9 for Hydrogen Line).")
        layout.addWidget(QtWidgets.QLabel("Center Frequency (Hz)"))
        layout.addWidget(self.freqInput)

        self.sampInput = QtWidgets.QLineEdit("10e6")
        self.sampInput.setToolTip("Number of samples per second (sampling rate).")
        layout.addWidget(QtWidgets.QLabel("Sample Rate"))
        layout.addWidget(self.sampInput)

        self.receiverInput = QtWidgets.QLineEdit("80cm Sun")
        self.receiverInput.setToolTip("Receiver name (e.g., 80cm Sun).")
        layout.addWidget(QtWidgets.QLabel("Receiver Name"))
        layout.addWidget(self.receiverInput)

        self.rfGainInput = QtWidgets.QLineEdit("20")
        self.rfGainInput.setToolTip("RF (Radio Frequency) Gain: adjusts the amplification of the antenna signal.")
        layout.addWidget(QtWidgets.QLabel("RF Gain"))
        layout.addWidget(self.rfGainInput)

        self.ifGainInput = QtWidgets.QLineEdit("10")
        self.ifGainInput.setToolTip("IF (Intermediate Frequency) Gain: controls gain in the down-converted stage.")
        layout.addWidget(QtWidgets.QLabel("IF Gain"))
        layout.addWidget(self.ifGainInput)

        self.bbGainInput = QtWidgets.QLineEdit("0")
        self.bbGainInput.setToolTip("BB (Baseband) Gain: sets gain at the lowest stage, before digitization.")
        layout.addWidget(QtWidgets.QLabel("BB Gain"))
        layout.addWidget(self.bbGainInput)

        self.obsTypeDropdown = QtWidgets.QComboBox()
        self.obsTypeDropdown.addItems(["Cold Calibration", "Hot Calibration", "Target Observation", ])
        self.obsTypeDropdown.setToolTip("Choose type of observation:\n"
                                        " - Cold Calibration: Ground background.\n"
                                        " - Hot Calibration: Sky background.\n"
                                        " - Target Observation: actual object.")
        layout.addWidget(QtWidgets.QLabel("Observation Type"))
        layout.addWidget(self.obsTypeDropdown)

        self.timeInputShort = QtWidgets.QLineEdit("0.5")
        self.timeInputShort.setToolTip("Integration time per sample in seconds (longer times reduce noise).")
        layout.addWidget(QtWidgets.QLabel("Short Integration Time (s)"))
        layout.addWidget(self.timeInputShort)

        self.timeInputLong = QtWidgets.QLineEdit("5")
        self.timeInputLong.setToolTip("Integration time per sample in seconds (longer times reduce noise).")
        layout.addWidget(QtWidgets.QLabel("Long Integration Time (s)"))
        layout.addWidget(self.timeInputLong)

        self.obsObjectInput = QtWidgets.QLineEdit("Sun")
        self.obsObjectInput.setToolTip("Name of the observed object (e.g. Sun, Moon).")
        layout.addWidget(QtWidgets.QLabel("Observation Object"))
        layout.addWidget(self.obsObjectInput)

        self.raInput = QtWidgets.QLineEdit("0.0")
        self.raInput.setToolTip("Right Ascension (RA) of target in degrees (celestial longitude).")
        layout.addWidget(QtWidgets.QLabel("RA (deg)"))
        layout.addWidget(self.raInput)

        self.decInput = QtWidgets.QLineEdit("0.0")
        self.decInput.setToolTip("Declination (Dec) of target in degrees (celestial latitude).")
        layout.addWidget(QtWidgets.QLabel("Dec (deg)"))
        layout.addWidget(self.decInput)

        self.filenameInput = QtWidgets.QLineEdit("observation.dat")
        self.filenameInput.setToolTip("Filename for saving recorded data (e.g. observation.dat).")
        layout.addWidget(QtWidgets.QLabel("Output Filename"))
        layout.addWidget(self.filenameInput)

        # --- Buttons ---
        self.startButton = QtWidgets.QPushButton("Start Observation")
        self.startButton.setToolTip("Start the radiometer observation with the chosen parameters.")
        self.stopButton = QtWidgets.QPushButton("Stop Observation")
        self.stopButton.setToolTip("Stop the ongoing observation safely.")
        layout.addWidget(self.startButton)
        layout.addWidget(self.stopButton)

        self.startButton.clicked.connect(self.start_observation)
        self.stopButton.clicked.connect(self.stop_observation)

        self.tb = None

        # --- Info Line ---
        info_layout = QtWidgets.QHBoxLayout()
        info_icon = QtWidgets.QLabel()
        info_icon.setPixmap(self.style().standardIcon(QtWidgets.QStyle.SP_MessageBoxInformation).pixmap(16, 16))
        info_text = QtWidgets.QLabel("Hover over the fields for extra info.")

        info_text.setStyleSheet("font-style: italic;")
        info_layout.addStretch()
        info_layout.addWidget(info_icon)
        info_layout.addWidget(info_text)
        info_layout.addStretch()

        layout.addLayout(info_layout)

    def start_observation(self):
        if self.tb is not None:
            QtWidgets.QMessageBox.warning(self, "Warning", "Observation already running!")
            return

        # Read GUI parameters
        freq = float(self.freqInput.text())
        sampRate = float(self.sampInput.text())
        receiverName = self.receiverInput.text()
        rf_gain = float(self.rfGainInput.text())
        if_gain = float(self.ifGainInput.text())
        bb_gain = float(self.bbGainInput.text())
        obs_type = self.obsTypeDropdown.currentText()
        integration_time_short = float(self.timeInputShort.text())
        integration_time_long = float(self.timeInputLong.text())
        obs_object = self.obsObjectInput.text()
        ra = float(self.raInput.text())
        dec = float(self.decInput.text())
        filename = self.filenameInput.text()

        # Instantiate flowgraph in main thread
        self.tb = sun_radiometer.radiometer(
            samp_rate=sampRate,
            rfgain=rf_gain,
            ifgain=if_gain,
            bbgain=bb_gain,
            restFreq=freq,
            receiver=receiverName,
            output_filename=filename,
            observationType=obs_type,
            observationRA=ra,
            observationDec=dec,
            observationObject=obs_object,
            integrationTimeShort=integration_time_short,
            integrationTimeLong=integration_time_long,
        )

        # Start flowgraph and show GUI
        self.tb.start()
        self.tb.show()

    def stop_observation(self):
        if self.tb is not None:
            self.tb.stop()
            self.tb.wait()
            self.tb = None

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon("icon.ico"))
    window = ObservationApp()
    window.show()
    sys.exit(app.exec_())