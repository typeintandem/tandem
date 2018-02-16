import os
import sys
import semver
from github import Github

# Test repo. Replace with final production repository
SUBLIME_REPO = "https://github.com/rageandqq/tandem"


def main():
    if len(sys.argv) < 2:
        print("Pass in repo as the first argument. Choose from: [sublime]")
        return
    elif len(sys.argv) < 3:
        print("You must also pass in repository SHA as the argument.")
        return

    repo_type = sys.argv[1].lower()
    if repo_type == "sublime":
        repo_url = SUBLIME_REPO
    else:
        print("Please pass in one of [sublime] as the repo.")
        return

    master_SHA = sys.argv[2]

    bot_username = os.environ.get('RELEASE_BOT_USERNAME')
    bot_password = os.environ.get('RELEASE_BOT_PASSWORD')

    g = Github(bot_username, bot_password)

    release_repo = None
    for repo in g.get_user().get_repos():
        if repo.html_url == repo_url:
            release_repo = repo
            break

    if release_repo is None:
        print("Error: {} repo not found".format(repo_type))

    tags = release_repo.get_tags()
    last_tag = None
    for t in tags:
        last_tag = t
        break

    if (last_tag is None):
        last_tag = '0.0.0'
    else:
        last_tag = last_tag.name

    tag = semver.bump_minor(last_tag)

    release_repo.create_git_tag_and_release(
        tag,
        "Release version {}".format(tag),
        "v{}".format(tag),
        "Release version {}".format(tag),
        master_SHA,
        "commit",
    )

    print("Succesfully created release v{}".format(tag))


if __name__ == "__main__":
    main()
