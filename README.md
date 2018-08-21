# Jira 2 GitHub migration tool

Script to convert Jira tickets to GitHub issues.

## Supported python version

This tool was test with python `3.6` and higher.

## Installation

From Pypi

```bash
$ pip install jira2github
```

From GitHub

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
                      [--jira-url JIRA_URL] [--jira-user JIRA_USER]
                      [--jira-password JIRA_PASSWORD]
                      [--github-orga GITHUB_ORGA] [--github-repo GITHUB_REPO]
                      [--github-user GITHUB_USER]
                      [--github-password GITHUB_PASSWORD]
                      [--github-token GITHUB_TOKEN]
                      [--custom-message CUSTOM_MESSAGE] [--prettify]
                      [--dry-run] [--check-rate-limit]

Migrate Jira Issues to github.

optional arguments:
  -h, --help            show this help message and exit
  --aliases-path ALIASES_PATH
                        Labels aliases path
  --cache-path CACHE_PATH
                        Cache path
  --xml-path XML_PATH   Jira xml path
  --jira-url JIRA_URL   Jira url
  --jira-user JIRA_USER
                        Jira user
  --jira-password JIRA_PASSWORD
                        Jira user password
  --github-orga GITHUB_ORGA
                        GitHub organisation
  --github-repo GITHUB_REPO
                        GitHub repository
  --github-user GITHUB_USER
                        GitHub user
  --github-password GITHUB_PASSWORD
                        GitHub password
  --github-token GITHUB_TOKEN
                        GitHub Token
  --custom-message CUSTOM_MESSAGE
                        Custom message when creating issue
  --prettify            show prettify projects
  --dry-run             Enable or disable dry-run
  --check-rate-limit    Check rate limit
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
