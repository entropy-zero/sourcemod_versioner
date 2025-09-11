import os
from os.path import abspath
import sys
import argparse
from sourcemod_versioner.data.manifest_file import Manifest

def main():
    print("Running script: " + sys.argv[0])

    parser=argparse.ArgumentParser(description="Convert Valve Manifest File (VMM) to Valve Map File (VMF)")
    parser.add_argument("--input_filepath", nargs='?', default="")
    parser.add_argument("--output_filepath", nargs='?', default="")
    args=parser.parse_args()

    manifest_file = Manifest(args.input_filepath)
    manifest_file.LoadFromFile()
    manifest_file.SaveToMapFile(args.output_filepath)

if __name__ == '__main__':
    sys.exit(main())