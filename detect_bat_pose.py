import sensor
import image
import lcd
import time
import utime
import KPU as kpu

from fpioa_manager import fm

fm.register(board_info.LED_R, fm.fpioa.GPIO4)
led_r = GPIO(GPIO.GPIO4, GPIO.OUT)
led_r.value(1) #RGBW LEDs are Active Low

fm.register(board_info.LED_G, fm.fpioa.GPIO5)
led_g = GPIO(GPIO.GPIO5, GPIO.OUT)
led_g.value(1) #RGBW LEDs are Active Low

fm.register(board_info.LED_B, fm.fpioa.GPIO6)
led_b = GPIO(GPIO.GPIO6, GPIO.OUT)
led_b.value(1) #RGBW LEDs are Active Low

def setup():
    img_size = 224 # 上記のセルで IMAGE_SIZE に指定したのと同じ値

    lcd.init()
    lcd.rotation(2)
    sensor.reset()
    sensor.set_pixformat(sensor.RGB565)
    sensor.set_framesize(sensor.QVGA)
    sensor.set_windowing((img_size, img_size)) #キャプチャの段階でサイズを合わせる
    sensor.skip_frames(time = 1000)
    #sensor.set_vflip(0) #flip camera; maix go use sensor.set_hmirror(0)
    sensor.run(1)


setup()

lcd.clear()
lcd.draw_string(0,0,"MobileNet Demo")
lcd.draw_string(0,10,"Loading labels...")

# ラベルファイルの読み込み
f=open('/sd/labels.txt','r')
labels=f.readlines()
f.close()

print(labels)

# kmodelをKPUにロードする
task = kpu.load('/sd/model.kmodel')

clock = time.clock()
print("load model")

leds = [led_r, led_g, led_b]


while True:
    img = sensor.snapshot()
    clock.tick()

    # カメラから取得した画像に対してkmodelによる推論を実行
    fmap = kpu.forward(task, img)
    fps=clock.fps()

    # 結果の中から一番確率が高い物を取得
    plist=fmap[:]
    pmax=max(plist)
    max_index=plist.index(pmax)
    max_label=labels[max_index].strip()

    # 結果を画面に表示
    #img.draw_string(0, 0, "%.2f:%s                            "%(pmax, max_label))
    a = lcd.display(img)
    print(fps)

    for i, led in enumerate(leds):
        if i == max_index and pmax > 0.8:
            led.value(0)
        else:
            led.value(1)

kpu.deinit(task)
