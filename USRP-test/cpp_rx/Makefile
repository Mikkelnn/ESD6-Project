# Makefile

# Compiler and flags
CXX = g++
CXXFLAGS = -std=c++11

# UHD library
LDLIBS = -luhd

# Source files
SRCS = main.cpp
OBJS = $(SRCS:.cpp=.o)

# Output binary
TARGET = radar

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CXX) $(CXXFLAGS) -o $@ $^ $(LDLIBS)

%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $<

clean:
	rm -f $(OBJS) $(TARGET)
