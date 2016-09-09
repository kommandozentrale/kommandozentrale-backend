from .device import Device

class BinaryLight(Device):
	device_type = "binary_light"
	public_methods = ["on", "off"]

	def on(self): pass

	def off(self): pass