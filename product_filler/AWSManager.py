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
    key.update_metadata(metadata)
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

  def updateName(self, oldName, newName):
    """Changes the key name of an S3 object"""
    if self.connectionStatus != self.CONNECTED:
      raise AWSManagerError('Cannot update name if not connected')
    if oldName == newName:
      return
    newKey = self.bucket.new_key(newName)
    oldKey = self.bucket.get_key(oldName)
    oldKey.copy(self.bucket, newKey, preserve_acl=True)
    oldKey.delete()

  def updateImage(self, name, newImagePath=None, newName=None, 
                       newMetadata=None):
    """Update image from new file, name and/or metadata of a key"""
    if self.connectionStatus != self.CONNECTED:
      raise AWSManagerError('Cannot update image if not connected')
    if not (newImagePath or newName or newMetadata):
      return
    key = self.bucket.get_key(name)
    if newMetadata:
      key.metadata = newMetadata
    if newImagePath:
      key.set_contents_from_filename(newImagePath)
    if newName:
      self.updateName(name, newName)


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
  imagesToErase = []
  try:
    # Testing creation and connection
    awsMgr = AWSManager(data['s3_bucket'], **data['aws_access_key'])
    awsMgr.connect()
    assert awsMgr.connectionStatus == awsMgr.CONNECTED, 'Connection failure'
    print 'Connected'

    # Testing upload and download image
    testImgFileName = 'resources/placeholder.png'
    fileName2 = 'resources/placeholder2.png'
    imagesToErase.append(fileName2)
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

    # Testing change name and update
    newKey1 = 'test_img2'
    awsMgr.updateName(testKey, newKey1)
    key = awsMgr.bucket.get_key(newKey1)
    assert key != None and key.metadata == metadata, 'updateName failed'
    assert awsMgr.bucket.get_key(testKey) == None, 'updateName did not ' \
                       'delete old key' 
    newKey2 = 'test_img3'
    newImg2 = 'resources/plus_icon.gif'
    metadata2 = {'newtitle':'newTest'}
    awsMgr.updateImage(newKey1, newImagePath=newImg2, newName=newKey2,
                       newMetadata=metadata2)
    assert awsMgr.bucket.get_key(newKey1) == None, 'updateImage did not ' \
                       'delete old key'
    key = awsMgr.bucket.get_key(newKey2)
    assert (key != None) and key.metadata == metadata2, 'updateImage failed ' \
                       'to create new key with new metadata'
    oldHash = hashlib.sha256(open(newImg2, 'rb').read()).digest()
    newImg2Copy = 'resources/plus_icon2.gif'
    imagesToErase.append(newImg2Copy)
    awsMgr.getImageFromName(newKey2, newImg2Copy)
    newHash = hashlib.sha256(open(newImg2Copy, 'rb').read()).digest()
    assert oldHash == newHash, 'updateImage failed to update to new image'

    # Testing delete key
    awsMgr.deleteKey(newKey2)
    key = awsMgr.bucket.get_key(newKey2)
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
    try:
      awsMgr.updateName(testKey, newKey1)
      assert None, 'updateName should have raised'
    except AWSManagerError:
      pass
  finally:
    for img in imagesToErase:
      if os.path.exists(img):
        os.remove(img)

  print 'All Tests Passed'