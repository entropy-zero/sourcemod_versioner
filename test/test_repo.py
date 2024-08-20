from sourcemod_versioner.versioning.repo import Repository
import unittest
from unittest import mock

class PushTestCase(unittest.TestCase):
    @mock.patch('git.repo.Repo')
    @mock.patch('git.remote.Remote')
    def test_push(self, mock_remote, mock_repo):
        repository = Repository(mock_repo, mock_remote)
        result = repository.push()
        self.assertEqual(result, 0)
        mock_remote.push.assert_called_with()

    @mock.patch('git.repo.Repo')
    @mock.patch('git.remote.Remote')
    def test_push_dry_run(self, mock_remote, mock_repo):
        repository = Repository(mock_repo, mock_remote)
        repository.set_dry_run(True)
        result = repository.push()
        self.assertEqual(result, 0)
        mock_remote.push.assert_not_called()


class TagTestCase(unittest.TestCase):
    @mock.patch('git.repo.Repo')
    @mock.patch('git.remote.Remote')
    def test_create_tag(self, mock_remote, mock_repo):
        repository = Repository(mock_repo, mock_remote)
        result = repository.create_tag("tag_version")
        mock_repo.create_tag.assert_called_with("tag_version", ref=mock_repo.head.ref)

    @mock.patch('git.repo.Repo')
    @mock.patch('git.remote.Remote')
    def test_create_tag_dry_run(self, mock_remote, mock_repo):
        repository = Repository(mock_repo, mock_remote)
        repository.set_dry_run(True)
        result = repository.create_tag("tag_version")
        mock_repo.create_tag.assert_not_called()