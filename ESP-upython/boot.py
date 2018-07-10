# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
import network,urequests,micropython,webrepl
from machine import Timer

webrepl.start()
micropython.alloc_emergency_exception_buf(100)

network_profiles = (

('CONVENDUM', 'C0nVenduM9701!',network.MODE_11N),
("zTest","healthiest36cleaving",network.MODE_11B),
('Nokia 8 is crappy','deepshrub',network.MODE_11B)
)

network.WLAN(network.AP_IF).active(False)
network.phy_mode(network_profiles[0][2])

class NetKeepAlive():
	def __init__(s, wait_function):
		s.running = True
		s.recon_count = -1
		s.if_profile_number = 0
		
		s.sta_if = network.WLAN(network.STA_IF)
		s.wait_function = wait_function
		s.check_connection()

	def is_connected(s):
		if s.sta_if.isconnected():
			try:
				urequests.get("http://www.google.com")
				return True
			except:
				return False
		return False

	def wait(s,seconds,callback):
		s.timer = s.wait_function(seconds, callback)

	def try_connect(s,_=None):
		if not s.is_connected():
			s.recon_count += 1
			ssid,password,netmode=network_profiles[s.if_profile_number]
			network.phy_mode(netmode)
			s.sta_if.connect(ssid,password)
		
		s.wait(30,s.check_connection)


	def check_connection(s):
		s.running = True
		if s.is_connected():
			s.wait(900,s.check_connection)
			s.recon_count = 0
		else:
			if s.recon_count > 2:
				s.if_profile_number = (1+s.if_profile_number )%len(network_profiles)
			s.try_connect()

	def stop(s):
		if s.running:
			s.timer.deinit()
			s.running=False
	
	def restart(s):
		s.check_connection()

	def __del__(s):
		s.stop()

def timer_wait(seconds,f):
	reconnTimer=Timer(-1)
 	reconnTimer.init(period=seconds*1000,mode=Timer.ONE_SHOT, callback=lambda x:f())
	return reconnTimer

netwatch = NetKeepAlive(timer_wait)

print("Boot done")

import printer
printerprocess=printer.StandupWatcher()
