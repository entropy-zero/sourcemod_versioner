import argparse
import os
from os.path import abspath
import subprocess
import sys
from sourcemod_versioner.versioning.game_version import GameVersion
from sourcemod_versioner.versioning.repo import Repository
from sourcemod_versioner.data.gameinfo_file import GameInfo
from sourcemod_versioner.data.autocubemap_file import AutoCubemapFile

def compile_maps(repository, gameInfo, binpath, game_prefix="ez2", release_stage="release", summary="", autocubemap_file=None) -> int:
    # Get the version number
    previous_version = gameInfo.GetKeyValue('ez2_version')
    game_version = GameVersion(previous_version, game_prefix, release_stage)

    # Gather changes
    release_diff = repository.get_diff_with_tag(str(game_version))
    print("Release diff:", release_diff)
    vmf_names_diff = [os.path.splitext(os.path.basename(file))[0] for file in release_diff if '.vmf' in file or '.vmm' in file]
    print("Map names diff:", vmf_names_diff)
    vmf_paths_diff = [file for file in release_diff if '.vmf' in file or '.vmm' in file]
    print("Map paths diff:", vmf_paths_diff)

    vmf_names_diff_no_instances = [file for file in vmf_names_diff if 'instance_' not in file and 'prefabs' not in file]
    vmf_paths_diff_no_instances = [file for file in vmf_paths_diff if 'instance_' not in file and 'prefabs' not in file]

    vbsp_command = os.path.join(binpath, "vbsp.exe")
    vvis_command = os.path.join(binpath, "vvis.exe")
    vrad_command = os.path.join(binpath, "vrad.exe")

    gamepath = os.path.dirname(gameInfo.GetFilepath())
    mapspath = abspath(os.path.join(gamepath, "maps"))

    errors = []

    for vmf_path in vmf_paths_diff_no_instances:
        try:
            print("Running compile process for VMF path: " + vmf_path)
            subprocess.check_call([vbsp_command, "-game", gamepath, vmf_path])
            subprocess.check_call([vvis_command, "-game", gamepath, vmf_path])
            subprocess.check_call([vrad_command, "-both", "-final", "-game", os.path.dirname(gameInfo.GetFilepath()), vmf_path])
            bsp_source_path = os.path.splitext(vmf_path)[0] + ".bsp"
            bsp_dest_path = abspath(os.path.join(mapspath, os.path.splitext(os.path.basename(vmf_path))[0])) + ".bsp"
            subprocess.check_call(["cp", bsp_source_path, bsp_dest_path])
        except subprocess.CalledProcessError as e:
            print("Process returned nonzero exit code")
            print("Command: "  + str(e.cmd))
            print("Return code: " + str(e.returncode))
            print("Output: " + str(e.output))
            errors.append(e)
    
    # Update version history file
    for vmf_name in vmf_names_diff_no_instances:
        autocubemap_file.ReplaceKeyValue(vmf_name, "1")
    autocubemap_file.SaveToFile()

    if(not errors):
        return 0
    else:
        print("Compile process returned errors! Please see above.")
        return 1


def main():
    print("Running script: " + sys.argv[0])

    parser=argparse.ArgumentParser(description="Version creation for source mods")
    parser.add_argument("--game", nargs='?', default="")
    parser.add_argument("--basegame", nargs='?', default="")
    parser.add_argument("--summary", nargs='?', default="")
    parser.add_argument("--prefix", nargs='?', default="ez2")
    parser.add_argument("--phase", nargs='?', default="release")
    args=parser.parse_args()

    if not args.game:
        print("Missing --game argument")
        return 1

    repo_path = abspath(args.game)
    print("Game path: {}".format(repo_path))

    gameinfo_path = os.path.join(repo_path, "gameinfo.txt")

    if not args.basegame:
        basegame_path =  abspath(os.path.join(repo_path, "..\\..\\common\\EntropyZero2"))
    else:
        basegame_path = abspath(args.basegame)

    binpath = os.path.join(basegame_path, "bin")
    print("Bin path: {}".format(binpath))

    # Setup repo
    repository = Repository()
    repository.initialize(repo_path)
    repository.set_dry_run(True)

    # Load gameinfo file
    # TODO - Add handling for missing gameinfo file
    gameInfo = GameInfo(gameinfo_path)
    gameInfo.LoadFromFile()

    # Create autocubemap file
    autocube_path = os.path.join(repo_path, "tools/autocubemap_ez2.txt")
    autocubemap_ez2 = AutoCubemapFile(autocube_path)

    return compile_maps(repository, gameInfo, binpath, game_prefix=args.prefix, release_stage=args.phase, summary=args.summary, autocubemap_file=autocubemap_ez2)

if __name__ == '__main__':
    sys.exit(main())