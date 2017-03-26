
all:


ifndef COCOTB
	$(error "Must provide cocotb path eg 'COCOTB=/path/to/cocotb'")
endif

VHDL_SOURCES = $(PWD)/../rtl/crossing.vhdl

TOPLEVEL = crossing_controller
MODULE   = test_controller

include $(COCOTB)/makefiles/Makefile.inc
include $(COCOTB)/makefiles/Makefile.sim
