#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Not titled yet
# Author: theil
# GNU Radio version: 3.10.11.0

from PyQt5 import Qt
from gnuradio import qtgui
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
from gnuradio import uhd
import time
import threading



class phaseShiftSetup(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Not titled yet", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Not titled yet")
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

        self.settings = Qt.QSettings("gnuradio/flowgraphs", "phaseShiftSetup")

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
        self.samp_rate = samp_rate = 40000000
        self.gain = gain = 10
        self.fc = fc = 100*10**6
        self.bw = bw = 5*10**6

        ##################################################
        # Blocks
        ##################################################

        self.uhd_usrp_source_0 = uhd.usrp_source(
            ",".join(("addr=192.168.1.2", '')),
            uhd.stream_args(
                cpu_format="fc32",
                args='',
                channels=list(range(0,4)),
            ),
        )
        self.uhd_usrp_source_0.set_clock_source('external', 0)
        self.uhd_usrp_source_0.set_samp_rate(samp_rate)
        self.uhd_usrp_source_0.set_time_now(uhd.time_spec(time.time()), uhd.ALL_MBOARDS)

        self.uhd_usrp_source_0.set_center_freq(fc, 0)
        self.uhd_usrp_source_0.set_antenna("RX1", 0)
        self.uhd_usrp_source_0.set_bandwidth(bw, 0)
        self.uhd_usrp_source_0.set_gain(gain, 0)

        self.uhd_usrp_source_0.set_center_freq(fc, 1)
        self.uhd_usrp_source_0.set_antenna("RX1", 1)
        self.uhd_usrp_source_0.set_bandwidth(bw, 1)
        self.uhd_usrp_source_0.set_gain(gain, 1)

        self.uhd_usrp_source_0.set_center_freq(fc, 2)
        self.uhd_usrp_source_0.set_antenna("RX1", 2)
        self.uhd_usrp_source_0.set_bandwidth(bw, 2)
        self.uhd_usrp_source_0.set_gain(gain, 2)

        self.uhd_usrp_source_0.set_center_freq(fc, 3)
        self.uhd_usrp_source_0.set_antenna("RX1", 3)
        self.uhd_usrp_source_0.set_bandwidth(bw, 3)
        self.uhd_usrp_source_0.set_gain(gain, 3)
        self.blocks_sub_xx_0_2 = blocks.sub_ff(1)
        self.blocks_sub_xx_0_1 = blocks.sub_ff(1)
        self.blocks_sub_xx_0_0 = blocks.sub_ff(1)
        self.blocks_sub_xx_0 = blocks.sub_ff(1)
        self.blocks_skiphead_0 = blocks.skiphead(gr.sizeof_float*1, (4*2000))
        self.blocks_interleave_0 = blocks.interleave(gr.sizeof_float*1, 1)
        self.blocks_head_0 = blocks.head(gr.sizeof_float*1, 10000)
        self.blocks_file_sink_0 = blocks.file_sink(gr.sizeof_float*1, 'phaseShift.dat', False)
        self.blocks_file_sink_0.set_unbuffered(False)
        self.blocks_complex_to_arg_2 = blocks.complex_to_arg(1)
        self.blocks_complex_to_arg_1 = blocks.complex_to_arg(1)
        self.blocks_complex_to_arg_0_0 = blocks.complex_to_arg(1)
        self.blocks_complex_to_arg_0 = blocks.complex_to_arg(1)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_complex_to_arg_0, 0), (self.blocks_sub_xx_0, 1))
        self.connect((self.blocks_complex_to_arg_0, 0), (self.blocks_sub_xx_0, 0))
        self.connect((self.blocks_complex_to_arg_0, 0), (self.blocks_sub_xx_0_0, 0))
        self.connect((self.blocks_complex_to_arg_0, 0), (self.blocks_sub_xx_0_1, 0))
        self.connect((self.blocks_complex_to_arg_0, 0), (self.blocks_sub_xx_0_2, 0))
        self.connect((self.blocks_complex_to_arg_0_0, 0), (self.blocks_sub_xx_0_0, 1))
        self.connect((self.blocks_complex_to_arg_1, 0), (self.blocks_sub_xx_0_1, 1))
        self.connect((self.blocks_complex_to_arg_2, 0), (self.blocks_sub_xx_0_2, 1))
        self.connect((self.blocks_head_0, 0), (self.blocks_file_sink_0, 0))
        self.connect((self.blocks_interleave_0, 0), (self.blocks_skiphead_0, 0))
        self.connect((self.blocks_skiphead_0, 0), (self.blocks_head_0, 0))
        self.connect((self.blocks_sub_xx_0, 0), (self.blocks_interleave_0, 0))
        self.connect((self.blocks_sub_xx_0_0, 0), (self.blocks_interleave_0, 1))
        self.connect((self.blocks_sub_xx_0_1, 0), (self.blocks_interleave_0, 2))
        self.connect((self.blocks_sub_xx_0_2, 0), (self.blocks_interleave_0, 3))
        self.connect((self.uhd_usrp_source_0, 0), (self.blocks_complex_to_arg_0, 0))
        self.connect((self.uhd_usrp_source_0, 1), (self.blocks_complex_to_arg_0_0, 0))
        self.connect((self.uhd_usrp_source_0, 2), (self.blocks_complex_to_arg_1, 0))
        self.connect((self.uhd_usrp_source_0, 3), (self.blocks_complex_to_arg_2, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("gnuradio/flowgraphs", "phaseShiftSetup")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.uhd_usrp_source_0.set_samp_rate(self.samp_rate)

    def get_gain(self):
        return self.gain

    def set_gain(self, gain):
        self.gain = gain
        self.uhd_usrp_source_0.set_gain(self.gain, 0)
        self.uhd_usrp_source_0.set_gain(self.gain, 1)
        self.uhd_usrp_source_0.set_gain(self.gain, 2)
        self.uhd_usrp_source_0.set_gain(self.gain, 3)

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




def main(top_block_cls=phaseShiftSetup, options=None):

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
