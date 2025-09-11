import os
from os.path import abspath
import sys
import argparse
from sourcemod_versioner.versioning.game_version import GameVersion
from sourcemod_versioner.versioning.repo import Repository
from sourcemod_versioner.data.gameinfo_file import GameInfo
from sourcemod_versioner.data.version_history_file import VersionHistoryFile

def determine_version_change(release_diff, maps_diff):    
    if("major_version" in release_diff):
        return "major"

    if("minor_version" in release_diff or len(maps_diff) > 0):
        return "minor"

    return "patch"

def commit_tag_and_push(repository, version, summary="") -> int:
    repository.create_commit("{}: {}".format(version.get_version_tag(), summary) if summary else version.get_version_tag())
    tag_object = repository.create_tag(str(version))
    repository.push([tag_object])

def document_version(repository, gameInfo, ez2_version_history, game_prefix="ez2", release_stage="release", summary="", old_version_string="", output_filepath="", new_version_string="HEAD") -> int:
    # If the old version is not specified, use the gameinfo.txt version
    if(old_version_string == ""):
        old_version_string = gameInfo.GetKeyValue('ez2_version')
    old_game_version = GameVersion(old_version_string.replace(game_prefix + "_" + release_stage + "-", ""), game_prefix, release_stage)

    # # Check if there are outstanding changes and exit if there are
    # if(repository.has_unstaged_changes()):
    #     print("Repository has outstanding changes! Exiting create_version...")
    #     return 1

    # Gather changes
    release_diff = repository.get_diff_with_tag(str(old_game_version))
    print("Release diff:", release_diff)
    vmf_names_diff = [os.path.splitext(os.path.basename(file))[0] for file in release_diff if '.vmf' in file or '.vmm' in file]
    print("Map names diff:", vmf_names_diff)
    vmf_paths_diff = [file for file in release_diff if '.vmf' in file or '.vmm' in file]
    print("Map paths diff:", vmf_paths_diff)
    asset_paths_diff = [file for file in release_diff if not '.vmf' in file and not '.vmm' in file and not 'gameinfo.txt' in file]
    print("Asset paths diff:", asset_paths_diff)

    vmf_names_diff_no_instances = [file for file in vmf_names_diff if 'instance_' not in file and 'prefabs' not in file]
    vmf_paths_diff_no_instances = [file for file in vmf_paths_diff if 'instance_' not in file and 'prefabs' not in file]

    output_string = "# Changelog\n"
 
    output_string = output_string + "\n## Code Changes\n"
    output_string = output_string + "\n**Read the code changelog on our GitHub here**: https://github.com/entropy-zero/source-sdk-2013/compare/" + str(old_game_version) + "..." + new_version_string + "\n"

    output_string = output_string + "\n## Other Changes Summarized\n"
    output_string = output_string + "\n* " + repository.log(str(old_game_version)).replace("\n", "\n* ")


    if(vmf_names_diff_no_instances and len(vmf_names_diff_no_instances) > 0):
        output_string = output_string + "\n\n## Maps Changed\n"
        chapters_dict = {}

        for file in vmf_names_diff_no_instances:
            if(game_prefix + "_c" not in file):
                if("Other" not in chapters_dict):
                    chapters_dict["Other"] = []
                chapters_dict["Other"].append(file)
            else:
                chapter_title = "Chapter " + file.replace(game_prefix + "_c", "")[0]
                if(chapter_title not in chapters_dict):
                    chapters_dict[chapter_title] = []
                chapters_dict[chapter_title].append(file)

        for chapter_name in chapters_dict:
            chapter_list = chapters_dict[chapter_name]
            output_string = output_string + "\n### " + chapter_name + "\n"
            output_string = output_string + '\n'.join(['* ' + file for file in chapter_list])            

    # Write file with all recently edited maps
    if output_filepath:
        f = open(output_filepath,'w')
        f.write(output_string)
        f.close() 

    return 0

def main():
    print("Running script: " + sys.argv[0])

    parser=argparse.ArgumentParser(description="Version documentation for source mods")
    parser.add_argument("--game", nargs='?', default="")
    parser.add_argument("--summary", nargs='?', default="")
    parser.add_argument("--prefix", nargs='?', default="ez2")
    parser.add_argument("--phase", nargs='?', default="release")
    parser.add_argument("--old_version", nargs='?', default="")
    parser.add_argument("--output_filepath", nargs='?', default="")
    parser.add_argument("--new_version", nargs='?', default="HEAD")    
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

    return document_version(repository, gameInfo, ez2_version_history, game_prefix=args.prefix, release_stage=args.phase, summary=args.summary, old_version_string=args.old_version, output_filepath=args.output_filepath, new_version_string=args.new_version)

if __name__ == '__main__':
    sys.exit(main())