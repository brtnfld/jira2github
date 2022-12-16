#!/usr/bin/env python3
import argparse
import getpass
import jira2github


def main():
    parser = argparse.ArgumentParser(description='Migrate Jira Issues to github.')
    parser.add_argument('--aliases-path', type=str, help='Labels aliases path')
    parser.add_argument('--cache-path', type=str, help='Cache path')
    parser.add_argument('--xml-path', type=str, help='Jira xml path')
    parser.add_argument('--jira-url', type=str, help='Jira url')
    parser.add_argument('--jira-user', type=str, help='Jira user')
    parser.add_argument('--jira-password', type=str, help='Jira user password')
    parser.add_argument('--github-orga', type=str, help='GitHub organisation')
    parser.add_argument('--github-repo', type=str, help='GitHub repository')
    parser.add_argument('--github-user', type=str, help='GitHub user')
    parser.add_argument('--github-password', type=str, help='GitHub password')
    parser.add_argument('--github-token', type=str, help='GitHub Token')
    parser.add_argument('--custom-github-message', type=str, help='Custom message when creating GitHub issue')
    parser.add_argument('--custom-comment-github-message', type=str, help='Custom comment message when creating GitHub comment')
    parser.add_argument('--custom-jira-message', type=str, help='Custom message when adding a comment into Jira')
    parser.add_argument('--prettify', action='store_const', const=True, help='show prettify projects')
    parser.add_argument('--dry-run', action='store_const', const=True, help='Enable or disable dry-run')
    parser.add_argument('--check-rate-limit', action='store_const', const=True, help='Check rate limit')
    args = parser.parse_args()

    xml_path = args.xml_path if args.xml_path else input('Jira xml path:')
    github_orga = args.github_orga if args.github_orga else input('GitHub orga: ')
    github_repo = args.github_repo if args.github_repo else input('GitHub repo: ')
    github_user = None
    github_password = None
    jira_user = None
    jira_password = None

    if not args.github_token:
        github_user = args.github_user if args.github_user else input('GitHub username: ')
        github_password = args.github_password if args.github_password else getpass.getpass('GitHub password: ')

    if args.jira_url or args.jira_user:
        jira_user = args.jira_user if args.jira_user else input('Jira username: ')
        jira_password = args.jira_password if args.jira_password else getpass.getpass('Jira password: ')

    jira_to_github = jira2github.jira2github(
        xml_path,
        github_orga,
        github_repo,
        github_user,
        github_password,
        args.github_token,
    )

    jira_to_github.set_aliases_path(args.aliases_path)
    jira_to_github.set_cache_path(args.cache_path)
    jira_to_github.set_dry_run(args.dry_run)
    jira_to_github.set_custom_github_message(args.custom_github_message)
    jira_to_github.set_custom_comment_github_message(args.custom_comment_github_message)
    jira_to_github.set_custom_jira_message(args.custom_jira_message)
    jira_to_github.set_jira_config(
        args.jira_url,
        jira_user,
        jira_password
    )

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
