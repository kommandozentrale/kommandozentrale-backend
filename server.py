import yaml
import os

if __name__ == '__main__':
	assert os.path.isfile("config.yml"), "You need to create a \"config.yml\""
	with open("config.yml") as configfile:
		config = yaml.load(configfile)
	print(config)