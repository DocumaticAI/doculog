# doculog

_README generated with **Documatic**_.

Quickly generate changelogs
and release notes
by analysing your git history.
A tool written in python,
but works on any language.
Once installed,
simply run

```bash
doculog -h
```

in a terminal
in a git-enabled
project directory,
and a changelog will be generated.
For advanced changelog generation,
you can use the [Documatic API](#api-key).

## Getting started

### Requirements

* python >= 3.8
* git
* "good" commit messages
* Git version tags

Minimum python 3.8.
Project actively supports python 3.8,
3.9,
3.10.
To install,
clone the repository
and run `pip install -e .`
to package locally
OR
`pip install doculog`.

`Doculog` works by reading git commit messages
and inferring what changes are being made.
It assumes that you are writing
your commit messages as actions:
e.g. "_Add_ some feature",
"_Fix_ a particular bug".
While it's good practice to have the action
in the present,
imperitive tense,
`doculog` accepts past verbs.
See [git best practices](https://cbea.ms/git-commit/#imperative)
for more information
on this git commit writing style.
Standard `doculog` looks through a list
of expected verbs
(open an issue/contribute a PR if there are some missing!),
but the [extended version](#api-key)
includes additional logic
for classifying commit message,
which allows you to be more lax
with your commit messages.

### API key

To generate a changelog
with a full feature-set,
doculog requires a (free)
API key.
Join the waitlist
for an API key
by signing up [here](https://www.documatic.com).
Someone will be in touch with your API key.
In the meantime,
doculog **works without an API key**
(you just won't have access to advanced features).

`doculog` uses `python-dotenv`
to load environment variables
stored in a `.env` file.
To use your API key,
create a `.env` file
in your project root directory
with the following fields:

```
DOCUMATIC_API_KEY = <your-api-key>
```

**IMPORTANT: DO NOT ADD `.env` TO VERSION CONTROL.
YOUR API KEY MUST BE KEPT SECRET.**


### Generate a Changelog

In a terminal,
run `doculog`
to create
a `CHANGELOG.md`
from your git commit history,
or update an existing changelog.
The "Unreleased" section corresponds to updates
not attached to a version.
Each changelog update version
may contain the following sections:
"Added",
"Removed",
"Deprecated",
"Fixed",
"Changed".
Each section header will only appear
in the version
if it has at least one update.
**Note:** `doculog` will overwrite changes made
to the "Unreleased" section
every time it is run,
however tagged versions are not overwritten.
Therefore,
you can manually edit
and add updates
to a version release.

To get the best out of the changelog,
read the concepts below
for information on
[configuration](#configuration),
[git commits](#git-commit-parsing)
and [version tags](#version-tags).

## Concepts

### Git commit parsing

The initial logic for generating a changelog
comes from reading
your git commit messages.
`doculog`
expects
commit messages to begin with an imperitive verb,
and to written passively.
`doculog` parses the message for signalling words
and phrases.

E.g. `Rename 'my_func' to 'my_awesome_func'`
will get interpreted as a "Changed" feature.
Whereas `'my_func' -> 'my_awesome_func'`
will not.

### Version tags

Changelogs break down your project's featureset
by each release.
Currently,
`doculog` infers a release has been made
by reading the git tags of your project.
If you don't have any git tags,
your changelog will only have an "Unreleased" section.
To make a git tag,
run `git tag -a v<MAJOR>-<MINOR>-<PATCH>`
(and `git push --tags` to push to your remote);
This assumes you're using [semver](https://www.mariokandut.com/what-is-semantic-versioning-semver/)
versioning system.

**Note:** not using semver or git tags to release your project?
Open an issue on the `doculog` repo
detailing your method to get it supported
by `doculog`.

### Configuration

You can configure how `doculog` runs
by adding a `tool.doculog` section
to `pyproject.toml`.

| Field | Purpose | Required | Default value |
|:------|:--------|:---------|:--------------|
| changelog | Name of changelog file generated. ".md" suffix added if not present. | No | CHANGELOG.md |
| project | The name of your project. Used to title the changelog | No | The name of your root project folder |
| local | If `true`, use a local sever for advanced features. Only used for project development | No | false |

For example,
your `pyproject.toml` file _might_ be:

```
[tool.doculog]
changelog = "CHANGELOG"
project = "My Cool Project"
```

## Developers

Read the [contributing guide](CONTRIBUTING.md)
for information on coding styles
and workflow.

Run `pip install -r requirements-dev.txt`
to get developer requirements.

| CI file | Purpose |
|:--------|:--------|
| `test.yml` | Linting and unit testing. Runs on every pull request |

## FAQ

### I want more intelligent featureset generation. What can I do?

Request access to the free Documatic API
to generate a changelog
driven by machine learning.
Follow `Documatic` on GitHub
and socials
to stay up to date
with the latest features
and releases.

### How do I get my API key?

Once you've joined the waitlist,
we will be in touch shortly
with your API key.

### The changelog is great, but I want more!

Get in touch - `info@documatic.com`.

### I'm not getting a complete changelog. What's gone wrong?

Check that you have appropriate [version tags](#version-tags)
and [commit messages](#git-commit-parsing).
If you have the advanced featureset
(i.e. have an API key)
then you will get better changelog updates
which don't require you to follow
the commit process
so strictly.
If you're still not getting good results,
please open a bug report.

### Can I contribute to doculog?

Absolutely:
feature requests,
bug fixes,
bug reports
and PRs of all shapes and sizes
are welcome.
See the [developers](#developers)
section.

## License

Licensed under GNU GPL3.
Please see the [LICENSE]
for terms in full.

_Generated by **Documatic**._
