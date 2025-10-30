#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Radiometer
# GNU Radio version: 3.10.12.0

from PyQt5 import Qt
from gnuradio import qtgui
from PyQt5.QtCore import QObject, pyqtSlot
from datetime import datetime
from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import filter
from gnuradio import gr
from gnuradio.filter import firdes
from gnuradio.fft import window
import sys
import signal
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
import osmosdr
import time
import pmt
import radiometer_Metadata_Writer_Start as Metadata_Writer_Start  # embedded python block
import sip # type: ignore
import threading


def snipfcn_Metadata_Writer_End(self):
    end_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = self.Metadata_Writer_Start.filename

    with open(filename, 'a') as f:
        f.write(f"Observation End: {end_time}\n")

    print(f"[INFO] Observation end time appended to: {filename}")


def snippets_main_after_stop(tb):
    snipfcn_Metadata_Writer_End(tb)

class radiometer(gr.top_block, Qt.QWidget):

    def __init__(self,
                 samp_rate,
                 rfgain,
                 ifgain,
                 bbgain,
                 restFreq,
                 receiver,
                 output_filename,
                 observationType,
                 observationRA,
                 observationDec,
                 observationObject,
                 integrationTimeShort=0.5,
                 integrationTimeLong=5,
                 freq=1.45e9,
                 dc_gain=1e5,
                 calibration_select=0,
                 T_hot=300,
                 T_cold=10,
                 P_hot=64,
                 P_cold=33):
        gr.top_block.__init__(self, "Radiometer", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Radiometer")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except BaseException as exc:
            print(f"Qt GUI: Could not set Icon: {str(exc)}", file=sys.stderr)
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("gnuradio/flowgraphs", "radiometer")

        try:
            geometry = self.settings.value("geometry")
            if geometry:
                self.restoreGeometry(geometry)
        except BaseException as exc:
            print(f"Qt GUI: Could not restore geometry: {str(exc)}", file=sys.stderr)
        self.flowgraph_started = threading.Event()

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate
        self.rfgain = rfgain
        self.ifgain = ifgain
        self.bbgain = bbgain
        self.vec_length = vec_length = 1024
        self.restFreq = restFreq
        self.receiver = receiver
        self.output_filename = output_filename
        self.observationType = observationType
        self.observationRA = observationRA
        self.observationObject = observationObject
        self.observationDec = observationDec
        self.intermediate_rate = intermediate_rate = 1e3
        self.integration_select = integration_select = 0
        self.integrationTimeShort = integrationTimeShort = .5
        self.integrationTimeLong = integrationTimeLong = 5
        self.freq = freq
        self.file_select = file_select = 1
        self.file_rate = file_rate = 1
        self.file = file = str(rfgain)+'_'+str(ifgain)+'_'+str(bbgain)+'G'+str(samp_rate/10e5)+'MHz.dat'
        self.dire = dire = '/home/georkeso/observations/Radiometer/'
        self.dc_gain = dc_gain
        self.date = date = 'Sun300625/'
        self.calibration_select = calibration_select = 0
        self.T_hot = T_hot
        self.T_cold = T_cold
        self.P_hot = P_hot
        self.P_cold = P_cold

        ##################################################
        # Blocks
        ##################################################

        # Create the options list
        self._integration_select_options = [0, 1]
        # Create the labels list
        self._integration_select_labels = ['Short Integration', 'Long Integration']
        # Create the combo box
        self._integration_select_tool_bar = Qt.QToolBar(self)
        self._integration_select_tool_bar.addWidget(Qt.QLabel("Integration Time" + ": "))
        self._integration_select_combo_box = Qt.QComboBox()
        self._integration_select_tool_bar.addWidget(self._integration_select_combo_box)
        for _label in self._integration_select_labels: self._integration_select_combo_box.addItem(_label)
        self._integration_select_callback = lambda i: Qt.QMetaObject.invokeMethod(self._integration_select_combo_box, "setCurrentIndex", Qt.Q_ARG("int", self._integration_select_options.index(i)))
        self._integration_select_callback(self.integration_select)
        self._integration_select_combo_box.currentIndexChanged.connect(
            lambda i: self.set_integration_select(self._integration_select_options[i]))
        # Create the radio buttons
        self.top_layout.addWidget(self._integration_select_tool_bar)
        self._dc_gain_tool_bar = Qt.QToolBar(self)
        self._dc_gain_tool_bar.addWidget(Qt.QLabel("DC Gain" + ": "))
        self._dc_gain_line_edit = Qt.QLineEdit(str(self.dc_gain))
        self._dc_gain_tool_bar.addWidget(self._dc_gain_line_edit)
        self._dc_gain_line_edit.editingFinished.connect(
            lambda: self.set_dc_gain(eng_notation.str_to_num(str(self._dc_gain_line_edit.text()))))
        self.top_layout.addWidget(self._dc_gain_tool_bar)
        # Create the options list
        self._calibration_select_options = [0, 1]
        # Create the labels list
        self._calibration_select_labels = ['Without Calibration', 'With Calibration']
        # Create the combo box
        self._calibration_select_tool_bar = Qt.QToolBar(self)
        self._calibration_select_tool_bar.addWidget(Qt.QLabel("Calibration" + ": "))
        self._calibration_select_combo_box = Qt.QComboBox()
        self._calibration_select_tool_bar.addWidget(self._calibration_select_combo_box)
        for _label in self._calibration_select_labels: self._calibration_select_combo_box.addItem(_label)
        self._calibration_select_callback = lambda i: Qt.QMetaObject.invokeMethod(self._calibration_select_combo_box, "setCurrentIndex", Qt.Q_ARG("int", self._calibration_select_options.index(i)))
        self._calibration_select_callback(self.calibration_select)
        self._calibration_select_combo_box.currentIndexChanged.connect(
            lambda i: self.set_calibration_select(self._calibration_select_options[i]))
        # Create the radio buttons
        self.top_layout.addWidget(self._calibration_select_tool_bar)
        self._P_hot_tool_bar = Qt.QToolBar(self)
        self._P_hot_tool_bar.addWidget(Qt.QLabel("Hot Pw" + ": "))
        self._P_hot_line_edit = Qt.QLineEdit(str(self.P_hot))
        self._P_hot_tool_bar.addWidget(self._P_hot_line_edit)
        self._P_hot_line_edit.editingFinished.connect(
            lambda: self.set_P_hot(int(str(self._P_hot_line_edit.text()))))
        self.top_layout.addWidget(self._P_hot_tool_bar)
        self._P_cold_tool_bar = Qt.QToolBar(self)
        self._P_cold_tool_bar.addWidget(Qt.QLabel("Cold Pw" + ": "))
        self._P_cold_line_edit = Qt.QLineEdit(str(self.P_cold))
        self._P_cold_tool_bar.addWidget(self._P_cold_line_edit)
        self._P_cold_line_edit.editingFinished.connect(
            lambda: self.set_P_cold(int(str(self._P_cold_line_edit.text()))))
        self.top_layout.addWidget(self._P_cold_tool_bar)
        self.single_pole_iir_filter_xx_0_0 = filter.single_pole_iir_filter_ff((1/(samp_rate*integrationTimeLong)), 1)
        self.single_pole_iir_filter_xx_0 = filter.single_pole_iir_filter_ff((1/(samp_rate*integrationTimeShort)), 1)
        self.radiometer_1 = qtgui.number_sink(
            gr.sizeof_float,
            0,
            qtgui.NUM_GRAPH_NONE,
            1,
            None # parent
        )
        self.radiometer_1.set_update_time(0.10)
        self.radiometer_1.set_title("Radiometer")

        labels = ['Value', '', '', '', '',
            '', '', '', '', '']
        units = ['', '', '', '', '',
            '', '', '', '', '']
        colors = [("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"),
            ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black")]
        factor = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]

        for i in range(1):
            self.radiometer_1.set_min(i, -1)
            self.radiometer_1.set_max(i, 1)
            self.radiometer_1.set_color(i, colors[i][0], colors[i][1])
            if len(labels[i]) == 0:
                self.radiometer_1.set_label(i, "Data {0}".format(i))
            else:
                self.radiometer_1.set_label(i, labels[i])
            self.radiometer_1.set_unit(i, units[i])
            self.radiometer_1.set_factor(i, factor[i])

        self.radiometer_1.enable_autoscale(False)
        self._radiometer_1_win = sip.wrapinstance(self.radiometer_1.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._radiometer_1_win)
        self.qtgui_time_sink_x_0 = qtgui.time_sink_f(
            (1024*1), #size
            intermediate_rate, #samp_rate
            "", #name
            1, #number of inputs
            None # parent
        )
        self.qtgui_time_sink_x_0.set_update_time(0.10)
        self.qtgui_time_sink_x_0.set_y_axis(-1, 100)

        self.qtgui_time_sink_x_0.set_y_label('Total Power', "")

        self.qtgui_time_sink_x_0.enable_tags(True)
        self.qtgui_time_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.qtgui_time_sink_x_0.enable_autoscale(True)
        self.qtgui_time_sink_x_0.enable_grid(False)
        self.qtgui_time_sink_x_0.enable_axis_labels(True)
        self.qtgui_time_sink_x_0.enable_control_panel(False)
        self.qtgui_time_sink_x_0.enable_stem_plot(False)


        labels = ['Signal 1', 'Signal 2', 'Signal 3', 'Signal 4', 'Signal 5',
            'Signal 6', 'Signal 7', 'Signal 8', 'Signal 9', 'Signal 10']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ['blue', 'red', 'green', 'black', 'cyan',
            'magenta', 'yellow', 'dark red', 'dark green', 'dark blue']
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]
        styles = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        markers = [-1, -1, -1, -1, -1,
            -1, -1, -1, -1, -1]


        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_time_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_time_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_0.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_0.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_0.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_0_win = sip.wrapinstance(self.qtgui_time_sink_x_0.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_time_sink_x_0_win)
        self.qtgui_histogram_sink_x_0 = qtgui.histogram_sink_f(
            1024,
            10,
            (-0.05),
            0.05,
            "System Heartbeat",
            1,
            None # parent
        )

        self.qtgui_histogram_sink_x_0.set_update_time(0.10)
        self.qtgui_histogram_sink_x_0.enable_autoscale(True)
        self.qtgui_histogram_sink_x_0.enable_accumulate(False)
        self.qtgui_histogram_sink_x_0.enable_grid(False)
        self.qtgui_histogram_sink_x_0.enable_axis_labels(True)


        labels = ['', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        styles = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        markers= [-1, -1, -1, -1, -1,
            -1, -1, -1, -1, -1]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_histogram_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_histogram_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_histogram_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_histogram_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_histogram_sink_x_0.set_line_style(i, styles[i])
            self.qtgui_histogram_sink_x_0.set_line_marker(i, markers[i])
            self.qtgui_histogram_sink_x_0.set_line_alpha(i, alphas[i])

        self._qtgui_histogram_sink_x_0_win = sip.wrapinstance(self.qtgui_histogram_sink_x_0.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_histogram_sink_x_0_win)
        self.osmosdr_source_0 = osmosdr.source(
            args="numchan=" + str(1) + " " + "bladerf"
        )
        self.osmosdr_source_0.set_time_source('gpsdo', 0)
        self.osmosdr_source_0.set_sample_rate(samp_rate)
        self.osmosdr_source_0.set_center_freq(freq, 0)
        self.osmosdr_source_0.set_freq_corr(0, 0)
        self.osmosdr_source_0.set_dc_offset_mode(0, 0)
        self.osmosdr_source_0.set_iq_balance_mode(0, 0)
        self.osmosdr_source_0.set_gain_mode(False, 0)
        self.osmosdr_source_0.set_gain(rfgain, 0)
        self.osmosdr_source_0.set_if_gain(ifgain, 0)
        self.osmosdr_source_0.set_bb_gain(bbgain, 0)
        self.osmosdr_source_0.set_antenna('', 0)
        self.osmosdr_source_0.set_bandwidth(0, 0)
        # Create the options list
        self._file_select_options = [0, 1]
        # Create the labels list
        self._file_select_labels = ['With Backup', 'Without Backup']
        # Create the combo box
        self._file_select_tool_bar = Qt.QToolBar(self)
        self._file_select_tool_bar.addWidget(Qt.QLabel("Backup" + ": "))
        self._file_select_combo_box = Qt.QComboBox()
        self._file_select_tool_bar.addWidget(self._file_select_combo_box)
        for _label in self._file_select_labels: self._file_select_combo_box.addItem(_label)
        self._file_select_callback = lambda i: Qt.QMetaObject.invokeMethod(self._file_select_combo_box, "setCurrentIndex", Qt.Q_ARG("int", self._file_select_options.index(i)))
        self._file_select_callback(self.file_select)
        self._file_select_combo_box.currentIndexChanged.connect(
            lambda i: self.set_file_select(self._file_select_options[i]))
        # Create the radio buttons
        self.top_layout.addWidget(self._file_select_tool_bar)
        self.blocks_selector_0_0 = blocks.selector(gr.sizeof_float*1,calibration_select,0)
        self.blocks_selector_0_0.set_enabled(True)
        self.blocks_selector_0 = blocks.selector(gr.sizeof_float*1,integration_select,0)
        self.blocks_selector_0.set_enabled(True)
        self.blocks_multiply_const_vxx_0_1 = blocks.multiply_const_ff(dc_gain)
        self.blocks_multiply_const_vxx_0_0 = blocks.multiply_const_ff(((T_hot - T_cold)/(P_hot - P_cold)))
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_ff(dc_gain)
        self.blocks_moving_average_xx_0 = blocks.moving_average_ff(int(intermediate_rate), (1e-3), 1000, 1)
        self.blocks_keep_one_in_n_1 = blocks.keep_one_in_n(gr.sizeof_float*1, (int(intermediate_rate/file_rate)))
        self.blocks_keep_one_in_n_0 = blocks.keep_one_in_n(gr.sizeof_float*1, (int(samp_rate/intermediate_rate)))
        self.blocks_file_sink_0_1_1_0 = blocks.file_sink(gr.sizeof_float*1, 'dire+date+observation+file', True)
        self.blocks_file_sink_0_1_1_0.set_unbuffered(False)
        self.blocks_file_sink_0_1_1 = blocks.file_sink(gr.sizeof_float*1, "dire+date+observation+'IIR'+file", True)
        self.blocks_file_sink_0_1_1.set_unbuffered(False)
        self.blocks_complex_to_real_0 = blocks.complex_to_real(1)
        self.blocks_complex_to_mag_squared_0 = blocks.complex_to_mag_squared(1)
        self.blocks_add_const_vxx_0 = blocks.add_const_ff((T_cold - ((T_hot - T_cold)/(P_hot - P_cold) * P_cold)))
        self.Metadata_Writer_Start = Metadata_Writer_Start.blk(
            object_name=self.observationObject,
            observation_type=self.observationType,
            rest_freq=self.restFreq,
            bandwidth=self.samp_rate,
            ra=self.observationRA,
            dec=self.observationDec,
            integration_time=self.integrationTimeShort,
            receiver=self.receiver,
            rf_gain=self.rfgain,
            if_gain=self.ifgain,
            bb_gain=self.bbgain
        )

        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_add_const_vxx_0, 0), (self.blocks_selector_0_0, 1))
        self.connect((self.blocks_complex_to_mag_squared_0, 0), (self.single_pole_iir_filter_xx_0, 0))
        self.connect((self.blocks_complex_to_mag_squared_0, 0), (self.single_pole_iir_filter_xx_0_0, 0))
        self.connect((self.blocks_complex_to_real_0, 0), (self.qtgui_histogram_sink_x_0, 0))
        self.connect((self.blocks_keep_one_in_n_0, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.blocks_keep_one_in_n_1, 0), (self.blocks_file_sink_0_1_1_0, 0))
        self.connect((self.blocks_keep_one_in_n_1, 0), (self.qtgui_time_sink_x_0, 0))
        self.connect((self.blocks_moving_average_xx_0, 0), (self.blocks_keep_one_in_n_1, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.blocks_multiply_const_vxx_0_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.blocks_selector_0_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0_0, 0), (self.blocks_add_const_vxx_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0_1, 0), (self.radiometer_1, 0))
        self.connect((self.blocks_selector_0, 0), (self.blocks_keep_one_in_n_0, 0))
        self.connect((self.blocks_selector_0, 0), (self.blocks_multiply_const_vxx_0_1, 0))
        self.connect((self.blocks_selector_0_0, 0), (self.blocks_file_sink_0_1_1, 0))
        self.connect((self.blocks_selector_0_0, 0), (self.blocks_moving_average_xx_0, 0))
        self.connect((self.osmosdr_source_0, 0), (self.blocks_complex_to_mag_squared_0, 0))
        self.connect((self.osmosdr_source_0, 0), (self.blocks_complex_to_real_0, 0))
        self.connect((self.single_pole_iir_filter_xx_0, 0), (self.blocks_selector_0, 0))
        self.connect((self.single_pole_iir_filter_xx_0_0, 0), (self.blocks_selector_0, 1))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("gnuradio/flowgraphs", "radiometer")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()
        snippets_main_after_stop(self)
        event.accept()

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.set_file(str(self.rfgain)+'_'+str(self.ifgain)+'_'+str(self.bbgain)+'G'+str(self.samp_rate/10e5)+'MHz.dat')
        self.Metadata_Writer_Start.bandwidth = self.samp_rate
        self.blocks_keep_one_in_n_0.set_n((int(self.samp_rate/self.intermediate_rate)))
        self.osmosdr_source_0.set_sample_rate(self.samp_rate)
        self.single_pole_iir_filter_xx_0.set_taps((1/(self.samp_rate*self.integrationTimeShort)))
        self.single_pole_iir_filter_xx_0_0.set_taps((1/(self.samp_rate*self.integrationTimeLong)))

    def get_rfgain(self):
        return self.rfgain

    def set_rfgain(self, rfgain):
        self.rfgain = rfgain
        self.set_file(str(self.rfgain)+'_'+str(self.ifgain)+'_'+str(self.bbgain)+'G'+str(self.samp_rate/10e5)+'MHz.dat')
        self.Metadata_Writer_Start.rf_gain = self.rfgain
        self.osmosdr_source_0.set_gain(self.rfgain, 0)

    def get_ifgain(self):
        return self.ifgain

    def set_ifgain(self, ifgain):
        self.ifgain = ifgain
        self.set_file(str(self.rfgain)+'_'+str(self.ifgain)+'_'+str(self.bbgain)+'G'+str(self.samp_rate/10e5)+'MHz.dat')
        self.Metadata_Writer_Start.if_gain = self.ifgain
        self.osmosdr_source_0.set_if_gain(self.ifgain, 0)

    def get_bbgain(self):
        return self.bbgain

    def set_bbgain(self, bbgain):
        self.bbgain = bbgain
        self.set_file(str(self.rfgain)+'_'+str(self.ifgain)+'_'+str(self.bbgain)+'G'+str(self.samp_rate/10e5)+'MHz.dat')
        self.Metadata_Writer_Start.bb_gain = self.bbgain
        self.osmosdr_source_0.set_bb_gain(self.bbgain, 0)

    def get_vec_length(self):
        return self.vec_length

    def set_vec_length(self, vec_length):
        self.vec_length = vec_length

    def get_restFreq(self):
        return self.restFreq

    def set_restFreq(self, restFreq):
        self.restFreq = restFreq
        self.Metadata_Writer_Start.rest_freq = self.restFreq

    def get_receiver(self):
        return self.receiver

    def set_receiver(self, receiver):
        self.receiver = receiver
        self.Metadata_Writer_Start.receiver = self.receiver

    def get_output_filename(self):
        return self.output_filename

    def set_output_filename(self, output_filename):
        self.output_filename = output_filename

    def get_observationType(self):
        return self.observationType

    def set_observationType(self, observationType):
        self.observationType = observationType
        self.Metadata_Writer_Start.observation_type = self.observationType

    def get_observationRA(self):
        return self.observationRA

    def set_observationRA(self, observationRA):
        self.observationRA = observationRA
        self.Metadata_Writer_Start.ra = self.observationRA

    def get_observationObject(self):
        return self.observationObject

    def set_observationObject(self, observationObject):
        self.observationObject = observationObject
        self.Metadata_Writer_Start.object_name = self.observationObject

    def get_observationDec(self):
        return self.observationDec

    def set_observationDec(self, observationDec):
        self.observationDec = observationDec
        self.Metadata_Writer_Start.dec = self.observationDec

    def get_intermediate_rate(self):
        return self.intermediate_rate

    def set_intermediate_rate(self, intermediate_rate):
        self.intermediate_rate = intermediate_rate
        self.blocks_keep_one_in_n_0.set_n((int(self.samp_rate/self.intermediate_rate)))
        self.blocks_keep_one_in_n_1.set_n((int(self.intermediate_rate/self.file_rate)))
        self.blocks_moving_average_xx_0.set_length_and_scale(int(self.intermediate_rate), (1e-3))
        self.qtgui_time_sink_x_0.set_samp_rate(self.intermediate_rate)

    def get_integration_select(self):
        return self.integration_select

    def set_integration_select(self, integration_select):
        self.integration_select = integration_select
        self._integration_select_callback(self.integration_select)
        self.blocks_selector_0.set_input_index(self.integration_select)

    def get_integrationTimeShort(self):
        return self.integrationTimeShort

    def set_integrationTimeShort(self, integrationTimeShort):
        self.integrationTimeShort = integrationTimeShort
        self.Metadata_Writer_Start.integration_time = self.integrationTimeShort
        self.single_pole_iir_filter_xx_0.set_taps((1/(self.samp_rate*self.integrationTimeShort)))

    def get_integrationTimeLong(self):
        return self.integrationTimeLong

    def set_integrationTimeLong(self, integrationTimeLong):
        self.integrationTimeLong = integrationTimeLong
        self.single_pole_iir_filter_xx_0_0.set_taps((1/(self.samp_rate*self.integrationTimeLong)))

    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        self.freq = freq
        self.osmosdr_source_0.set_center_freq(self.freq, 0)

    def get_file_select(self):
        return self.file_select

    def set_file_select(self, file_select):
        self.file_select = file_select
        self._file_select_callback(self.file_select)

    def get_file_rate(self):
        return self.file_rate

    def set_file_rate(self, file_rate):
        self.file_rate = file_rate
        self.blocks_keep_one_in_n_1.set_n((int(self.intermediate_rate/self.file_rate)))

    def get_file(self):
        return self.file

    def set_file(self, file):
        self.file = file

    def get_dire(self):
        return self.dire

    def set_dire(self, dire):
        self.dire = dire

    def get_dc_gain(self):
        return self.dc_gain

    def set_dc_gain(self, dc_gain):
        self.dc_gain = dc_gain
        Qt.QMetaObject.invokeMethod(self._dc_gain_line_edit, "setText", Qt.Q_ARG("QString", eng_notation.num_to_str(self.dc_gain)))
        self.blocks_multiply_const_vxx_0.set_k(self.dc_gain)
        self.blocks_multiply_const_vxx_0_1.set_k(self.dc_gain)

    def get_date(self):
        return self.date

    def set_date(self, date):
        self.date = date

    def get_calibration_select(self):
        return self.calibration_select

    def set_calibration_select(self, calibration_select):
        self.calibration_select = calibration_select
        self._calibration_select_callback(self.calibration_select)
        self.blocks_selector_0_0.set_input_index(self.calibration_select)

    def get_T_hot(self):
        return self.T_hot

    def set_T_hot(self, T_hot):
        self.T_hot = T_hot
        self.blocks_add_const_vxx_0.set_k((self.T_cold - ((self.T_hot - self.T_cold)/(self.P_hot - self.P_cold) * self.P_cold)))
        self.blocks_multiply_const_vxx_0_0.set_k(((self.T_hot - self.T_cold)/(self.P_hot - self.P_cold)))

    def get_T_cold(self):
        return self.T_cold

    def set_T_cold(self, T_cold):
        self.T_cold = T_cold
        self.blocks_add_const_vxx_0.set_k((self.T_cold - ((self.T_hot - self.T_cold)/(self.P_hot - self.P_cold) * self.P_cold)))
        self.blocks_multiply_const_vxx_0_0.set_k(((self.T_hot - self.T_cold)/(self.P_hot - self.P_cold)))

    def get_P_hot(self):
        return self.P_hot

    def set_P_hot(self, P_hot):
        self.P_hot = P_hot
        Qt.QMetaObject.invokeMethod(self._P_hot_line_edit, "setText", Qt.Q_ARG("QString", str(self.P_hot)))
        self.blocks_add_const_vxx_0.set_k((self.T_cold - ((self.T_hot - self.T_cold)/(self.P_hot - self.P_cold) * self.P_cold)))
        self.blocks_multiply_const_vxx_0_0.set_k(((self.T_hot - self.T_cold)/(self.P_hot - self.P_cold)))

    def get_P_cold(self):
        return self.P_cold

    def set_P_cold(self, P_cold):
        self.P_cold = P_cold
        Qt.QMetaObject.invokeMethod(self._P_cold_line_edit, "setText", Qt.Q_ARG("QString", str(self.P_cold)))
        self.blocks_add_const_vxx_0.set_k((self.T_cold - ((self.T_hot - self.T_cold)/(self.P_hot - self.P_cold) * self.P_cold)))
        self.blocks_multiply_const_vxx_0_0.set_k(((self.T_hot - self.T_cold)/(self.P_hot - self.P_cold)))




def main(top_block_cls=radiometer, options=None):

    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()

    tb.start()
    tb.flowgraph_started.set()

    tb.show()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()
        snippets_main_after_stop(tb)
        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    qapp.exec_()

if __name__ == '__main__':
    main()
