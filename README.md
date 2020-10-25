# py_artifactory_sync.py

This branch is specifically for a python script which compares a remote repository to a
local repository and copies over new or modified files.

The script depends on ArtificerRuby to generate configurations for authentication and
repository groups and to cache the remote repository's artifacts, so run that first from
https://github.com/danarchy85/artificer_ruby/

The ArtificerRuby::Routine `cache_remote_repository` will caching the remote repository, so
that this script is able to copy those cached files. The default repository_groups.yaml
ArtificerRuby comes with assumes this with a limit `- 5` to minimize the amount of data
copied in this example.

For example:

    OL8_EPEL:
    routines:
    - cache_remote_repository:
        - "/repodata/"
        - 5
    repos:
      remote:
        key: remote.OL8_EPEL
        rclass: remote
        package_type: rpm
        url: https://yum.oracle.com/repo/OracleLinux/OL8/developer/EPEL/x86_64
        description: Remote - Oracle Linux 8 (x86_64) EPEL
      local:
        key: local.OL8_EPEL
        rclass: local
        package_type: rpm
      virtual:
        key: virtual.OL8_EPEL
        rclass: virtual
        package_type: rpm
        repositories:
        - local.OL8_EPEL"

To run the py_artifactory_sync.py script, run `git clone https://github.com/danarchy85/py_artifactory_sync.git`
once those configurations are in place, and then run `source ./setup.sh`, which will create a virtualenv
install the needed pip dependencies and will leave you within the virtualenv.

With the virtualenv sourced, run `python py_artifactory_sync.py` to output the script's help info.

py_artifactory_sync.py requires a repository group name be provided and it can also take an optional
`-d /directory/` argument:

    :~/github/artificer_ruby git:(python_script) $ cd ./python && bash ./setup.sh
    :~/github/artificer_ruby/python git:(python_script) $ source ./venv/bin/activate
    (venv) :~/github/artificer_ruby/python $ python py_artifactory_sync.py
    py_artifactory_sync.py requires a repository group name. Ex: OL8_EPEL
        optionally, -d /dirname/ can be provided to sync that directory.
    Example: python py_artifactory_sync.py OL8_EPEL -d /repodata/

Running py_artifactory_sync.py on the above OL8_EPEL repository group on the /repodata/ directory will
read directory listings of both repositories, compare them to one another, and if a file does not exist
in the local repository, or the files' sha256 sums do not match, it will copy over the file to add or
update it in the local repository.

In this example, 6 files exist on the remote cache, and 2 of those files with older content already exist
on the local repository. It will copy over the four new files, and overwrite the two updated files.

    (venv) :~/github/artificer_ruby/python  $ python py_artifactory_sync.py OL8_EPEL -d repodata
    Loaded auth http://localhost:8082/artifactory/
    Fetching file list from: remote.OL8_EPEL-cache/.
    Found 6 artifacts.
    Fetching file list from: local.OL8_EPEL/.
    Found 2 artifacts.
    New file: 07aab311753e334600686eda6f13f075b9540dfe-primary.sqlite.bz2
    New file: 081a0c7fa70b3577d434a238d7e31a9edb03c233-filelists.sqlite.bz2
    Files differ: 09b3780ab325d9d39a7bc840376172853ac35478-updateinfo.xml.gz
    Files differ: 09ba6052f97aa03ef34b2293a53a4f74da6ac3d8-filelists.xml.gz
    New file: 09b3780ab325d9d39a7bc840376172853ac35478-updateinfo.xml.gz
    New file: 0bec498113cb0dc9c59187e23047cf39d6b162ac-filelists.sqlite.bz2

    Copying files from remote.OL8_EPEL-cache/ to local.OL8_EPEL/
    Source: http://localhost:8082/artifactory/remote.OL8_EPEL-cache/07aab311753e334600686eda6f13f075b9540dfe-primary.sqlite.bz2
    Destination: http://localhost:8082/artifactory/local.OL8_EPEL/07aab311753e334600686eda6f13f075b9540dfe-primary.sqlite.bz2
    Copied: http://localhost:8082/artifactory/remote.OL8_EPEL-cache/07aab311753e334600686eda6f13f075b9540dfe-primary.sqlite.bz2 to http://localhost:8082/artifactory/local.OL8_EPEL/07aab311753e334600686eda6f13f075b9540dfe-primary.sqlite.bz2

    Source: http://localhost:8082/artifactory/remote.OL8_EPEL-cache/081a0c7fa70b3577d434a238d7e31a9edb03c233-filelists.sqlite.bz2
    Destination: http://localhost:8082/artifactory/local.OL8_EPEL/081a0c7fa70b3577d434a238d7e31a9edb03c233-filelists.sqlite.bz2
    Copied: http://localhost:8082/artifactory/remote.OL8_EPEL-cache/081a0c7fa70b3577d434a238d7e31a9edb03c233-filelists.sqlite.bz2 to http://localhost:8082/artifactory/local.OL8_EPEL/081a0c7fa70b3577d434a238d7e31a9edb03c233-filelists.sqlite.bz2

    Source: http://localhost:8082/artifactory/remote.OL8_EPEL-cache/09b3780ab325d9d39a7bc840376172853ac35478-updateinfo.xml.gz
    Destination: http://localhost:8082/artifactory/local.OL8_EPEL/09b3780ab325d9d39a7bc840376172853ac35478-updateinfo.xml.gz
    Copied: http://localhost:8082/artifactory/remote.OL8_EPEL-cache/09b3780ab325d9d39a7bc840376172853ac35478-updateinfo.xml.gz to http://localhost:8082/artifactory/local.OL8_EPEL/09b3780ab325d9d39a7bc840376172853ac35478-updateinfo.xml.gz

    Source: http://localhost:8082/artifactory/remote.OL8_EPEL-cache/09ba6052f97aa03ef34b2293a53a4f74da6ac3d8-filelists.xml.gz
    Destination: http://localhost:8082/artifactory/local.OL8_EPEL/09ba6052f97aa03ef34b2293a53a4f74da6ac3d8-filelists.xml.gz
    Copied: http://localhost:8082/artifactory/remote.OL8_EPEL-cache/09ba6052f97aa03ef34b2293a53a4f74da6ac3d8-filelists.xml.gz to http://localhost:8082/artifactory/local.OL8_EPEL/09ba6052f97aa03ef34b2293a53a4f74da6ac3d8-filelists.xml.gz

    Source: http://localhost:8082/artifactory/remote.OL8_EPEL-cache/09b3780ab325d9d39a7bc840376172853ac35478-updateinfo.xml.gz
    Destination: http://localhost:8082/artifactory/local.OL8_EPEL/09b3780ab325d9d39a7bc840376172853ac35478-updateinfo.xml.gz
    Copied: http://localhost:8082/artifactory/remote.OL8_EPEL-cache/09b3780ab325d9d39a7bc840376172853ac35478-updateinfo.xml.gz to http://localhost:8082/artifactory/local.OL8_EPEL/09b3780ab325d9d39a7bc840376172853ac35478-updateinfo.xml.gz

    Source: http://localhost:8082/artifactory/remote.OL8_EPEL-cache/0bec498113cb0dc9c59187e23047cf39d6b162ac-filelists.sqlite.bz2
    Destination: http://localhost:8082/artifactory/local.OL8_EPEL/0bec498113cb0dc9c59187e23047cf39d6b162ac-filelists.sqlite.bz2
    Copied: http://localhost:8082/artifactory/remote.OL8_EPEL-cache/0bec498113cb0dc9c59187e23047cf39d6b162ac-filelists.sqlite.bz2 to http://localhost:8082/artifactory/local.OL8_EPEL/0bec498113cb0dc9c59187e23047cf39d6b162ac-filelists.sqlite.bz2

This should result in a local repository collecting remote artifacts over time, updating modified files, and retaining old files
when removed from the remote repository.
