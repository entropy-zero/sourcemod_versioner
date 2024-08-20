import os
from os.path import abspath
import sys
import argparse
from sourcemod_versioner.versioning.repo import Repository
from sourcemod_versioner.data.gameinfo_file import GameInfo
from sourcemod_versioner.data.version_history_file import VersionHistoryFile

def determine_version_change(release_diff, maps_diff):    
    if("major_version" in release_diff):
        return "major"

    if("minor_version" in release_diff or len(maps_diff) > 0):
        return "minor"

    return "patch"

def update_version_tag(previous_version, version_change):
    version_parts = previous_version.split('.')
    major = int(version_parts[0])
    minor = int(version_parts[1])
    patch = int(version_parts[2])    
    
    if(version_change == "major"):
        major = major + 1
        minor = 0
        patch = 0
        return '.'.join([str(major), str(minor), str(patch)])

    if(version_change == "minor"):
        minor = minor + 1
        patch = 0
        return '.'.join([str(major), str(minor), str(patch)])

    patch = patch + 1
    return '.'.join([str(major), str(minor), str(patch)])

def version_tag_to_git_tag(version_tag, game_prefix, release_stage):
    return game_prefix + "_" + release_stage + "-" + version_tag 

def commit_tag_and_push(repository, version_tag, game_prefix, release_stage, summary="") -> int:
    git_tag = version_tag_to_git_tag(version_tag, game_prefix, release_stage)    
    repository.create_commit("{}: {}".format(version_tag, summary) if summary else version_tag)
    tag_object = repository.create_tag(git_tag)
    repository.push([tag_object])

def create_version(repository, gameInfo, ez2_version_history, game_prefix="ez2", release_stage="release", summary="") -> int:
    # Get the version number
    previous_version = gameInfo.GetKeyValue('ez2_version')

    # Check if there are outstanding changes and exit if there are
    if(repository.has_unstaged_changes()):
        print("Repository has outstanding changes! Exiting create_version...")
        return 1

    # Gather changes
    release_diff = repository.get_diff_with_tag(version_tag_to_git_tag(previous_version, game_prefix, release_stage))
    print("Release diff:", release_diff)
    maps_diff = [os.path.splitext(os.path.basename(file))[0] for file in release_diff if '.vmf' in file or '.vmm' in file]
    print("Maps diff:", maps_diff)

    # Determine automatic semantic version
    version_change = determine_version_change(release_diff, maps_diff)
    version_tag = update_version_tag(previous_version, version_change)
    minor_version_string = '.'.join(version_tag.split('.')[0:2])
    
    # Update version history file
    if(version_change == "minor" or version_change == "major"):
        version_history_object = { "branch" : "{}-{}".format(release_stage, minor_version_string), "universal" : 1 if version_change == "major" else "0", "maps" : { mapname : "1" for mapname in maps_diff}}
        ez2_version_history.ReplaceKeyValue(minor_version_string, version_history_object)
        ez2_version_history.SaveToFile()

    # Update gameinfo.txt with version
    # ez2_version is hard coded - it does not update to the game prefix
    gameInfo.ReplaceKeyValue('ez2_version', version_tag)
    gameInfo.SaveToFile()

    repository.add_files([gameInfo.GetFilepath(), ez2_version_history.GetFilepath()])

    if(version_change == "major"):
        major_version_filepath=os.path.join(repository.get_filepath(), 'major_version')
        try:
            os.remove(major_version_filepath)
            repository.remove_files([major_version_filepath])
        except FileNotFoundError:
            print("Could not remove file '{}' because the file could not be found.".format(major_version_filepath))

    if(version_change == "minor"):
        minor_version_filepath=os.path.join(repository.get_filepath(), 'minor_version')
        try:
            os.remove(minor_version_filepath)
            repository.remove_files([minor_version_filepath])
        except FileNotFoundError:
            print("Could not remove file '{}' because the file could not be found.".format(minor_version_filepath))


    return commit_tag_and_push(repository, version_tag, game_prefix, release_stage, summary)

def main():
    print("Running script: " + sys.argv[0])

    parser=argparse.ArgumentParser(description="Version creation for source mods")
    parser.add_argument("--game", nargs='?', default="")
    parser.add_argument("--summary", nargs='?', default="")
    parser.add_argument("--prefix", nargs='?', default="ez2")
    parser.add_argument("--phase", nargs='?', default="release")
    parser.add_argument("--dryrun", action=argparse.BooleanOptionalAction)
    args=parser.parse_args()

    if not args.game:
        print("Missing --game argument")
        return 1

    repo_path = abspath(args.game)
    print("Game path: {}".format(repo_path))

    gameinfo_path = os.path.join(repo_path, "gameinfo.txt")
    versionhistory_path = os.path.join(repo_path, "scripts/ez2_version_history.txt")

    # Setup repo
    repository = Repository()
    repository.initialize(repo_path)
    repository.set_dry_run(args.dryrun)

    # Load gameinfo file
    # TODO - Add handling for missing gameinfo file
    gameInfo = GameInfo(gameinfo_path)
    gameInfo.LoadFromFile()

    # Load version history file
    # TODO - Add handling for missing version history file
    ez2_version_history = VersionHistoryFile(versionhistory_path)
    ez2_version_history.LoadFromFile()

    return create_version(repository, gameInfo, ez2_version_history, game_prefix=args.prefix, release_stage=args.phase, summary=args.summary)

if __name__ == '__main__':
    sys.exit(main())