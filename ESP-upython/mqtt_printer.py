# vim: set ts=3:sw=3
from machine import Timer, UART, Pin
from urequests import get
from umqtt.robust import MQTTClient
import time, micropython

class printMQ():
	def __init__(s,default_interval=600,wait_function=None):
		mqttpass=open("mqttpass.txt").read().strip()
		self.c = MQTTClient("dog", "ops-senpai.5z.fyi", port=30001, user="dog", password=mqttpass)
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

