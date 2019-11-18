import audio
import sensor
import image
import lcd
import time
import utime
import KPU as kpu

from fpioa_manager import fm
from machine import I2C
from Maix import I2S, GPIO

fm.register(board_info.LED_B, fm.fpioa.GPIO6)
led_b = GPIO(GPIO.GPIO6, GPIO.OUT)
led_b.value(1) #RGBW LEDs are Active Low

i2c = I2C(I2C.I2C0, freq=400000, scl=28, sda=29)

fm.register(board_info.SPK_SD, fm.fpioa.GPIO0)
spk_sd=GPIO(GPIO.GPIO0, GPIO.OUT)
spk_sd.value(1) #Enable the SPK output

fm.register(board_info.SPK_DIN,fm.fpioa.I2S0_OUT_D1)
fm.register(board_info.SPK_BCLK,fm.fpioa.I2S0_SCLK)
fm.register(board_info.SPK_LRCLK,fm.fpioa.I2S0_WS)

wav_dev = I2S(I2S.DEVICE_0)

def play_sound(filename):
    try:
        player = audio.Audio(path = filename)
        player.volume(100)
        wav_info = player.play_process(wav_dev)
        wav_dev.channel_config(wav_dev.CHANNEL_1, I2S.TRANSMITTER,resolution = I2S.RESOLUTION_16_BIT, align_mode = I2S.STANDARD_MODE)
        wav_dev.set_sample_rate(wav_info[1])
        while True:
            ret = player.play()
            if ret == None:
                break
            elif ret==0:
                break
        player.finish()
    except:
        pass

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
#f=open('/sd/labels.txt','r')
#labels=f.readlines()
#f.close()
labels=["absence","bad_pose","good_pose"]

print(labels)

# kmodelをKPUにロードする
task = kpu.load('/sd/model.kmodel')

clock = time.clock()
print("load model")

keep_cnt = 0
is_noticed = False

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
    print("%.2f:%s", pmax, max_label)
    lcd.display(img)
    #print(fps)

    if 1 == max_index and pmax > 0.8:
        led_b.value(0)
        keep_cnt += 1
        if keep_cnt > 10 : keep_cnt = 10

    else:
        led_b.value(1)
        keep_cnt = 0
        is_noticed = False

    print(keep_cnt)
    if keep_cnt >= 10 and is_noticed == False:
        is_noticed = True
        play_sound("/sd/voice/notice_bad_pose.wav")


kpu.deinit(task)
