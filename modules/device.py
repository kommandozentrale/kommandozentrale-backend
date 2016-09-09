class Device():
	name = None
	device_type = None
	public_methods = []

	def __init__(self, **config):
		self.name = config["name"]

	def getName(self):
		assert self.name != None, "Name must be set"
		return self.name