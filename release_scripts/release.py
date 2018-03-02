import os
import sys
import semver
from github import Github

PLUGIN_TYPES = "[vim | nvim | sublime]"

# Test repos. Replace with final production URLs
SUBLIME_REPO = "https://github.com/rageandqq/tandem"
VIM_REPO = "https://github.com/rageandqq/tandem_vim"
NVIM_REPO = "https://github.com/rageandqq/tandem_nvim"


def error(msg):
    print("ERROR: {}.".format(msg))
    exit(1)


def main():
    if len(sys.argv) < 2:
        error("Pass in plugin type as the first argument. "
              "Choose from: {}".format(PLUGIN_TYPES))
    elif len(sys.argv) < 3:
        error("You must also pass in repository SHA as the argument")

    repo_type = sys.argv[1].lower()
    if repo_type == "sublime":
        repo_url = SUBLIME_REPO
    elif repo_type == "vim":
        repo_url = VIM_REPO
    elif repo_type == "nvim":
        repo_url = NVIM_REPO
    else:
        error("ERROR: Please pass in one of {} as the plugin type"
              .format(PLUGIN_TYPES))

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
        error("{} repo not found".format(repo_type))

    tags = release_repo.get_tags()
    last_tag = None
    for t in tags:
        last_tag = t
        break

    if (last_tag is None):
        last_tag = '0.0.0'
    else:
        if last_tag.commit.sha == master_SHA:
            error("ERROR: Cannot create release with same SHA")
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
