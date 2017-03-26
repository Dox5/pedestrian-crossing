import cocotb

from cocotb.triggers import Edge
from cocotb.triggers import Timer
from cocotb.result import TestFailure

SECONDS = 10 ** 9

def toggle_clock(clk):
    current_state = clk.value
    clk.value = not current_state

@cocotb.coroutine
def single_step_sim(clk, clock_rate_hz=4):
    hold_time = (1.0 / clock_rate_hz) / 2
    hold_time_ns = hold_time * SECONDS

    toggle_clock(clk)
    yield Timer(hold_time_ns)
    toggle_clock(clk)
    yield Timer(hold_time_ns)

@cocotb.coroutine
def advance_sim(clk, time_s, clock_rate_hz=4, first_step_action=None):
    num_steps = time_s * clock_rate_hz

    for _ in range(num_steps):
        yield single_step_sim(clk, clock_rate_hz)
        if first_step_action is not None:
            print("Running action")
            first_step_action.__call__()
            first_step_action = None

@cocotb.coroutine
def bring_out_of_reset(clk, reset):
    reset.value = 1
    yield single_step_sim(clk)
    reset.value = 0
    yield single_step_sim(clk)

@cocotb.coroutine
def change_to_state_to_green(dut):
    yield bring_out_of_reset(dut.clk, dut.reset)

    lights_status = dut.lights.value.binstr
    if lights_status != "001":
        raise TestFailure("Precondition not met: light should be green (001)"
                          " but it was acutally {}".format(lights_status))

@cocotb.coroutine
def change_to_state_to_amber(dut):
    yield bring_out_of_reset(dut.clk, dut.reset)
    dut.wait_btn.value = 1
    yield single_step_sim(dut.clk)
    dut.wait_btn.value = 0

    yield advance_sim(dut.clk, 1)
    yield single_step_sim(dut.clk)

    if dut.wait_btn.value == 1:
        raise TestFailure("Button was still pressed")

    lights_status = dut.lights.value.binstr
    if lights_status != "010":
        raise TestFailure("Precondition not met: light should be amber (010)"
                          " but it was acutally {}".format(lights_status))

@cocotb.coroutine
def change_to_state_to_red(dut):
    yield bring_out_of_reset(dut.clk, dut.reset)
    dut.wait_btn.value = 1
    yield single_step_sim(dut.clk)
    dut.wait_btn.value = 0

    yield advance_sim(dut.clk, 3)

    lights_status = dut.lights.value.binstr
    if lights_status != "100":
        raise TestFailure("Precondition not met: light should be red (100)"
                          " but it was acutally {}".format(lights_status))

@cocotb.coroutine
def change_to_state_to_red_amber(dut):
    yield bring_out_of_reset(dut.clk, dut.reset)
    dut.wait_btn.value = 1
    yield single_step_sim(dut.clk)
    dut.wait_btn.value = 0

    yield advance_sim(dut.clk, 7)

    lights_status = dut.lights.value.binstr
    if lights_status != "110":
        raise TestFailure("Precondition not met: light should be red amber"
                          " (110) but it was acutally {}".format(lights_status))


@cocotb.test()
def given_lightIsGreen_when_buttonIsPressed_then_lightShouldChangeToAmber(dut):
    # Given 
    yield change_to_state_to_green(dut)

    # When
    dut.wait_btn.value = 1
    yield single_step_sim(dut.clk)
    dut.wait_btn.value = 0
        
    yield advance_sim(dut.clk, 1)

    # Then
    lights_status = dut.lights.value.binstr

    if lights_status != "010":
        raise TestFailure("Expected light to be amber (010) but it was actually "
                          "{}".format(lights_status))

@cocotb.test()
def given_lightIsAmber_when_twoSecondsPass_then_lightShouldChangeToRed(dut):
    # Given
    yield change_to_state_to_amber(dut)

    # When
    yield advance_sim(dut.clk, 2)

    # Then
    lights_status = dut.lights.value.binstr

    if lights_status != "100":
        raise TestFailure("Expected light to be red (100) but it was actually"
                          " {}".format(lights_status))

@cocotb.test()
def given_lightIsAmber_when_twoSecondsHasNotPassed_then_lightShouldStayAmber(dut):
    # Given
    yield change_to_state_to_amber(dut)

    # Then
    lights_changed = Edge(dut.lights)
    timeout_expired = Timer(1.9 * SECONDS)
    result = yield [lights_changed, timeout_expired]

    if result is lights_changed:
        raise TestFailure("Lights changed before they were expected to!")

@cocotb.test()
def given_lightIsRed_when_fourSecondsHasPassed_then_lightShouldChangeToRedAmber(dut):
    # Given
    yield change_to_state_to_red(dut)

    # When
    yield advance_sim(dut.clk, 4)

    # Then
    lights_status = dut.lights.value.binstr

    if lights_status != "110":
        raise TestFailure("Expected lights to be red amber (110) but they were"
                          " actually {}".format(lights_status))

@cocotb.test()
def given_lightIsRed_when_fourSecondsHasNotPassed_then_lightShouldStayRed(dut):
    # Given
    yield change_to_state_to_red(dut)

    # When
    lights_changed = Edge(dut.lights)
    timeout_expired = Timer(3.9 * SECONDS)
    result = yield [lights_changed, timeout_expired]

    if result is lights_changed:
        raise TestFailure("Lights changed before there were expected to!")

@cocotb.test()
def given_lightIsRedAmber_when_twoSecondsHasPassed_then_lightShouldChangeToGreen(dut):
    # Given
    yield change_to_state_to_red_amber(dut)

    # When
    yield advance_sim(dut.clk, 2)

    # Then
    lights_status = dut.lights.value.binstr

    if lights_status != "001":
        raise TestFailure("Expected lights to be green (001) but they were"
                          " actually {}".format(lights_status))

@cocotb.test()
def given_lightIsRedAmber_when_twoSecondsHasNotPassed_then_lightShouldStayRedAmber(dut):
    # Given
    yield change_to_state_to_red_amber(dut)

    # When
    lights_changed = Edge(dut.lights)
    timeout_expired = Timer(1.9 * SECONDS)
    result = yield [lights_changed, timeout_expired]

    if result is lights_changed:
        raise TestFailure("Lights changed before they were expected to!")



@cocotb.test()
def given_controllerInReset_then_noLightShouldBeOn(dut):
    # Given
    dut.reset = 1
    yield single_step_sim(dut.clk)

    # Then
    lights_status = dut.lights.value.binstr

    if lights_status != "000":
        raise TestFailure("Expected lights to be off (000) when in reset but"
                          " they were actually {}".format(lights_status))

@cocotb.test()
def given_controllerInReset_when_broughtOutOfReset_then_lightShouldBeGreen(dut):
    # Given
    dut.reset = 1
    yield single_step_sim(dut.clk)

    # When
    dut.reset = 0
    yield single_step_sim(dut.clk)

    lights_status = dut.lights.value.binstr

    if lights_status != "001":
        raise TestFailure("Expected lights to be green (001) when coming out of"
                          " reset but they were actually"
                          " {}".format(lights_status))

