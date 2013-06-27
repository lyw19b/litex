from mibuild.generic_platform import *
from mibuild.xilinx_ise import XilinxISEPlatform, CRG_SE

_io = [
		("user_btn", 0, Pins("V4"), IOStandard("LVCMOS33"),
			Misc("PULLDOWN"), Misc("TIG")),

		# TI CDCE913 programmable triple-output PLL
		("clk_y1", 0, Pins("V10"), IOStandard("LVCMOS33")), # default: 40 MHz
		("clk_y2", 0, Pins("K15"), IOStandard("LVCMOS33")), # default: 66 2/3 MHz
		("clk_y3", 0, Pins("C10"), IOStandard("LVCMOS33")), # default: 100 MHz

		# Maxim DS1088LU oscillator, not populated
		("clk_backup", 0, Pins("R8"), IOStandard("LVCMOS33")),

		# TI CDCE913 PLL I2C control
		("pll", 0,
			Subsignal("scl", Pins("P12")),
			Subsignal("sda", Pins("U13")),
			Misc("PULLUP"),
			IOStandard("LVCMOS33")),

		# Micron N25Q128 SPI Flash
		("spiflash", 0,
			Subsignal("clk", Pins("R15")),
			Subsignal("cs_n", Pins("V3")),
			Subsignal("dq", Pins("T13 R13 T14 V14")),
			IOStandard("LVCMOS33")),

		("user_dip", 0, Pins("B3 A3 B4 A4"), Misc("PULLDOWN"),
				IOStandard("LVCMOS33")),

		("user_led", 0, Pins("P4 L6 F5 C2"), Misc("SLEW=QUIETIO"),
				IOStandard("LVCMOS18")),

		# PMOD extension connectors
		("pmod", 0,
			Subsignal("d", Pins("F15 F16 C17 C18 F14 G14 D17 D18")),
			IOStandard("LVCMOS33")),
		("pmod", 1,
			Subsignal("d", Pins("H12 G13 E16 E18 K12 K13 F17 F18")),
			IOStandard("LVCMOS33")),

		("uart", 0,
			Subsignal("tx", Pins("T7"), Misc("SLEW=SLOW")),
			Subsignal("rx", Pins("R7"), Misc("PULLUP")),
			IOStandard("LVCMOS33")),

		("ddram_clock", 0,
			Subsignal("p", Pins("G3")),
			Subsignal("n", Pins("G1")),
			IOStandard("MOBILE_DDR")), # actually DIFF_

		# Micron MT46H32M16LFBF-5 LPDDR
		("ddram", 0,
			Subsignal("a", Pins("J7 J6 H5 L7 F3 H4 H3 H6 "
				"D2 D1 F4 D3 G6")),
			Subsignal("ba", Pins("F2 F1")),
			Subsignal("dq", Pins("L2 L1 K2 K1 H2 H1 J3 J1 "
				"M3 M1 N2 N1 T2 T1 U2 U1")),
			Subsignal("cke", Pins("H7")),
			Subsignal("we_n", Pins("E3")),
			Subsignal("cs_n", Pins("K6")), # NC!
			Subsignal("cas_n", Pins("K5")),
			Subsignal("ras_n", Pins("L5")),
			Subsignal("dm", Pins("K3", "K4")),
			Subsignal("dqs", Pins("L4", "P2")),
			Subsignal("rzq", Pins("N4")),
			IOStandard("MOBILE_DDR")),

		# Nat Semi DP83848J 10/100 Ethernet PHY
		# pull-ups on rx_data set phy addr to 11110b
		# and prevent isolate mode (addr 00000b)
		("eth_clocks", 0,
			Subsignal("rx", Pins("L15")),
			Subsignal("tx", Pins("H17")),
			IOStandard("LVCMOS33")),

		("eth", 0,
			Subsignal("col", Pins("M18"), Misc("PULLDOWN")),
			Subsignal("crs", Pins("N17"), Misc("PULLDOWN")),
			Subsignal("mdc", Pins("M16")),
			Subsignal("mdio", Pins("L18")),
			Subsignal("rst_n", Pins("T18"), Misc("TIG")),
			Subsignal("rx_data", Pins("T17 N16 N15 P18"), Misc("PULLUP")),
			Subsignal("dv", Pins("P17")),
			Subsignal("rx_er", Pins("N18")),
			Subsignal("tx_data", Pins("K18 K17 J18 J16")),
			Subsignal("tx_en", Pins("L17")),
			Subsignal("tx_er", Pins("L16")), # NC!
			IOStandard("LVCMOS33")),
		]


class Platform(XilinxISEPlatform):
	def __init__(self):
		XilinxISEPlatform.__init__(self, "xc6slx9-2csg324", _io,
				lambda p: CRG_SE(p, "clk_y3", "user_btn", 10.))
		self.add_platform_command("""
CONFIG VCCAUX = "3.3";
""")

	def do_finalize(self, fragment):
		try:
			eth_clocks = self.lookup_request("eth_clocks")
			self.add_platform_command("""
NET "{phy_rx_clk}" TNM_NET = "GRPphy_rx_clk";
NET "{phy_tx_clk}" TNM_NET = "GRPphy_tx_clk";
TIMESPEC "TSphy_rx_clk" = PERIOD "GRPphy_rx_clk" 40 ns HIGH 50%;
TIMESPEC "TSphy_tx_clk" = PERIOD "GRPphy_tx_clk" 40 ns HIGH 50%;
TIMESPEC "TSphy_tx_clk_io" = FROM "GRPphy_tx_clk" TO "PADS" 10 ns;
TIMESPEC "TSphy_rx_clk_io" = FROM "PADS" TO "GRPphy_rx_clk" 10 ns;
""", phy_rx_clk=eth_clocks.rx, phy_tx_clk=eth_clocks.tx)
		except ContraintError:
			pass
