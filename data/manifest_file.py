import vdf

class Manifest:
    def __init__(self, filepath=""):
        self.manifestData = None
        self.mapData = None
        self.filepath = filepath

    def LoadFromFile(self):
        f = open(self.filepath,'r')
        filedata = f.read()
        f.close()

        filedata = filedata.replace("+", "\\PLUS\\")
        filedata = filedata.replace("|", "\\PIPE\\")

        self.manifestData = vdf.loads(filedata, mapper=vdf.VDFDict)
    def SaveToFile(self):
        f = open(self.filepath,'w')

        vdf.dump(self.manifestData, f, pretty=True)
        f.close()

        f = open(self.filepath,'r')
        newdata = f.read()
        f.close()
        newdata = newdata.replace("\\PLUS\\", "+")
        newdata = newdata.replace("\\PIPE\\", "|")
        newdata = newdata.replace("\\+\\", "+")
        newdata = newdata.replace("\\|\\", "|")
        newdata = newdata.replace("\\+", "+")
        newdata = newdata.replace("\\|", "|")
        f = open(self.filepath,'w')
        f.write(newdata)
        f.close()

    def SaveToMapFile(self, filepath):
        self.mapData = vdf.VDFDict()
        
        for key, values in self.manifestData["Maps"].items():
            print("Key: " + str(key))
            print("Value: " + str(values))
            for map_filepath in values.get_all_for("File"):
                print("Map: " + str(map_filepath))
                entityData = vdf.VDFDict()
                entityData["classname"] = "func_instance"
                # TODO - Need to fix up path relative to VMF file
                entityData["file"] = map_filepath
                # TODO - Need to fixup targetname to only the filename part
                entityData["name"] = map_filepath
                self.mapData['entity'] = entityData
        
        f = open(filepath,'w')

        vdf.dump(self.mapData, f, pretty=True)
        f.close()

        f = open(filepath,'r')
        newdata = f.read()
        f.close()
        newdata = newdata.replace("\\PLUS\\", "+")
        newdata = newdata.replace("\\PIPE\\", "|")
        newdata = newdata.replace("\\+\\", "+")
        newdata = newdata.replace("\\|\\", "|")
        newdata = newdata.replace("\\+", "+")
        newdata = newdata.replace("\\|", "|")
        f = open(filepath,'w')
        f.write(newdata)
        f.close()


    def GetManifestData(self):
        return self.manifestData

    def GetKeyValue(self, key):
        return self.manifestData[key]

    def GetFilepath(self):
        return self.filepath
    
    def ReplaceKeyValue(self, key, value):
        self.manifestData.remove_all_for(key)
        self.manifestData[key] = value