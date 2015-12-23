
import pyexiv2

class Image2Exif:
    '''
    Image2Exif(metadataDict, imagePath)
    on instantiation this class updates the meta data of imagePath with info from metadataDict
    metadata will be written as 'Xmp.apis.metadata_key'
    '''

    def __init__(self, metadataDict, imagePath):

        self.metadataDict = metadataDict
        self.imagePath = imagePath
        try:
            self.update_metaData()
        except:
            raise IOError('Was not able to set metadata for {0}'.format(self.imagePath))


    def update_metaData(self):
        metadata = pyexiv2.ImageMetadata(self.imagePath)
        pyexiv2.xmp.register_namespace('/', 'apis')
        for k,v in self.metadataDict.items():
            metadata_key = 'Xmp.apis.{0}'.format(k)
            metadata[metadata_key] = v
        metadata.write()
