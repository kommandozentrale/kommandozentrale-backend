class Device():
	name = None
	device_type = None
	pubic_methods = []

	def __init__(self, **config):
		self.name = config["name"]