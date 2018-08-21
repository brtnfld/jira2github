import csv
import json
import os
import re
import requests
import time
from progressbar.bar import ProgressBar
from html.entities import name2codepoint
from lxml import objectify
from collections import defaultdict


class jira2github:

    TYPE_FLOAT = 'com.atlassian.jira.plugin.system.customfieldtypes:float'
    METHOD_GET = 'get'
    METHOD_POST = 'post'

    ##
    # Initialize github and Jira information
    #
    def __init__(
        self,
        xml_path,
        jira_project,
        github_orga,
        github_repo,
        github_user,
        github_password,
        github_token
    ):
        self.xml_path = xml_path
        self.jira_project = jira_project
        self.github_orga = github_orga
        self.github_user = github_user
        self.github_repo = github_repo
        self.github_password = github_password
        self.github_token = github_token
        self.github_url = 'https://api.github.com/repos/{}/{}'.format(github_orga, github_repo)
        self.projects = {}
        self.dry_run = False
        self.cached_data = {}
        self.migration_errors = {}

    ##
    # Set cache path and reload cached data if needed
    #
    def set_cache_path(self, cache_path):
        if cache_path is None:
            cache_path = os.path.abspath('cache.json')

        self.cache_path = cache_path

        try:
            if os.path.getsize(self.cache_path) > 0:
                with open(self.cache_path, 'rb') as fp:
                    self.cached_data = json.load(fp)
        except FileNotFoundError:
            pass

    ##
    # Set cache path and reload cached data if needed
    #
    def set_aliases_path(self, aliases_path):
        self.aliases = dict()
        if aliases_path is not None:
            with open(aliases_path, encoding='utf-8') as f:
                r = csv.reader(f, delimiter=',', quotechar='"')
                self.aliases = dict(r)

    ##
    # Set custom message
    #
    def set_custom_message(self, custom_message):
        if custom_message is not None:
            self.custom_message = custom_message
        else:
            self.custom_message = 'This issue has been migrated from this Forge ticket'

    ##
    # Enable dry run mode
    #
    def set_dry_run(self, dry_run):
        if dry_run is True:
            print('Run into dry-run mode')
            self.dry_run = dry_run

    ##
    # Html entity decode
    #
    def htmlentitydecode(self, s):
        if s is None:
            return ''

        s = s.replace(' '*8, '')
        return re.sub('&(%s);' % '|'.join(name2codepoint),
            lambda m: chr(name2codepoint[m.group(1)]), s)

    ##
    # Extract issues from xml

    def extract(self):
        all_xml = objectify.fromstring(open(self.xml_path).read())

        for item in all_xml.channel.item:
            self._add_to_projects(item)

    ##
    # Add issues and informations into projects list
    #
    def _add_to_projects(self, item):
        try:
            proj = item.project.get('key')
        except AttributeError:
            proj = item.key.text.split('-')[0]

        if proj not in self.projects:
            self.projects[self.jira_project] = {
                'Milestones': defaultdict(int),
                'Components': defaultdict(int),
                'Labels': defaultdict(int),
                'Issues': []
            }

        try:
            resolved_at = '- _**Resolved at:**_ {resolved_at}'.format(resolved_at=item.resolved.text)
        except AttributeError:
            resolved_at = ''

        body = '''
> {custom_message} [{issue_link}]({issue_link})

- _**Reporter:**_ {reporter}
- _**Created at:**_ {created_at}
{resolved_at}

{description}
        '''

        self.projects[self.jira_project]['Issues'].append(
            {
                'title': item.title.text,
                'type': item.type.text,
                'key': item.key.text,
                'body': body.format(
                    reporter=item.reporter.get('username'),
                    created_at=item.created.text,
                    description=self.htmlentitydecode(item.description.text),
                    resolved_at=resolved_at,
                    issue_link=item.link.text,
                    custom_message=self.custom_message,
                ),
                'labels': [item.status.text, item.type.text],
                'comments': [],
            }
        )
        try:
            self.projects[self.jira_project]['Milestones'][item.fixVersion.text] += 1
            # this prop will be deleted later:
            self.projects[self.jira_project]['Issues'][-1]['milestone_name'] = item.fixVersion.text
        except AttributeError:
            pass

        try:
            self.projects[self.jira_project]['Components'][item.component.text] += 1
            self.projects[self.jira_project]['Issues'][-1]['labels'].append(item.component.text)
        except AttributeError:
            pass

        try:
            for version in item.version:
                if re.match('^(\d+.){3}\d+$', version.text) is not None:
                    self.projects[self.jira_project]['Labels'][version.text] += 1
                    self.projects[self.jira_project]['Issues'][-1]['labels'].append(version.text)
        except AttributeError:
            pass

        try:
            self.projects[self.jira_project]['Labels'][item.priority.text] += 1
            self.projects[self.jira_project]['Issues'][-1]['labels'].append(item.priority.text)
        except AttributeError:
            pass

        try:
            for label in item.labels.label:
                self.projects[self.jira_project]['Labels'][label.text] += 1
                self.projects[self.jira_project]['Issues'][-1]['labels'].append(label.text)
        except AttributeError:
            pass

        try:
            for customfield in item.customfields.customfield:
                if customfield.get('key') == self.TYPE_FLOAT:
                    field_value = int(float(customfield.customfieldvalues.customfieldvalue[0].text))
                elif isinstance(customfield.customfieldvalues, list):
                    field_value = customfield.customfieldvalues.customfieldvalue[0].text
                else:
                    field_value = customfield.customfieldvalues.text

                if customfield.customfieldname.text in ['Story Points']:
                    self.projects[self.jira_project]['Labels'][field_value] += 1
                    self.projects[self.jira_project]['Issues'][-1]['labels'].append(field_value)
        except AttributeError:
            pass

        try:

            body = '''
> {custom_message} [{issue_link}]({issue_link})

- _**Author:**_ {author}
- _**Created at:**_ {created_at}

{description}
        '''
            for comment in item.comments.comment:
                self.projects[self.jira_project]['Issues'][-1]['comments'].append(
                    body.format(
                        author=comment.get('author'),
                        created_at=comment.get('created'),
                        description=self.htmlentitydecode(comment.text),
                        issue_link=item.link.text,
                        custom_message=self.custom_message,
                    )
                )
        except AttributeError:
            pass

    ##
    # Prettify data
    #
    def prettify(self):
        def hist(h):
            for key in h.keys():
                print('%30s(%5d): ' % (key, h[key]) + h[key]*'#')
            print('')

        for proj in iter(self.projects.keys()):
            print(proj + ':\n    Milestones:')
            hist(self.projects[proj]['Milestones'])
            print('    Components:')
            hist(self.projects[proj]['Components'])
            print('    Labels:')
            hist(self.projects[proj]['Labels'])
            print('')
            print('    Total Issues: {}'.format(len(self.projects[proj]['Issues'])))
            print('')

    ##
    # Check for github milestones
    #
    def milestones(self):
        print('Making milestones...', self.github_url + '/milestones')
        print('')

        r = self._execute_request(
            self.METHOD_GET,
            self.github_url + '/milestones',
        )

        def find_in_milestones(response, title):
            for milestone in r.json():
                if mkey == milestone['title']:
                    return True
            return False

        response_json = r.json()

        for mkey in iter(self.projects[self.jira_project]['Milestones'].keys()):
            if find_in_milestones(response_json, mkey) is False:
                self.projects[self.jira_project]['Milestones'][mkey] = None

    ##
    # Migrate issue to github
    #
    def migrate(self):
        print('Creating each issue...')

        bar = ProgressBar(max_value=len(self.projects[self.jira_project]['Issues']))
        self.migration_errors = {
            'milestone': [],
            'github': [],
        }
        for index, issue in enumerate(self.projects[self.jira_project]['Issues']):
            # Check if this issue has already been created on github
            if self.jira_project in self.cached_data and issue['key'] in self.cached_data[self.jira_project]:
                bar.update(index)
                continue

            # Check for milestone
            if 'milestone_name' in issue:
                issue['milestone'] = self.projects[self.jira_project]['Milestones'][issue['milestone_name']]
                if issue['milestone'] is None:
                    self.migration_errors['milestone'].append(issue['title'])
                    continue

                del issue['milestone_name']

            if len(self.aliases) != 0:
                result = []
                for i, label in enumerate(issue['labels']):
                    if label in self.aliases:
                        if self.aliases[label] == 'DELETED':
                            continue

                        if self.aliases[label] != 'same':
                            result.append(self.aliases[label])
                            continue
                    result.append(label)
                issue['labels'] = result

            comments = issue['comments']
            del issue['comments']

            result = self._save_issue(issue, comments)
            if result is not True:
                self.migration_errors['github'].append(
                    {
                        'issue': issue,
                        'result': json.loads(result.content),
                        'status': result.status_code,
                    }
                )

            bar.update(index)
        bar.update(len(self.projects[self.jira_project]['Issues']))

    ##
    # Save issue into github
    #
    def _save_issue(self, issue, comments):
        if self.dry_run:
            self._add_cache_data(issue['key'], issue)
            return True

        response_create = self._execute_request(
            self.METHOD_POST,
            self.github_url + '/issues',
            json.dumps(issue),
        )

        # Sleep even if the response was ok
        self._sleep()

        # Error while saving issue
        if response_create.status_code != 201:
            return response_create

        content = json.loads(response_create.content)
        self._add_cache_data(issue['key'], content['url'])

        for comment in comments:
            self._execute_request(
                self.METHOD_POST,
                self.github_url + '/issues/' + str(content['number']) + '/comments',
                json.dumps({'body': comment}),
            )
            self._sleep()

        return True

    ##
    # Sleep
    #
    def _sleep(self, seconds=3):
        time.sleep(seconds)

    ##
    # Save issue key and url into cach file
    #
    def _add_cache_data(self, key, url):
        if self.jira_project not in self.cached_data:
            self.cached_data[self.jira_project] = {}

        self.cached_data[self.jira_project][key] = url

    ##
    # Save file cache
    #
    def save_cache_data(self):
        self._save_json(self.cache_path, self.cached_data)

    ##
    # Save errors data
    #
    def save_errors_data(self):
        if len(self.migration_errors) > 0:
            print('This jira issues are on errors: ')
            print('Milestone errors: {}'.format(len(self.migration_errors['milestone'])))
            print('Issues errors: {}'.format(len(self.migration_errors['github'])))
            self._save_json('errors.json', self.migration_errors)

    ##
    # Save json file
    #
    def _save_json(self, file_path, data):
        with open(file_path, 'w') as fp:
            json.dump(data, fp, ensure_ascii=False)

    ##
    # Check rate Limit
    #
    def check_rate_limit(self):
        limit = self._execute_request(
            self.METHOD_GET,
            'https://api.github.com/rate_limit',
        )
        print(json.loads(limit.content))

    ##
    # Execute requests
    #
    def _execute_request(self, method, url, data=None, headers={'Accept': 'application/vnd.github.beta.html+json'}):
        params = {
            'headers': headers,
        }

        if self.github_token is not None:
            params['headers']['Authorization'] = 'Token {}'.format(self.github_token)
        else:
            params['auth'] = (self.github_user, self.github_password)

        if data is not None:
            params['data'] = data

        if method == self.METHOD_POST:
            return requests.post(
                url,
                **params
            )

        return requests.get(
            url,
            **params
        )
