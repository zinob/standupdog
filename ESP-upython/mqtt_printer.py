from machine import Timer, UART, Pin
from urequests import get
from umqtt.robust import MQTTClient
import time, micropython

class printMQ():
	def __init__(s,default_interval=600,wait_function=None):
		self.c = MQTTClient("dog", "ops-senpai.5z.fyi", port=30001, user="dog", password="x3lespxjdttiqjb5")
		c.set_callback(self._sub_cb)
		c.connect()
		c.subscribe(b"printme")


	def _sub_cb(self,topic, msg):
		print(msg)
		self.uart.write(msg.strip()+b"\n")

	def start_mqtt(self,server="ops-senpai.5z.fyi"):
		try:
			while True:
				# Blocking wait for message
				c.wait_msg()
		finally:
			c.disconnect()

Pin(0,Pin.IN,Pin.PULL_UP).irq(handler=start_webrepl, trigger=Pin.IRQ_FALLING)


