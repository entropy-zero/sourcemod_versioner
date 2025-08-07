import vdf

class AutoCubemapFile:
    def __init__(self, filepath=""):
        self.autoCubemapData = vdf.loads('"AutoCubemap"{}', mapper=vdf.VDFDict)
        self.filepath = filepath

    def LoadFromFile(self):
        f = open(self.filepath,'r')
        filedata = f.read()
        f.close()

        filedata = filedata.replace("+", "\\PLUS\\")
        filedata = filedata.replace("|", "\\PIPE\\")

        self.autoCubemapData = vdf.loads(filedata, mapper=vdf.VDFDict)
    def SaveToFile(self):
        f = open(self.filepath,'w')

        vdf.dump(self.autoCubemapData, f, pretty=True)
        f.close()

        f = open(self.filepath,'r')
        newdata = f.read()
        f.close()
        newdata = newdata.replace("\\PLUS\\", "+")
        newdata = newdata.replace("\\PIPE\\", "|")
        newdata = newdata.replace("\\+\\", "+")
        newdata = newdata.replace("\\|\\", "|")
        newdata = newdata.replace("\\+", "+")
        f = open(self.filepath,'w')
        f.write(newdata)
        f.close()

    def GetAutoCubemapData(self):
        return self.autoCubemapData

    def GetKeyValue(self, key):
        return self.autoCubemapData["AutoCubemap"][key]

    def GetFilepath(self):
        return self.filepath
    
    def ReplaceKeyValue(self, key, value):
        self.autoCubemapData["AutoCubemap"].remove_all_for(key)
        self.autoCubemapData["AutoCubemap"][key] = value