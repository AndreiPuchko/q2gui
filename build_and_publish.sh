poetry version patch
echo __version__ = \"$(poetry  version -s)\" > "${PWD##*/}"/version.py
poetry build
poetry publish