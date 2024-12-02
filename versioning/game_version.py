class GameVersion:
    def __init__(self):
        self._game_prefix = ""
        self._release_stage = ""
        self._version_major = -1
        self._version_minor = -1
        self._version_patch = -1

    def __init__(self,version_tag, game_prefix, release_stage):
        version_numbers = version_tag.split(".")
        self._version_major = int(version_numbers[0])
        self._version_minor = int(version_numbers[1])
        self._version_patch = int(version_numbers[2])
        self._game_prefix = game_prefix
        self._release_stage = release_stage

    def update_version(self,version_change):        
        if(version_change == "major"):
            self._version_major = self._version_major + 1
            self._version_minor = 0
            self._version_patch = 0
            return

        if(version_change == "minor"):
            self._version_minor = self._version_minor + 1
            self._version_patch = 0
            return

        self._version_patch = self._version_patch + 1
        return
    
    def get_version_tag(self):
        return str(self._version_major) + "." + str(self._version_minor) + "." + str(self._version_patch)
    
    def get_minor_version_tag(self):
        return str(self._version_major) + "." + str(self._version_minor)

    def __str__(self):
        return self._game_prefix + "_" + self._release_stage + "-" + self.get_version_tag()
    
    def __repr__(self):
        return self._game_prefix + "_" + self._release_stage + "-" + self.get_version_tag()