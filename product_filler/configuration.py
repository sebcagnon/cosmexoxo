import os
import json

class Configuration(object):
  """A class that handles the configuration files and data"""
  
  def __init__(self, appFolder, configFile):
    self.dataPath = os.getenv('LOCALAPPDATA')
    self.appFolder = appFolder
    self.configFile = configFile
    self.filePath = os.path.join(self.dataPath, self.appFolder, self.configFile)
    self.config = {}
    self.loadConfig()

  def loadConfig(self):
    """Loads the configuration file"""
    try:
      with open(self.filePath, 'r') as f:
        self.config = json.load(f)
    except IOError:
      print 'No config available, will create new one'
      directory = os.path.join(self.dataPath, self.appFolder)
      if not os.path.exists(directory):
        os.makedirs(directory)

  def saveConfig(self):
    """Saves the current configuration variable into the configuration file"""
    try:
      with open(self.filePath, 'w') as f:
        f.write(json.dumps(self.config))
    except IOError:
      print "Couldn't open config file for writing"

  def get(self, key):
    """Gets a config variable or returns None if doesn't exit"""
    return self.config.get(key, None)

  def set(self, key, value):
    """Sets a key/value pair in the configuration file ans saves"""
    self.config[key] = value
    self.saveConfig()