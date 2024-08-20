
This repository stores a Python project to automate tasks related to publishing versions of Entropy : Zero 2 and related projects.

## Dependencies ##
```
pip install --requirements ./requirements.txt
# OR
pip install gitpython
pip install vdf
```

## How to use ##

To create an automatic version, tag, and push, run the Python module sourcemod_versioner.tools.create_version.

**NOTE** - Currently, this does not account for creating the first version. The initial version within each phase should be tagged manually.

For the full help documentation, run the help command:
```
python -m sourcemod_versioner.tools.create_version --help
```

For these examples, suppose there is a Git repository for an EZ2 mod called EntropyZero2_MyEZ2Mod in the sourcemods folder. Also, suppose that the base game is installed on the C drive, with Steam being installed in Program Files( x86).

To automatically create a version tag for this repo, one would run the Python module with this command in Bash:
```
python -m sourcemod_versioner.tools.create_version --game="/Program Files (x86)/Steam/steamapps/sourcemods/EntropyZero2_MyEZ2Mod"
```
OR use a relative path with the working directory
```
python -m sourcemod_versioner.tools.create_version --game="$(pwd)/../../EntropyZero2_MyEZ2Mod"
```

#### --prefix ####
Entropy : Zero 2 tags begin with ``ez2_``. To change the game prefix, use the --prefix option. In the below example, release will be tagged ``ap_`` instead:
```
python -m sourcemod_versioner.tools.create_version --game="/Program Files (x86)/Steam/steamapps/sourcemods/EntropyZero2_MyEZ2Mod" --prefix ap
```

#### --summary ####
Use the --summary option to supply a commit message for the release.
```
python -m sourcemod_versioner.tools.create_version --game="/Program Files (x86)/Steam/steamapps/sourcemods/EntropyZero2_MyEZ2Mod" --summary="Fixed that one specific bug"
```

#### --phase ####
Sets the release phase in the tag. ez2 releases are tagged like ``ez2_release``. In this example, the tag will be for ``ez2_alpha`` instead.
```
python -m sourcemod_versioner.tools.create_version --game="/Program Files (x86)/Steam/steamapps/sourcemods/EntropyZero2_MyEZ2Mod" --phase="alpha"
```

#### --dryrun ####
Do not push to the repository. This will still modify files locally.
```
python -m sourcemod_versioner.tools.create_version --game="/Program Files (x86)/Steam/steamapps/sourcemods/EntropyZero2_MyEZ2Mod" --dryrun
```

## Unit Tests ##

To run all unit tests from Bash, use:
```
python -m unittest
```

To run a particular unit test class like test_push, make sure that the working directory is this repo and use:
```
python -m unittest -v sourcemod_versioner.test.test_repo
```

Unit tests are not comprehensive. They should be improved in the future.