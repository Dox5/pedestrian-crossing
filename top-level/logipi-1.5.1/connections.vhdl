library ieee;
use ieee.std_logic_1164.all;

library crossing_controller;


entity top_level is
    port(
        OSC_FPGA : in std_ulogic;
        PB       : in std_ulogic_vector(1 DOWNTO 0);
		  PMOD1	  : out std_ulogic_vector(2 DOWNTO 0);
		  LED		  : out std_ulogic_vector(1 DOWNTO 0)
    );
end top_level;

architecture rtl of top_level is
    signal clk_4hz        : std_ulogic := '0';
	 signal reset_toggle   : std_ulogic := '1';
	 signal reset_debounce : std_ulogic := '0';
	 
	 signal reset_button   : std_ulogic;
	 signal wait_button   : std_ulogic;
	 
	 constant hold_ticks : integer := (50000000 / (4*2)) - 1;
	 signal counter : integer range hold_ticks DOWNTO 0 := 0;
	 
    component crossing_controller is
        port(
            -- 4 Hz clock
            clk : in std_ulogic; 
            reset : in std_ulogic;

            wait_btn : in std_ulogic;

            -- traffic lights 0: red, 1: Amber, 2: Green
            lights   : out std_ulogic_vector(2 DOWNTO 0);

            buzzer   : out std_ulogic;

            spinner  : out std_ulogic
		  );
    end component;
	 
begin
	LED(0) <= reset_toggle;
	LED(1) <= clk_4hz;
	
	-- PB are the wrong way around!
	wait_button <= not PB(0);
	reset_button <= not PB(1);
	
	controller: crossing_controller
	    port map(
			clk => clk_4hz,
			reset => reset_toggle,
			wait_btn => wait_button,
			lights => PMOD1
		 );
		 
    process(OSC_FPGA)
    begin
        if rising_edge(OSC_FPGA) then
		      if reset_button = '0' and reset_debounce = '0' then
					reset_toggle <= not reset_toggle;						 
					reset_debounce <= '1';
				end if;
				
				if reset_button = '1' and reset_debounce = '1' then
					reset_debounce <= '0';
				end if;
        end if;
    end process;
	 
	 -- Take our 50Mhz clock and make it 4Hz :)
    process(OSC_FPGA)     
    begin
        if rising_edge(OSC_FPGA) then
		      if counter = hold_ticks then
			       clk_4hz <= not clk_4hz;
					 counter <= 0;
		      else
				    counter <= counter + 1;
				end if;
		  end if;
	 end process;
		 
end architecture;
