import vdf

class VersionHistoryFile:
    def __init__(self, filepath=""):
        self.versionHistoryData = None
        self.filepath = filepath

    def LoadFromFile(self):
        f = open(self.filepath,'r')
        filedata = f.read()
        f.close()

        filedata = filedata.replace("+", "\\PLUS\\")
        filedata = filedata.replace("|", "\\PIPE\\")

        self.versionHistoryData = vdf.loads(filedata, mapper=vdf.VDFDict)
    def SaveToFile(self):
        f = open(self.filepath,'w')

        vdf.dump(self.versionHistoryData, f, pretty=True)
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

    def GetversionHistoryData(self):
        return self.versionHistoryData

    def GetKeyValue(self, key):
        return self.versionHistoryData["VersionHistory"][key]

    def GetFilepath(self):
        return self.filepath
    
    def ReplaceKeyValue(self, key, value):
        self.versionHistoryData["VersionHistory"].remove_all_for(key)
        self.versionHistoryData["VersionHistory"][key] = value