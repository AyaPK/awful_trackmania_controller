import board
import digitalio
import time
from adafruit_debouncer import Debouncer

# Rotary encoder pins
clk_right = digitalio.DigitalInOut(board.GP22)  # A RIGHT
clk_right.direction = digitalio.Direction.INPUT
clk_right.pull = digitalio.Pull.UP

dt_right = digitalio.DigitalInOut(board.GP26_A0)  # B RIGHT
dt_right.direction = digitalio.Direction.INPUT
dt_right.pull = digitalio.Pull.UP

# Optional: Encoder push button on SW
btn_pin_right = digitalio.DigitalInOut(board.GP15) # Press RIGHT
btn_pin_right.direction = digitalio.Direction.INPUT
btn_pin_right.pull = digitalio.Pull.UP
switch_right = Debouncer(btn_pin_right)

# Rotary encoder pins
clk_left = digitalio.DigitalInOut(board.GP17)  # A LEFT
clk_left.direction = digitalio.Direction.INPUT
clk_left.pull = digitalio.Pull.UP

dt_left = digitalio.DigitalInOut(board.GP16)  # B LEFT
dt_left.direction = digitalio.Direction.INPUT
dt_left.pull = digitalio.Pull.UP

# Optional: Encoder push button on SW
btn_pin_left = digitalio.DigitalInOut(board.GP14) # Press LEFT
btn_pin_left.direction = digitalio.Direction.INPUT
btn_pin_left.pull = digitalio.Pull.UP
switch_left = Debouncer(btn_pin_left)

# Button pins
btn = digitalio.DigitalInOut(board.GP18)
btn.direction = digitalio.Direction.INPUT
btn.pull = digitalio.Pull.UP
btn_switch = Debouncer(btn)

# Track last state of CLK
last_clk_right = clk_right.value
counter_right = 0

last_clk_left = clk_left.value
counter_left = 0

while True:
    switch_right.update()
    switch_left.update()
    btn_switch.update()

    # Handle push button
    if switch_right.fell:
        print("Button Pressed!")
    if switch_right.rose:
        print("Button Released!")

    if switch_left.fell:
        print("Button Pressed!")
    if switch_left.rose:
        print("Button Released!")

    if btn_switch.fell:
        print("Resetting Counter!")
        counter_right = 0
        counter_left = 0

    # Rotary encoder logic
    current_clk_right = clk_right.value
    current_dt_right = dt_right.value

    current_clk_left = clk_left.value
    current_dt_left = dt_left.value

    if current_clk_right != last_clk_right:
        if current_clk_right == False:
            if current_dt_right != current_clk_right:
                counter_right += 1
                print("Rotated Right Clockwise →", counter_right)
            else:
                counter_right -= 1
                print("Rotated Right Counter-Clockwise ←", counter_right)

    if current_clk_left != last_clk_left:
        if current_clk_left == False:
            if current_dt_left != current_clk_left:
                counter_left += 1
                print("Rotated Left Clockwise →", counter_left)
            else:
                counter_left -= 1
                print("Rotated Left Counter-Clockwise ←", counter_left)

    last_clk_right = current_clk_right
    last_clk_left = current_clk_left
    time.sleep(0.001)  # Small debounce
