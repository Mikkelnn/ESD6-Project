#
# Copyright 2024 Ettus Research, a National Instruments Brand
#
# SPDX-License-Identifier: LGPL-3.0-or-later
#

include $(TOOLS_DIR)/make/viv_ip_builder.mak

LIB_IP_XFFT_64K_16B_SRCS = $(IP_BUILD_DIR)/xfft_64k_16b/xfft_64k_16b.xci

LIB_IP_XFFT_64K_16B_OUTS = $(addprefix $(IP_BUILD_DIR)/xfft_64k_16b/, \
xfft_64k_16b.xci.out \
synth/xfft_64k_16b.vhd \
)

$(LIB_IP_XFFT_64K_16B_SRCS) $(LIB_IP_XFFT_64K_16B_OUTS) : $(LIB_IP_DIR)/xfft_64k_16b/xfft_64k_16b.xci
	$(call BUILD_VIVADO_IP,xfft_64k_16b,$(ARCH),$(PART_ID),$(LIB_IP_DIR),$(IP_BUILD_DIR),0)
