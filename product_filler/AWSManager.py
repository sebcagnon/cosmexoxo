import boto

class AWSManager(object):
  """Class that handles the connection, upload and download of S3 objects"""
  CONNECTED = "connected"
  DISCONNECTED = "disconnected"

  def __init__(self, bucketName, **connectionArgs):
    """Connection information must be passed as keyword arguments"""
    self.bucketName = bucketName
    self.connectionArguments = connectionArgs
    self.bucket = None
    self.s3 = None
    self.connectionStatus = self.DISCONNECTED

  def connect(self):
    """Connects to S3 instance and initializes bucket"""
    if self.connectionStatus != self.CONNECTED:
      self.s3 = boto.connect_s3(**self.connectionArguments)
      self.bucket = self.s3.get_bucket(self.bucketName)
      self.connectionStatus = self.CONNECTED

  def disconnect(self):
    """Closes connection to S3 instance"""
    if self.connectionStatus != self.DISCONNECTED:
      self.s3.close()
      self.bucket = None
      self.connectionStatus = self.DISCONNECTED


if __name__=='__main__':
  import argparse
  import json
  parser = argparse.ArgumentParser(description='Tests for AWSManager')
  parser.add_argument('jsonFile', type=argparse.FileType('r'))
  args = parser.parse_args()
  data = json.load(args.jsonFile)
  awsMgr = AWSManager(data['s3_bucket'], **data['aws_access_key'])
  awsMgr.connect()
  assert awsMgr.connectionStatus == awsMgr.CONNECTED, 'Connection failure'
  print 'Connected'
  awsMgr.disconnect()
  assert awsMgr.connectionStatus == awsMgr.DISCONNECTED, \
                       'Disconnection failure'
  print 'Disconnected'
  print 'All Tests Passed'
  
  