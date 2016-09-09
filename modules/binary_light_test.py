from .binary_light import BinaryLight

class BinaryLightTest(BinaryLight):
	device_type = "binary_light"
	public_methods = ["on", "off"]

	def on(self):
		print("Light {} was turned on".format(self.getName()))

	def off(self):
		print("Light {} was turned off".format(self.getName()))