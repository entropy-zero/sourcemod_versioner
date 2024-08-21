import vdf

class GameInfo:
    def __init__(self, filepath=""):
        self.gameInfoData = None
        self.filepath = filepath

    def LoadFromFile(self):
        f = open(self.filepath,'r')
        filedata = f.read()
        f.close()

        filedata = filedata.replace("+", "\\PLUS\\")
        filedata = filedata.replace("|", "\\PIPE\\")

        self.gameInfoData = vdf.loads(filedata, mapper=vdf.VDFDict)
    def SaveToFile(self):
        f = open(self.filepath,'w')

        vdf.dump(self.gameInfoData, f, pretty=True)
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

    def GetGameInfoData(self):
        return self.gameInfoData

    def GetKeyValue(self, key):
        return self.gameInfoData["GameInfo"][key]

    def GetFilepath(self):
        return self.filepath
    
    def ReplaceKeyValue(self, key, value):
        self.gameInfoData["GameInfo"].remove_all_for(key)
        self.gameInfoData["GameInfo"][key] = value