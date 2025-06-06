#
# Copyright 2015 Ettus Research LLC
#

#-------------------------------------------------
# Top-of-Makefile
#-------------------------------------------------
# Define BASE_DIR to point to the "top" dir
BASE_DIR = $(abspath ../../..)
# Include viv_sim_preamble after defining BASE_DIR
include $(BASE_DIR)/../tools/make/viv_sim_preamble.mak

#-------------------------------------------------
# Design Specific
#-------------------------------------------------
# Define part using PART_ID (<device>/<package>/<speedgrade>)
ARCH = kintex7
PART_ID = xc7k410t/ffg900/-2

# Include makefiles and sources for the DUT and its dependencies
include $(BASE_DIR)/../lib/fifo/Makefile.srcs
include $(BASE_DIR)/../lib/axi/Makefile.srcs
include $(BASE_DIR)/../lib/control/Makefile.srcs
include $(BASE_DIR)/../lib/rfnoc/Makefile.srcs

DESIGN_SRCS = $(abspath \
$(FIFO_SRCS) \
$(AXI_SRCS) \
$(CONTROL_LIB_SRCS) \
$(RFNOC_SRCS) \
)

#-------------------------------------------------
# IP Specific
#-------------------------------------------------
# If simulation contains IP, define the IP_DIR and point
# it to the base level IP directory
IP_DIR = ../../ip

# Include makefiles and sources for all IP components
# *after* defining the IP_DIR
include $(IP_DIR)/aurora_64b66b_pcs_pma/Makefile.inc
include $(IP_DIR)/fifo_short_2clk/Makefile.inc
include $(IP_DIR)/axi64_4k_2clk_fifo/Makefile.inc

DESIGN_SRCS += $(abspath \
$(IP_AURORA_64B66B_PCS_PMA_SRCS) \
$(IP_AXI64_4K_2CLK_FIFO_SRCS) \
$(IP_FIFO_SHORT_2CLK_SRCS) \
$(AURORA_PHY_SRCS) \
)

#-------------------------------------------------
# ModelSim Specific
#-------------------------------------------------

MODELSIM_IP_SRCS = $(wildcard $(abspath \
$(IP_BUILD_DIR)/fifo_short_2clk/sim/fifo_short_2clk.v \
$(IP_BUILD_DIR)/axi64_4k_2clk_fifo/sim/axi64_4k_2clk_fifo.v \
$(IP_BUILD_DIR)/aurora_64b66b_pcs_pma/aurora_64b66b_pcs_pma.v \
$(IP_BUILD_DIR)/aurora_64b66b_pcs_pma/aurora_64b66b_pcs_pma_core.v \
$(IP_BUILD_DIR)/aurora_64b66b_pcs_pma/aurora_64b66b_pcs_pma/src/*.v \
$(IP_BUILD_DIR)/aurora_64b66b_pcs_pma/aurora_64b66b_pcs_pma/example_design/*.v \
$(IP_BUILD_DIR)/aurora_64b66b_pcs_pma/aurora_64b66b_pcs_pma/example_design/gt/*.v \
$(VIVADO_PATH)/data/verilog/src/glbl.v \
))

MODELSIM_LIBS += \
unisims_ver \
unimacro_ver \
secureip \
fifo_generator_v13_2_5 \


MODELSIM_ARGS += glbl -t 1fs

#-------------------------------------------------
# Testbench Specific
#-------------------------------------------------
include $(BASE_DIR)/../sim/general/Makefile.srcs
include $(BASE_DIR)/../sim/control/Makefile.srcs
include $(BASE_DIR)/../sim/axi/Makefile.srcs

# Define only one toplevel module
SIM_TOP = aurora_loopback_tb
# Simulation runtime in microseconds
SIM_RUNTIME_US = 70

SIM_SRCS = \
$(abspath aurora_loopback_tb.sv) \
$(SIM_GENERAL_SRCS) \
$(SIM_CONTROL_SRCS) \
$(SIM_AXI_SRCS) \
$(MODELSIM_IP_SRCS) \

#-------------------------------------------------
# Bottom-of-Makefile
#-------------------------------------------------
# Include all simulator specific makefiles here
# Each should define a unique target to simulate
# e.g. xsim, vsim, etc and a common "clean" target
include $(BASE_DIR)/../tools/make/viv_simulator.mak
