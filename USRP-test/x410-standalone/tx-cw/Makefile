# === CONFIGURE THESE ===
APP_NAME := cw_tx
SRC := $(APP_NAME).cpp
OUT := $(APP_NAME)

# Paths
SYSROOT := ../x410-sysroot
INCLUDE_DIR := $(SYSROOT)/include
LIB_DIR := $(SYSROOT)/lib

# Cross-compiler
CROSS_COMPILE := aarch64-linux-gnu
CXX := $(CROSS_COMPILE)-g++

# Flags
INCLUDES := -I$(INCLUDE_DIR)
LIBS := -L$(LIB_DIR) -luhd
RPATH := -Wl,-rpath-link=$(LIB_DIR)

CXXFLAGS := -O2 -std=c++17 $(INCLUDES)
LDFLAGS := $(LIBS) $(RPATH)

# === RULES ===
all: $(OUT)

$(OUT): $(SRC)
	$(CXX) $(CXXFLAGS) -o $@ $^ $(LDFLAGS)

clean:
	rm -f $(OUT)
