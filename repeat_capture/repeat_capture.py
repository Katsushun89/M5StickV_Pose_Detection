import sensor
import image
import lcd
import os
import utime

from fpioa_manager import fm

#Button A
fm.register(board_info.BUTTON_A, fm.fpioa.GPIO1)
btn_a = GPIO(GPIO.GPIO1, GPIO.IN, GPIO.PULL_UP)

#LED Blue
fm.register(board_info.LED_B, fm.fpioa.GPIO6)
led_b = GPIO(GPIO.GPIO6, GPIO.OUT)
led_b.value(1)

is_push_btn_a = 0

is_requested_cap = 0
INTERVAL_TIME = 1000 * 10
pre_cap_time = 0

is_enable_rec = False

lcd.init()
lcd.rotation(2)
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.run(1)

path = "save/"
ext = ".jpg"
cnt = 0
image_read = image.Image()

x_pos = 260
y_pos = 170
radius = 10

while True:
    current_time = utime.ticks_ms()

    img=sensor.snapshot()

    if current_time - pre_cap_time > 5:
        led_b.value(1)

    if current_time - pre_cap_time > INTERVAL_TIME:
        pre_cap_time = current_time
        if is_enable_rec:
            is_requested_cap = 1
            #led_b.value(0)
            #print(pre_cap_time)

    if is_requested_cap == 1 and is_push_btn_a == 0:
        print("save image")
        cnt += 1
        fname = path + str(cnt) + ext
        print(fname)
        img.save(fname, quality=95)
        is_push_btn_a = 1
        is_requested_cap = 0

    if btn_a.value() == 0 and is_push_btn_a == 0:
        print("hoge")
        print(is_enable_rec)
        is_push_btn_a = 1
        is_enable_rec != is_enable_rec
        if is_enable_rec:
            is_enable_rec = False
            print("disable rec")
        else:
            is_enable_rec = True
            print("enable rec")

    if btn_a.value() == 1 and is_push_btn_a == 1:
        is_push_btn_a = 0

    if is_enable_rec == True:
        img.draw_circle(x_pos, y_pos, radius, color = (255, 0, 0), thickness = 1, fill = True)

    lcd.display(img)
