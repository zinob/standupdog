from machine import Timer, UART, Pin
from urequests import get
from umqtt.robust import MQTTClient
import time, micropython

class StandupWatcher():
	def __init__(s,default_interval=600,wait_function=None):
		s.uart = UART(1, 9600)
		s.uart.init(9600, bits=8, parity=None, stop=1)
		s.default_interval = default_interval
		if wait_function != None:
			s.wait_function = wait_function
		else:
			s.wait_function = s._timersleep
			
		#s.wait(default_interval)

	def wait(s,seconds,cb=None):
		if cb == None:
			cb = s.get_net
		s.wait_function(seconds,cb)

	def _timersleep(s,seconds,cb):
		s.timer=Timer(-1)
		s.timer.init(period=seconds*1000, mode=Timer.ONE_SHOT, callback=lambda x:cb())

	def get_net(s):
		try:
			s.check_for_print()
		except:
			s.wait(s.default_interval)
		
	def check_for_print(s):
			r=get("http://ops-senpai.5z.fyi/cgi-bin/status")
			if r.text.startswith("wait"):
				print_in = int(r.text.split(":")[1])
				print("waiting for %i seconds"%print_in)
				s.wait(print_in)
			elif  r.text.startswith("print"):
				print("reading standup")
				r = get("http://ops-senpai.5z.fyi/printout.txt")
				s._read_to_uart(r.raw)
				r.close()
				print("done reading")
				s.wait(s.default_interval)
			else:
				s.wait(s.default_interval)


	def _read_to_uart(s,socket,readsize=10):
		readlen=readsize
		while readlen == readsize:
			time.sleep(.1)
			a=socket.read(readsize)
			readlen = s.uart.write(a)
			print("wrote %i bytes to uart"%readlen)




	def _sub_cb(self,topic, msg):
		print(msg)
		self.uart.write(msg.strip()+b"\n")

	def start_mqtt(self,server="ops-senpai.5z.fyi"):
		c = MQTTClient("dog", "ops-senpai.5z.fyi", port=30001, user="dog", password="x3lespxjdttiqjb5")
		c.set_callback(self._sub_cb)
		c.connect()
		c.subscribe(b"printme")
		try:
			while True:
				# Blocking wait for message
				c.wait_msg()
		finally:
			c.disconnect()


def start_webrepl(_):
	UART(1, 9600).write("Connected at %s \n\n"%network.WLAN(network.STA_IF).ifconfig()[0])

Pin(0,Pin.IN,Pin.PULL_UP).irq(handler=start_webrepl, trigger=Pin.IRQ_FALLING)


