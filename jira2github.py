#!/usr/bin/env python
import argparse
import getpass
import jira2github


def main():
    parser = argparse.ArgumentParser(description='Migrate Jira Issues to github.')
    parser.add_argument('--aliases-path', type=str, help='Labels aliases path')
    parser.add_argument('--cache-path', type=str, help='Cache path')
    parser.add_argument('--xml-path', type=str, help='Jira xml path')
    parser.add_argument('--jira-project', type=str, help='Jira Project to use')
    parser.add_argument('--github-orga', type=str, help='Github organisation')
    parser.add_argument('--github-repo', type=str, help='Github repository')
    parser.add_argument('--github-user', type=str, help='Github user')
    parser.add_argument('--github-password', type=str, help='Github password')
    parser.add_argument('--custom-message', type=str, help='Custom message when creating issue')
    parser.add_argument('--prettify', action='store_const', const=True, help='show prettify projects')
    parser.add_argument('--dry-run', action='store_const', const=True, help='Enable or disable dry-run')
    parser.add_argument('--check-rate-limit', action='store_const', const=True, help='Check rate limit')
    args = parser.parse_args()

    xml_path = args.xml_path if args.xml_path else input('Jira xml path:')
    jira_project = args.jira_project if args.jira_project else input('Jira project to use:')
    github_orga = args.github_orga if args.github_orga else input('Github orga: ')
    github_repo = args.github_repo if args.github_repo else input('Github repo: ')
    github_user = args.github_user if args.github_user else input('Github username: ')
    github_password = args.github_password if args.github_password else getpass.getpass('Github password: ')

    jira_to_github = jira2github.jira2github(
        xml_path,
        jira_project,
        github_orga,
        github_repo,
        github_user,
        github_password,
    )
    jira_to_github.set_aliases_path(args.aliases_path)
    jira_to_github.set_cache_path(args.cache_path)
    jira_to_github.set_dry_run(args.dry_run)
    jira_to_github.set_custom_message(args.custom_message)

    jira_to_github.extract()
    if args.prettify:
        jira_to_github.prettify()
    elif args.check_rate_limit:
        jira_to_github.check_rate_limit()
    else:
        jira_to_github.milestones()
        try:
            jira_to_github.migrate()
        except KeyboardInterrupt:
            print('Interrupted, saving cache')
        finally:
            jira_to_github.save_cache_data()
            jira_to_github.save_errors_data()


if __name__ == '__main__':
    main()
