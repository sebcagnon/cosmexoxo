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

  def uploadImage(self, keyName, imagePath, **metadata):
    """Uploads the image from file to bucket"""
    if self.connectionStatus != self.CONNECTED:
      raise AWSManagerError('Cannot upload image if not connected')
    key = self.bucket.new_key(keyName)
    for k,v in metadata.items():
      key.set_metadata(k, v)
    key.set_contents_from_filename(imagePath)

  def getImageFromName(self, keyName, destinationFile):
    """Returns True if image was downloaded to destFile, False otherwise"""
    if self.connectionStatus != self.CONNECTED:
      raise AWSManagerError('Cannot download image if not connected')
    key = self.bucket.get_key(keyName)
    if key:
      key.get_contents_to_filename(destinationFile)
      return True
    else:
      return False

  def deleteKey(self, keyName):
    """Deletes keyName key"""
    if self.connectionStatus != self.CONNECTED:
      raise AWSManagerError('Cannot delete key image if not connected')
    self.bucket.delete_key(keyName)


class AWSManagerError(BaseException):
  """Error raised when trying to use a disconnected AWSManager"""

  def __init__(self, value):
    self.value = value

  def __str__(self):
    return repr(self.value)


if __name__=='__main__':
  import argparse
  import json
  import hashlib
  import os
  parser = argparse.ArgumentParser(description='Tests for AWSManager')
  parser.add_argument('jsonFile', type=argparse.FileType('r'))
  args = parser.parse_args()
  data = json.load(args.jsonFile)
  try:
    # Testing creation and connection
    awsMgr = AWSManager(data['s3_bucket'], **data['aws_access_key'])
    awsMgr.connect()
    assert awsMgr.connectionStatus == awsMgr.CONNECTED, 'Connection failure'
    print 'Connected'

    # Testing upload and download image
    testImgFileName = 'resources/placeholder.png'
    fileName2 = 'resources/placeholder2.png'
    originalHash = hashlib.sha256(open(testImgFileName, 'rb').read()).digest()
    testKey = 'test_img'
    metadata = {'title':'test'}
    assert awsMgr.getImageFromName('dfklajfnejcdjka', fileName2) == False, \
                         'getImageFromName should return false for fake keys'
    awsMgr.uploadImage(testKey, testImgFileName, **metadata)
    key = awsMgr.bucket.get_key(testKey)
    assert key != None, 'uploadImage: key was not created'
    assert key.metadata == metadata, 'uploadImage metadata was not saved'
    assert awsMgr.getImageFromName(testKey, fileName2) == True, \
                         'getImageFromName should return True on success'
    newHash = hashlib.sha256(open(fileName2, 'rb').read()).digest()
    assert newHash == originalHash, 'image was modified between upload ' \
                                     'and download'
    awsMgr.deleteKey(testKey)
    key = awsMgr.bucket.get_key(testKey)
    assert key == None, 'deleteKey did not delete the key'

    # Testing disconnection handling
    awsMgr.disconnect()
    assert awsMgr.connectionStatus == awsMgr.DISCONNECTED, \
                         'Disconnection failure'
    print 'Disconnected'
    try:
      awsMgr.uploadImage(testKey, testImgFileName, **metadata)
      assert None, 'uploadImage should have raised'
    except AWSManagerError:
      pass
    try:
      awsMgr.getImageFromName(testKey, fileName2)
      assert None, 'getImageFromName should have raised'
    except AWSManagerError:
      pass
    try:
      awsMgr.deleteKey(testKey)
      assert None, 'deleteKey should have raised'
    except AWSManagerError:
      pass
  finally:
    if os.path.exists(fileName2):
      os.remove(fileName2)

  print 'All Tests Passed'