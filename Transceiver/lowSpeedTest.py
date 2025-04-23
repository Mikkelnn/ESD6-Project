#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: YoMama
# GNU Radio version: 3.10.12.0

from PyQt5 import Qt
from gnuradio import qtgui
from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import gr
from gnuradio.filter import firdes
from gnuradio.fft import window
import sys
import signal
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import uhd
import time
import threading



class lowSpeedTest(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "YoMama", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("YoMama")
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

        self.settings = Qt.QSettings("gnuradio/flowgraphs", "lowSpeedTest")

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
        self.variable_function_probe_3 = variable_function_probe_3 = 0
        self.variable_function_probe_2 = variable_function_probe_2 = 0
        self.variable_function_probe_1 = variable_function_probe_1 = 0
        self.variable_function_probe_0 = variable_function_probe_0 = 0
        self.variable_qtgui_label_3 = variable_qtgui_label_3 = variable_function_probe_3
        self.variable_qtgui_label_2 = variable_qtgui_label_2 = variable_function_probe_2
        self.variable_qtgui_label_1 = variable_qtgui_label_1 = variable_function_probe_1
        self.variable_qtgui_label_0 = variable_qtgui_label_0 = variable_function_probe_0
        self.samp_rate = samp_rate = 500000
        self.fc = fc = 5.8*10**9
        self.bw = bw = 10000

        ##################################################
        # Blocks
        ##################################################

        self.blocks_probe_signal_x_3 = blocks.probe_signal_vf(1)
        self.blocks_probe_signal_x_2 = blocks.probe_signal_vf(1)
        self.blocks_probe_signal_x_1 = blocks.probe_signal_vf(1)
        self.blocks_probe_signal_x_0 = blocks.probe_signal_f()
        self._variable_qtgui_label_3_tool_bar = Qt.QToolBar(self)

        if None:
            self._variable_qtgui_label_3_formatter = None
        else:
            self._variable_qtgui_label_3_formatter = lambda x: eng_notation.num_to_str(x)

        self._variable_qtgui_label_3_tool_bar.addWidget(Qt.QLabel("Rx4  "))
        self._variable_qtgui_label_3_label = Qt.QLabel(str(self._variable_qtgui_label_3_formatter(self.variable_qtgui_label_3)))
        self._variable_qtgui_label_3_tool_bar.addWidget(self._variable_qtgui_label_3_label)
        self.top_layout.addWidget(self._variable_qtgui_label_3_tool_bar)
        self._variable_qtgui_label_2_tool_bar = Qt.QToolBar(self)

        if None:
            self._variable_qtgui_label_2_formatter = None
        else:
            self._variable_qtgui_label_2_formatter = lambda x: eng_notation.num_to_str(x)

        self._variable_qtgui_label_2_tool_bar.addWidget(Qt.QLabel("Rx3  "))
        self._variable_qtgui_label_2_label = Qt.QLabel(str(self._variable_qtgui_label_2_formatter(self.variable_qtgui_label_2)))
        self._variable_qtgui_label_2_tool_bar.addWidget(self._variable_qtgui_label_2_label)
        self.top_layout.addWidget(self._variable_qtgui_label_2_tool_bar)
        self._variable_qtgui_label_1_tool_bar = Qt.QToolBar(self)

        if None:
            self._variable_qtgui_label_1_formatter = None
        else:
            self._variable_qtgui_label_1_formatter = lambda x: eng_notation.num_to_str(x)

        self._variable_qtgui_label_1_tool_bar.addWidget(Qt.QLabel("Rx2  "))
        self._variable_qtgui_label_1_label = Qt.QLabel(str(self._variable_qtgui_label_1_formatter(self.variable_qtgui_label_1)))
        self._variable_qtgui_label_1_tool_bar.addWidget(self._variable_qtgui_label_1_label)
        self.top_layout.addWidget(self._variable_qtgui_label_1_tool_bar)
        self._variable_qtgui_label_0_tool_bar = Qt.QToolBar(self)

        if None:
            self._variable_qtgui_label_0_formatter = None
        else:
            self._variable_qtgui_label_0_formatter = lambda x: eng_notation.num_to_str(x)

        self._variable_qtgui_label_0_tool_bar.addWidget(Qt.QLabel("Rx1  "))
        self._variable_qtgui_label_0_label = Qt.QLabel(str(self._variable_qtgui_label_0_formatter(self.variable_qtgui_label_0)))
        self._variable_qtgui_label_0_tool_bar.addWidget(self._variable_qtgui_label_0_label)
        self.top_grid_layout.addWidget(self._variable_qtgui_label_0_tool_bar, 0, 0, 1, 1)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        def _variable_function_probe_3_probe():
          self.flowgraph_started.wait()
          while True:

            val = self.blocks_probe_signal_x_3.level()
            try:
              try:
                self.doc.add_next_tick_callback(functools.partial(self.set_variable_function_probe_3,val))
              except AttributeError:
                self.set_variable_function_probe_3(val)
            except AttributeError:
              pass
            time.sleep(1.0 / (10))
        _variable_function_probe_3_thread = threading.Thread(target=_variable_function_probe_3_probe)
        _variable_function_probe_3_thread.daemon = True
        _variable_function_probe_3_thread.start()
        def _variable_function_probe_2_probe():
          self.flowgraph_started.wait()
          while True:

            val = self.blocks_probe_signal_x_2.level()
            try:
              try:
                self.doc.add_next_tick_callback(functools.partial(self.set_variable_function_probe_2,val))
              except AttributeError:
                self.set_variable_function_probe_2(val)
            except AttributeError:
              pass
            time.sleep(1.0 / (10))
        _variable_function_probe_2_thread = threading.Thread(target=_variable_function_probe_2_probe)
        _variable_function_probe_2_thread.daemon = True
        _variable_function_probe_2_thread.start()
        def _variable_function_probe_1_probe():
          self.flowgraph_started.wait()
          while True:

            val = self.blocks_probe_signal_x_1.level()
            try:
              try:
                self.doc.add_next_tick_callback(functools.partial(self.set_variable_function_probe_1,val))
              except AttributeError:
                self.set_variable_function_probe_1(val)
            except AttributeError:
              pass
            time.sleep(1.0 / (10))
        _variable_function_probe_1_thread = threading.Thread(target=_variable_function_probe_1_probe)
        _variable_function_probe_1_thread.daemon = True
        _variable_function_probe_1_thread.start()
        def _variable_function_probe_0_probe():
          self.flowgraph_started.wait()
          while True:

            val = self.blocks_probe_signal_x_0.level()
            try:
              try:
                self.doc.add_next_tick_callback(functools.partial(self.set_variable_function_probe_0,val))
              except AttributeError:
                self.set_variable_function_probe_0(val)
            except AttributeError:
              pass
            time.sleep(1.0 / (1))
        _variable_function_probe_0_thread = threading.Thread(target=_variable_function_probe_0_probe)
        _variable_function_probe_0_thread.daemon = True
        _variable_function_probe_0_thread.start()
        self.uhd_usrp_source_0 = uhd.usrp_source(
            ",".join(("addr=192.168.1.2", '')),
            uhd.stream_args(
                cpu_format="fc32",
                args='',
                channels=list(range(0,4)),
            ),
        )
        self.uhd_usrp_source_0.set_samp_rate(samp_rate)
        self.uhd_usrp_source_0.set_time_unknown_pps(uhd.time_spec(0))

        self.uhd_usrp_source_0.set_center_freq(fc, 0)
        self.uhd_usrp_source_0.set_antenna("RX2", 0)
        self.uhd_usrp_source_0.set_bandwidth(bw, 0)
        self.uhd_usrp_source_0.set_gain(10, 0)

        self.uhd_usrp_source_0.set_center_freq(fc, 1)
        self.uhd_usrp_source_0.set_antenna("RX2", 1)
        self.uhd_usrp_source_0.set_bandwidth(bw, 1)
        self.uhd_usrp_source_0.set_gain(10, 1)

        self.uhd_usrp_source_0.set_center_freq(fc, 2)
        self.uhd_usrp_source_0.set_antenna("RX2", 2)
        self.uhd_usrp_source_0.set_bandwidth(bw, 2)
        self.uhd_usrp_source_0.set_gain(10, 2)

        self.uhd_usrp_source_0.set_center_freq(fc, 3)
        self.uhd_usrp_source_0.set_antenna("RX2", 3)
        self.uhd_usrp_source_0.set_bandwidth(bw, 3)
        self.uhd_usrp_source_0.set_gain(10, 3)

        self.uhd_usrp_source_0.set_start_time(uhd.time_spec(5))
        self.blocks_nlog10_ff_0_2 = blocks.nlog10_ff(10, 1, 0)
        self.blocks_nlog10_ff_0_1 = blocks.nlog10_ff(10, 1, 0)
        self.blocks_nlog10_ff_0_0 = blocks.nlog10_ff(10, 1, 0)
        self.blocks_nlog10_ff_0 = blocks.nlog10_ff(10, 1, 0)
        self.blocks_moving_average_xx_0_2 = blocks.moving_average_ff(50000, (20*10**(-6)), 4000, 1)
        self.blocks_moving_average_xx_0_1 = blocks.moving_average_ff(50000, (20*10**(-6)), 4000, 1)
        self.blocks_moving_average_xx_0_0 = blocks.moving_average_ff(50000, (20*10**(-6)), 4000, 1)
        self.blocks_moving_average_xx_0 = blocks.moving_average_ff(50000, (20*10**(-6)), 4000, 1)
        self.blocks_complex_to_mag_squared_0_2 = blocks.complex_to_mag_squared(1)
        self.blocks_complex_to_mag_squared_0_1 = blocks.complex_to_mag_squared(1)
        self.blocks_complex_to_mag_squared_0_0 = blocks.complex_to_mag_squared(1)
        self.blocks_complex_to_mag_squared_0 = blocks.complex_to_mag_squared(1)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_complex_to_mag_squared_0, 0), (self.blocks_moving_average_xx_0, 0))
        self.connect((self.blocks_complex_to_mag_squared_0_0, 0), (self.blocks_moving_average_xx_0_0, 0))
        self.connect((self.blocks_complex_to_mag_squared_0_1, 0), (self.blocks_moving_average_xx_0_1, 0))
        self.connect((self.blocks_complex_to_mag_squared_0_2, 0), (self.blocks_moving_average_xx_0_2, 0))
        self.connect((self.blocks_moving_average_xx_0, 0), (self.blocks_nlog10_ff_0, 0))
        self.connect((self.blocks_moving_average_xx_0_0, 0), (self.blocks_nlog10_ff_0_0, 0))
        self.connect((self.blocks_moving_average_xx_0_1, 0), (self.blocks_nlog10_ff_0_1, 0))
        self.connect((self.blocks_moving_average_xx_0_2, 0), (self.blocks_nlog10_ff_0_2, 0))
        self.connect((self.blocks_nlog10_ff_0, 0), (self.blocks_probe_signal_x_0, 0))
        self.connect((self.blocks_nlog10_ff_0_0, 0), (self.blocks_probe_signal_x_1, 0))
        self.connect((self.blocks_nlog10_ff_0_1, 0), (self.blocks_probe_signal_x_2, 0))
        self.connect((self.blocks_nlog10_ff_0_2, 0), (self.blocks_probe_signal_x_3, 0))
        self.connect((self.uhd_usrp_source_0, 0), (self.blocks_complex_to_mag_squared_0, 0))
        self.connect((self.uhd_usrp_source_0, 1), (self.blocks_complex_to_mag_squared_0_0, 0))
        self.connect((self.uhd_usrp_source_0, 2), (self.blocks_complex_to_mag_squared_0_1, 0))
        self.connect((self.uhd_usrp_source_0, 3), (self.blocks_complex_to_mag_squared_0_2, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("gnuradio/flowgraphs", "lowSpeedTest")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_variable_function_probe_3(self):
        return self.variable_function_probe_3

    def set_variable_function_probe_3(self, variable_function_probe_3):
        self.variable_function_probe_3 = variable_function_probe_3
        self.set_variable_qtgui_label_3(self.variable_function_probe_3)

    def get_variable_function_probe_2(self):
        return self.variable_function_probe_2

    def set_variable_function_probe_2(self, variable_function_probe_2):
        self.variable_function_probe_2 = variable_function_probe_2
        self.set_variable_qtgui_label_2(self.variable_function_probe_2)

    def get_variable_function_probe_1(self):
        return self.variable_function_probe_1

    def set_variable_function_probe_1(self, variable_function_probe_1):
        self.variable_function_probe_1 = variable_function_probe_1
        self.set_variable_qtgui_label_1(self.variable_function_probe_1)

    def get_variable_function_probe_0(self):
        return self.variable_function_probe_0

    def set_variable_function_probe_0(self, variable_function_probe_0):
        self.variable_function_probe_0 = variable_function_probe_0
        self.set_variable_qtgui_label_0(self.variable_function_probe_0)

    def get_variable_qtgui_label_3(self):
        return self.variable_qtgui_label_3

    def set_variable_qtgui_label_3(self, variable_qtgui_label_3):
        self.variable_qtgui_label_3 = variable_qtgui_label_3
        Qt.QMetaObject.invokeMethod(self._variable_qtgui_label_3_label, "setText", Qt.Q_ARG("QString", str(self._variable_qtgui_label_3_formatter(self.variable_qtgui_label_3))))

    def get_variable_qtgui_label_2(self):
        return self.variable_qtgui_label_2

    def set_variable_qtgui_label_2(self, variable_qtgui_label_2):
        self.variable_qtgui_label_2 = variable_qtgui_label_2
        Qt.QMetaObject.invokeMethod(self._variable_qtgui_label_2_label, "setText", Qt.Q_ARG("QString", str(self._variable_qtgui_label_2_formatter(self.variable_qtgui_label_2))))

    def get_variable_qtgui_label_1(self):
        return self.variable_qtgui_label_1

    def set_variable_qtgui_label_1(self, variable_qtgui_label_1):
        self.variable_qtgui_label_1 = variable_qtgui_label_1
        Qt.QMetaObject.invokeMethod(self._variable_qtgui_label_1_label, "setText", Qt.Q_ARG("QString", str(self._variable_qtgui_label_1_formatter(self.variable_qtgui_label_1))))

    def get_variable_qtgui_label_0(self):
        return self.variable_qtgui_label_0

    def set_variable_qtgui_label_0(self, variable_qtgui_label_0):
        self.variable_qtgui_label_0 = variable_qtgui_label_0
        Qt.QMetaObject.invokeMethod(self._variable_qtgui_label_0_label, "setText", Qt.Q_ARG("QString", str(self._variable_qtgui_label_0_formatter(self.variable_qtgui_label_0))))

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.uhd_usrp_source_0.set_samp_rate(self.samp_rate)

    def get_fc(self):
        return self.fc

    def set_fc(self, fc):
        self.fc = fc
        self.uhd_usrp_source_0.set_center_freq(self.fc, 0)
        self.uhd_usrp_source_0.set_center_freq(self.fc, 1)
        self.uhd_usrp_source_0.set_center_freq(self.fc, 2)
        self.uhd_usrp_source_0.set_center_freq(self.fc, 3)

    def get_bw(self):
        return self.bw

    def set_bw(self, bw):
        self.bw = bw
        self.uhd_usrp_source_0.set_bandwidth(self.bw, 0)
        self.uhd_usrp_source_0.set_bandwidth(self.bw, 1)
        self.uhd_usrp_source_0.set_bandwidth(self.bw, 2)
        self.uhd_usrp_source_0.set_bandwidth(self.bw, 3)




def main(top_block_cls=lowSpeedTest, options=None):

    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()

    tb.start()
    tb.flowgraph_started.set()

    tb.show()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    qapp.exec_()

if __name__ == '__main__':
    main()
