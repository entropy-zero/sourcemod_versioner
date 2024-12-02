import argparse
import os
from os.path import abspath
import subprocess
import sys
from sourcemod_versioner.versioning.game_version import GameVersion
from sourcemod_versioner.versioning.repo import Repository
from sourcemod_versioner.data.gameinfo_file import GameInfo


def compile_maps(repository, gameInfo, binpath, game_prefix="ez2", release_stage="release", summary="") -> int:
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

    vmf_paths_diff_no_instances = [file for file in vmf_paths_diff if 'instance_' not in file]

    vbsp_command = os.path.join(binpath, "vbsp.exe")
    vvis_command = os.path.join(binpath, "vvis.exe")
    vrad_command = os.path.join(binpath, "vrad.exe")

    gamepath = os.path.dirname(gameInfo.GetFilepath())
    mapspath = abspath(os.path.join(gamepath, "maps"))

    for vmf_path in vmf_paths_diff_no_instances:
        subprocess.check_call([vbsp_command, "-game", gamepath, vmf_path])
        subprocess.check_call([vvis_command, "-game", gamepath, vmf_path])
        subprocess.check_call([vrad_command, "-both", "-final", "-game", os.path.dirname(gameInfo.GetFilepath()), vmf_path])
        bsp_source_path = os.path.splitext(vmf_path)[0] + ".bsp"
        bsp_dest_path = abspath(os.path.join(mapspath, os.path.splitext(os.path.basename(vmf_path))[0])) + ".bsp"
        subprocess.check_call(["cp", bsp_source_path, bsp_dest_path])

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

    return compile_maps(repository, gameInfo, binpath, game_prefix=args.prefix, release_stage=args.phase, summary=args.summary)

if __name__ == '__main__':
    sys.exit(main())