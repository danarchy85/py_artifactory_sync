#!/usr/bin/env python

import yaml, json
import os, sys, getopt
from artifactory import ArtifactoryPath

class SyncRepo:
    def __init__(self, _auth, _basedir):
        global auth, basedir
        auth = _auth
        basedir = _basedir
        print('Loaded auth ' + auth['endpoint'])

    def connector_path(self, path):
        path = auth['endpoint'] + path
        if 'username' in auth and 'password' in auth:
            path = ArtifactoryPath(path, auth=(auth['username'], auth['password']))
        elif 'api_key' in auth:
            path = ArtifactoryPath(path, apikey=auth['api_key'])

        return path

    def fetch_file_list(self, repo):
        path = repo['key'] + basedir
        print('Fetching file list from: ' + path)
        path = self.connector_path(path)

        artifacts = dict()
        query = ["items.find",
                 { "$and": [{ "repo": { "$eq": repo['key'] } },
                            { "path": { "$match": basedir } }] }]

        for a in path.aql(*query):
            artifacts[a['name']] = a

        print('Found ' + str(len(artifacts)) + ' artifacts.')
        return artifacts

    def compare_file_sets(self, r_files, l_files):
        files_to_copy = list()
        for name, f in r_files.items():
            if name not in l_files:
                print('New file    : ' + name)
                files_to_copy.append(name)
            else:
                lf = l_files[name]
                path  = '/' if basedir == '.' else '/' + basedir + '/'
                path += name
                r_sha256 = self.get_sha256_sum( f['repo'] + path)
                l_sha256 = self.get_sha256_sum(lf['repo'] + path)

                if r_sha256 != l_sha256:
                    print('Files differ: ' + name)
                    files_to_copy.append(name)

        return files_to_copy

    def get_sha256_sum(self, f):
        path = self.connector_path(f)
        return ArtifactoryPath.stat(path).sha256

    def copy_files(self, files, r_repo, l_repo):
        path  = '/' if basedir == '.' else '/' + basedir + '/'
        print("\nCopying files from " + r_repo['key'] + path + ' to ' + l_repo['key'] + path)
        for name in files:
            p = path + name
            source = self.connector_path(r_repo['key'] + p)
            dest   = self.connector_path(l_repo['key'] + p)
            print('Source:      ' + str(source))
            print('Destination: ' + str(dest))
            try:
                source.copy(dest)
                print("\rCopied: " + str(source) + ' to ' + str(dest))
            except RuntimeError as e:
                errors = json.loads(e.args[0])['errors']
                for error in errors:
                    print(error['message'])


def main(rgroup, argv):
    cfgdir = os.environ['HOME'] + '/.config/artificer_ruby/'

    # with open('example_auth.yaml') as file:
    with open(cfgdir + 'auth.yaml') as file:
        auth = yaml.full_load(file)

    # with open('example_repository_groups.yaml') as file:
    with open(cfgdir + 'repository_groups.yaml') as file:
        rgroups = yaml.full_load(file)

    basedir = '.'
    try:
        opts, args = getopt.getopt(argv, "hd:", ["dir="])
    except getopt.GetoptError:
        print('py_artifactory_sync.py -r repository_group -d repodata')
        sys.exit(2)

    for opt, arg in opts:
        if opt in ('-d', '--dir'):
            basedir = arg

    sync   = SyncRepo(auth, basedir)
    rgroup = rgroups[rgroup]

    r_repo = rgroup['repos']['remote']
    r_repo['key'] += '-cache'
    r_files = sync.fetch_file_list(r_repo)

    l_repo = rgroup['repos']['local']
    l_files = sync.fetch_file_list(l_repo)

    files_to_copy = sync.compare_file_sets(r_files, l_files)
    if len(files_to_copy) > 0:
        sync.copy_files(files_to_copy, r_repo, l_repo) 


if __name__ == '__main__':
    argv = sys.argv[1:]
    if argv == []:
        print('python_pull.py requires a repository group name. Ex: OL8_EPEL')
        print('    optionally, -d /dirname/ can be provided to sync that directory.')
        print('Example: python python_pull.py OL8_EPEL -d /repodata/')
    else:
        rgroup = argv.pop(0)
        main(rgroup, argv)

