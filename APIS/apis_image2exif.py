# -*- coding: utf-8 -*

import pyexiv2, os, sys

class Image2Exif():
    '''
    Image2Exif(metadataDict, imagePath)
    on instantiation this class updates the meta data of imagePath with info from metadataDict
    metadata will be written as 'Xmp.apis.metadata_key'
    '''

    def __init__(self, metadataDict, imagePath):

        self.metadataDict = metadataDict
        self.imagePath = imagePath

        if not os.path.isfile(self.imagePath):
            raise IOError('Was not able to read file {0}'.format(self.imagePath))

        try:
            self.update_metaData()
        except:
            raise IOError('Was not able to set metadata for {0}'.format(self.imagePath))


    def update_metaData(self):
        try:
            metadata = pyexiv2.ImageMetadata(self.imagePath)
            metadata.read()
            try:
                pyexiv2.xmp.register_namespace('/', 'apis')
            except:
                pass
            for k ,v in self.metadataDict.items():
                metadata_key = 'Xmp.apis.{0}'.format(k)
                metadata[metadata_key] = unicode(v)
            metadata.write()
        except Exception, e:
            print "> Error metadata", e
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)


if __name__ == '__main__':
    metadataDict = {}
    metadataDict['bildnummer'] = u"0120140301.001"
    metadataDict['flughoehe'] = 1200
    metadataDict['longitude'] = "16.12345"
    metadataDict['latitude'] = "48.12345"
    metadataDict['fundorte'] = u"AUT.120;AUT.232;AUT.12"
    metadataDict['keyword'] = u"Schlüsselwort"
    metadataDict['description'] = u"Beschreibung"
    metadataDict['projekt'] = u"Projekt A;ProjektB"
    metadataDict['copyright'] = u"IUHA"
    metadataDict['militaernummer'] = u"ABC/1254"
    metadataDict['militaernummer_alt'] = u"ABC 458"
    metadataDict['hersteller'] = u"IUHA"
    metadataDict['kamera'] = u"IUHA"
    metadataDict['kalibrierungsnummer'] = u"IUHA"
    metadataDict['kammerkonstante'] = "150.0"
    metadataDict['fotograf'] = u"Doneus"
    metadataDict['flugdatum'] = u"2014-03-22"
    metadataDict['flugzeug'] = u"C172"
    imagePath = "C:\\Users\\Johannes\\Desktop\\bild.jpg"
    Image2Exif(metadataDict, imagePath)
