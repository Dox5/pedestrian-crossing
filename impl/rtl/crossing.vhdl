library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;


entity crossing_controller is
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
end crossing_controller;

-- Transision timings
-- btn       -> amber     1s
-- amber     -> red       2s
-- red       -> red amber 4s
-- red amber -> green     2s
architecture rtl of crossing_controller is
    type state_machine_type is (in_reset, green, amber, red, red_amber);

    signal state : state_machine_type := in_reset;
    signal btn_debounce : std_ulogic  := '0';

    -- Longest transision is 4 seconds, which is 4 * 4 clock ticks
    -- so 5 bits should be enough to count this down
    -- When next_state is in_reset this means that no change is in progress
    signal delay_change : integer range 16 DOWNTO 0 := 0;
    signal next_state  : state_machine_type         := in_reset;
begin
    buzzer <= '0';
    spinner <= '0';

    process(clk, reset, state)
    begin
        if reset = '1' then
            state <= in_reset;
        elsif rising_edge(clk) then
            if state = in_reset then
                state <= green;
            end if;

            if          state = green 
                    and wait_btn = '1' 
                    and btn_debounce = '0' 
                    and next_state = in_reset then
                -- Stop the button being pressed again
                btn_debounce <= '1';
                delay_change <=  (1 * 4) - 1;
                next_state   <= amber;

            elsif next_state /= in_reset then
                -- We are counting down to a change!

                if delay_change = 0 then
                    -- Time to change our state!
                    state <= next_state;

                    -- Start the next transition
                    case next_state is
                        when amber =>
                            -- Next state is red in 2 seconds
                            next_state <= red;
                            delay_change <= (2 * 4) - 1;
                        when red =>
                            -- Next state is red amber is 4 seconds
                            next_state <= red_amber;
                            delay_change <= (4 * 4) - 1;
                        when red_amber =>
                            next_state <= green;
                            delay_change <= (2 * 4)  - 1;
                        when others =>
                            delay_change <= 0;
                            next_state <= in_reset;
                    end case;
                else
                    delay_change <= delay_change - 1;
                end if;
            end if;




            if wait_btn = '0' and btn_debounce = '1' then
                -- Allow the button to be pressed again, it has been released
                btn_debounce <= '0';
            end if;

        end if;

        case state is
            when in_reset =>
                lights <= (others => '0');
                btn_debounce <= '0';
                delay_change <= 0;
                next_state <= in_reset;
            when green =>
                lights <= "001";
            when amber =>
                lights <= "010";
            when red =>
                lights <= "100";
            when red_amber =>
                lights <= "110";
        end case;
    end process;
end rtl;
