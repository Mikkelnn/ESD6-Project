#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: USRP_rx_test
# GNU Radio version: 3.10.12.0

from PyQt5 import Qt
from gnuradio import qtgui
from gnuradio import analog
from gnuradio import blocks
from gnuradio import gr
from gnuradio.filter import firdes
from gnuradio.fft import window
import sys
import signal
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
import sip
import threading



class USRPrx(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "USRP_rx_test", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("USRP_rx_test")
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

        self.settings = Qt.QSettings("gnuradio/flowgraphs", "USRPrx")

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
        self.samp_rate = samp_rate = 30*10**6
        self.fc = fc = 5.8*10**9
        self.bw = bw = 10*10**6

        ##################################################
        # Blocks
        ##################################################

        self.qtgui_const_sink_x_0 = qtgui.const_sink_c(
            32768, #size
            "", #name
            4, #number of inputs
            None # parent
        )
        self.qtgui_const_sink_x_0.set_update_time(0.10)
        self.qtgui_const_sink_x_0.set_y_axis((-1.2), 1.2)
        self.qtgui_const_sink_x_0.set_x_axis((-1.2), 1.2)
        self.qtgui_const_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, "")
        self.qtgui_const_sink_x_0.enable_autoscale(False)
        self.qtgui_const_sink_x_0.enable_grid(False)
        self.qtgui_const_sink_x_0.enable_axis_labels(True)


        labels = ['', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        styles = [0, 0, 0, 0, 0,
            0, 0, 0, 0, 0]
        markers = [0, 0, 0, 0, 0,
            0, 0, 0, 0, 0]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(4):
            if len(labels[i]) == 0:
                self.qtgui_const_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_const_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_const_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_const_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_const_sink_x_0.set_line_style(i, styles[i])
            self.qtgui_const_sink_x_0.set_line_marker(i, markers[i])
            self.qtgui_const_sink_x_0.set_line_alpha(i, alphas[i])

        self._qtgui_const_sink_x_0_win = sip.wrapinstance(self.qtgui_const_sink_x_0.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_const_sink_x_0_win)
        self.blocks_multiply_xx_0_2 = blocks.multiply_vcc(1)
        self.blocks_multiply_xx_0_1 = blocks.multiply_vcc(1)
        self.blocks_multiply_xx_0_0 = blocks.multiply_vcc(1)
        self.blocks_multiply_xx_0 = blocks.multiply_vcc(1)
        self.blocks_conjugate_cc_0_2 = blocks.conjugate_cc()
        self.blocks_conjugate_cc_0_1 = blocks.conjugate_cc()
        self.blocks_conjugate_cc_0_0 = blocks.conjugate_cc()
        self.blocks_conjugate_cc_0 = blocks.conjugate_cc()
        self.analog_sig_source_x_1_1 = analog.sig_source_c(samp_rate, analog.GR_SIN_WAVE, 1000, 1, 0, 0)
        self.analog_sig_source_x_1_0 = analog.sig_source_c(samp_rate, analog.GR_SIN_WAVE, 1000, 1, 0, 1)
        self.analog_sig_source_x_1 = analog.sig_source_c(samp_rate, analog.GR_SIN_WAVE, 1000, 1, 0, 0.5)
        self.analog_sig_source_x_0 = analog.sig_source_c(samp_rate, analog.GR_SIN_WAVE, 1000, 1, 0, 0.25)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_sig_source_x_0, 0), (self.blocks_conjugate_cc_0_0, 0))
        self.connect((self.analog_sig_source_x_1, 0), (self.blocks_conjugate_cc_0_1, 0))
        self.connect((self.analog_sig_source_x_1_0, 0), (self.blocks_conjugate_cc_0_2, 0))
        self.connect((self.analog_sig_source_x_1_1, 0), (self.blocks_conjugate_cc_0, 0))
        self.connect((self.analog_sig_source_x_1_1, 0), (self.blocks_multiply_xx_0, 0))
        self.connect((self.analog_sig_source_x_1_1, 0), (self.blocks_multiply_xx_0_0, 0))
        self.connect((self.analog_sig_source_x_1_1, 0), (self.blocks_multiply_xx_0_1, 0))
        self.connect((self.analog_sig_source_x_1_1, 0), (self.blocks_multiply_xx_0_2, 0))
        self.connect((self.blocks_conjugate_cc_0, 0), (self.blocks_multiply_xx_0, 1))
        self.connect((self.blocks_conjugate_cc_0_0, 0), (self.blocks_multiply_xx_0_0, 1))
        self.connect((self.blocks_conjugate_cc_0_1, 0), (self.blocks_multiply_xx_0_1, 1))
        self.connect((self.blocks_conjugate_cc_0_2, 0), (self.blocks_multiply_xx_0_2, 1))
        self.connect((self.blocks_multiply_xx_0, 0), (self.qtgui_const_sink_x_0, 0))
        self.connect((self.blocks_multiply_xx_0_0, 0), (self.qtgui_const_sink_x_0, 1))
        self.connect((self.blocks_multiply_xx_0_1, 0), (self.qtgui_const_sink_x_0, 2))
        self.connect((self.blocks_multiply_xx_0_2, 0), (self.qtgui_const_sink_x_0, 3))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("gnuradio/flowgraphs", "USRPrx")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.analog_sig_source_x_0.set_sampling_freq(self.samp_rate)
        self.analog_sig_source_x_1.set_sampling_freq(self.samp_rate)
        self.analog_sig_source_x_1_0.set_sampling_freq(self.samp_rate)
        self.analog_sig_source_x_1_1.set_sampling_freq(self.samp_rate)

    def get_fc(self):
        return self.fc

    def set_fc(self, fc):
        self.fc = fc

    def get_bw(self):
        return self.bw

    def set_bw(self, bw):
        self.bw = bw




def main(top_block_cls=USRPrx, options=None):

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
