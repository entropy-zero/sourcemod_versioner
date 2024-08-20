import git
from git.repo import Repo
from git.remote import Remote

class Repository:
    def __init__(self, repo=None, remote=None):
        self._repo = repo
        self._dry_run = False
        if(remote == None and repo != None):
            self._remote = self._repo.remotes.origin
        else:
            self._remote = remote

    def initialize(self, filepath):
        self._filepath = filepath
        self._repo = Repo(filepath)
        self._remote = self._repo.remotes.origin

    def set_dry_run(self, dry_run):
        self._dry_run = dry_run

    def get_repo(self):
        return self._repo

    def has_unstaged_changes(self):
        diff = self._repo.index.diff(None)
        return len(diff) > 0

    def get_diff_with_tag(self, tag_name):
        tag = self._repo.tags[tag_name]
        diffs = self._repo.index.diff(tag_name)
        result = []
        for diff in diffs:
            result.append(diff.b_path)
        return result
    
    def get_filepath(self):
        return self._filepath

    def add_files(self, files_names=[]) -> int:
        if(self._dry_run):
            print("DRY RUN: Would have staged added files for commit: " + str(files_names))
            return 0
        self._repo.index.add(files_names) 
        return 0
    
    def remove_files(self, files_names=[]) -> int:
        if(self._dry_run):
            print("DRY RUN: Would have staged deleted files for commit: " + str(files_names))
            return 0
        self._repo.index.remove(files_names) 
        return 0

    def create_commit(self, commit_message) -> int:
        if(self._dry_run):
            print("DRY RUN: Would have committed with message: " + commit_message)
            return 0
        self._repo.index.commit(commit_message)
        return 0

    def push(self, tags=[]) -> int:
        print("Pushing to repository")

        if(self._dry_run):
            print("DRY RUN: Would have pushed head commit and tags: " + str(tags))
            return 0            

        self._remote.push()
        for tag in tags:
            self._remote.push(tag.name)
        return 0

    def create_tag(self, tag_name) -> int:
        if(self._dry_run):
            print("DRY RUN: Would have created tag: " + tag_name)
            return {"name":tag_name}

        tag = self._repo.create_tag(
            tag_name,
            ref=self._repo.head.ref
        )
        return tag


if __name__ == '__main__':
    sys.exit(0)