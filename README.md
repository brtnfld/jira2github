# Jira 2 Github migration tool

Script to convert Jira tickets to Github issues.

## Supported python version

This tool was test with python `3.6` and higher.

## Installation

From Pypi

```bash
$ pip install jira2github
```

From Github

```bash
$ git clone https://github.com/PierreRambaud/jira2github.git
$ cd jira2github
$ ./jira2github.py --help
```

## Usage

```bash
$ ./jira2github.py -h
usage: jira2github.py [-h] [--aliases-path ALIASES_PATH]
                      [--cache-path CACHE_PATH] [--xml-path XML_PATH]
                      [--jira-project JIRA_PROJECT]
                      [--github-orga GITHUB_ORGA] [--github-repo GITHUB_REPO]
                      [--github-user GITHUB_USER]
                      [--github-password GITHUB_PASSWORD] [--prettify]
                      [--dry-run]

Migrate Jira Issues to github.

optional arguments:
  -h, --help            show this help message and exit
  --aliases-path ALIASES_PATH
                        Labels aliases path
  --cache-path CACHE_PATH
                        Cache path
  --xml-path XML_PATH   Jira xml path
  --jira-project JIRA_PROJECT
                        Jira Project to use
  --github-orga GITHUB_ORGA
                        Github organisation
  --github-repo GITHUB_REPO
                        Github repository
  --github-user GITHUB_USER
                        Github user
  --github-password GITHUB_PASSWORD
                        Github password
  --prettify            show prettify projects
  --dry-run             Enable or disable dry-run
```


## Running tests

Install dependencies:

```bash
$ ./setup.py test
```

To check code style:

```bash
$ ./setup.py flake8
$ # or
$ flake8
```

## License

See [LICENSE.md](LICENSE.md) file.
