import json
import os
from os.path import abspath
import shutil
import subprocess
import sys
import argparse
from git import Repo
import vdf

def main():
    print("Running script: " + sys.argv[0])

    parser=argparse.ArgumentParser(description="Wrapper script to automate steam publication")
    parser.add_argument("--games_file", nargs='?', default="")
    parser.add_argument("--working_directory", nargs='?', default="")
    parser.add_argument("--launchpad_directory", nargs='?', default="")
    parser.add_argument("--appid", nargs='?', default="1583720")
    parser.add_argument("--dryrun", action=argparse.BooleanOptionalAction)
    args=parser.parse_args()

    if not args.games_file:
        print("Missing --games_file argument")
        return 1
    
    if not args.working_directory:
        working_directory = os.path.join(os.getcwd(), "work")
    else:
        working_directory = abspath(args.working_directory)

    if not args.launchpad_directory:
        launchpad_directory = abspath(os.getcwd())
    else:
        launchpad_directory = abspath(args.launchpad_directory)
    
    games_filepath = abspath(args.games_file)
    games = {}
    with open(games_filepath, mode="r", encoding="utf-8") as read_file:
        games = json.load(read_file)

    print(games)

    changes_to_publish = False
    latest_private_versions = {}
    latest_public_versions = {}
    builds_to_copy = {}

    ##################################################
    # Automated version build loop
    ##################################################
    for game_key,game_value in games.items():
        repo_dir = os.path.join(working_directory, game_value["name"])
        latest_version_filepath = os.path.join(repo_dir, "latest_version.txt")
        if not os.path.isdir(repo_dir):
            print("Cloning repo ", repo_dir, "from remote ", game_value["repo_url"])
            repo = Repo.clone_from(game_value["repo_url"], repo_dir)
        else:
            print("Repo already exists at path: ", repo_dir)
            repo = Repo(repo_dir)
        
        # Store old version tag
        with open(latest_version_filepath, mode="r", encoding="utf-8") as latest_vesion_file:
                old_tag = latest_vesion_file.read().strip()

        if args.dryrun:
            print("Would have run: automated-package-build.sh")
        else:
            os.chdir(repo_dir)
            print(subprocess.run(["sh",os.path.join(repo_dir, "automated-package-build.sh")], 
                     capture_output=True))
            with open(latest_version_filepath, mode="r", encoding="utf-8") as latest_vesion_file:
                new_tag = latest_vesion_file.read().strip()

            print("Got new tag:", new_tag)
            
            # Public depots also get added to private builds, but not the reverse!
            latest_private_versions[game_key] = new_tag
            if game_value["visibility"] == "public":
                latest_public_versions[game_key] = new_tag

            if old_tag == new_tag:
                print(game_key, "had no version changes")
            else:
                print(game_key, "is now version", new_tag)
                builds_to_copy[os.path.join(working_directory, new_tag)] = os.path.join(launchpad_directory, game_value["launchpad_directory"])
                changes_to_publish = True

    if not changes_to_publish:
        print("No changes to publish!")
        return 0
    else:
        ##################################################
        # Update VDF files
        ##################################################
        print("Build changes detected!")
        print("Updating VDF files...")
        config_directory = os.path.join(launchpad_directory, "Config")
        public_config_file = os.path.join(config_directory, "app_build_" + args.appid + ".vdf")
        private_config_file = os.path.join(config_directory, "app_build_" + args.appid + "_DLC.vdf")
        f = open(public_config_file,'r')
        filedata = f.read()
        f.close()
        public_config_vdf = vdf.loads(filedata, mapper=vdf.VDFDict)
        public_config_vdf["appbuild"].remove_all_for("desc")
        public_config_vdf["appbuild"]["desc"] = "PUBLIC: " + ','.join(latest_public_versions.values())
        f = open(public_config_file,'w')
        vdf.dump(public_config_vdf, f, pretty=True)
        f.close()

        f = open(private_config_file,'r')
        filedata = f.read()
        f.close()
        private_config_vdf = vdf.loads(filedata, mapper=vdf.VDFDict)
        private_config_vdf["appbuild"].remove_all_for("desc")
        private_config_vdf["appbuild"]["desc"] = "PRIVATE: " + ','.join(latest_private_versions.values())
        f = open(private_config_file,'w')
        vdf.dump(private_config_vdf, f, pretty=True)
        f.close()

        ##################################################
        # Copy content into build
        ##################################################
        for from_filepath, to_filepath in builds_to_copy.items():
            print("Copying files from", from_filepath, "to", to_filepath)
            shutil.copytree(
                src=from_filepath,
                dst=to_filepath,
                dirs_exist_ok=True)
            
        ##################################################
        # Publish to Steam
        ##################################################
        print(subprocess.run(["cmd.exe", "/c", os.path.join(launchpad_directory, "run_build_EZ2.bat")], 
                    capture_output=True))
        print(subprocess.run(["cmd.exe", "/c",os.path.join(launchpad_directory, "run_build_EZ2_DLC.bat")], 
                    capture_output=True))

if __name__ == '__main__':
    sys.exit(main())