# Makefile for Logistics Routing Engine

# Compiler settings
CXX = g++
CXXFLAGS = -std=c++11 -Wall -Wextra -O2

# Libraries
LIBS = -ljsoncpp

# Target executable
TARGET = routing_engine

# Source files
SOURCES = routing_engine.cpp

# Object files
OBJECTS = $(SOURCES:.cpp=.o)

# Default target
all: $(TARGET)

# Build the executable
$(TARGET): $(OBJECTS)
	$(CXX) $(OBJECTS) -o $(TARGET) $(LIBS)

# Compile source files
%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

# Clean build files
clean:
	rm -f $(OBJECTS) $(TARGET)

# Install dependencies (Ubuntu/Debian)
install-deps:
	sudo apt-get update
	sudo apt-get install -y g++ libjsoncpp-dev

# Install dependencies (CentOS/RHEL/Fedora)
install-deps-rpm:
	sudo yum install -y gcc-c++ jsoncpp-devel

# Install dependencies (macOS with Homebrew)
install-deps-macos:
	brew install jsoncpp

# Test the routing engine
test: $(TARGET)
	./$(TARGET) factory warehouse_north

# Run with sample data
run-sample: $(TARGET)
	./$(TARGET) warehouse_east warehouse_south

# Show help
help:
	@echo "Available targets:"
	@echo "  all              - Build the routing engine"
	@echo "  clean            - Remove build files"
	@echo "  install-deps     - Install dependencies (Ubuntu/Debian)"
	@echo "  install-deps-rpm - Install dependencies (CentOS/RHEL/Fedora)"
	@echo "  install-deps-macos - Install dependencies (macOS)"
	@echo "  test             - Test with factory to warehouse_north"
	@echo "  run-sample       - Test with warehouse_east to warehouse_south"
	@echo "  help             - Show this help message"

.PHONY: all clean install-deps install-deps-rpm install-deps-macos test run-sample help 