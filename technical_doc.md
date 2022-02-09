# Doculog Technical Documentation

**Last updated:** 2022-02-08\
_Document generation aided by **Documatic**_

## Introduction

This is a technical document detailing
        at a high-level
        what Doculog does, how it operates,
        and how it is built.

The outline of this document was generated
        by **Documatic**.
<!---Documatic-section-group: helloworld-start--->


## Getting Started

<!---Documatic-section-helloworld: setup-start--->
* The codebase is compatible with Python 3.8 and above, because of walrus in `doculog/doculog/changelog.py`.
* Install requirements with `pip install -r requirements.txt`.
* Install from pypi with `pip install doculog`.

**CLI**

The project has the following CLI commands:

* `doculog` runs `doculog.main.parse`

```
parse()

This function parses command line arguments.
It sets the logger and updates path to the project if a path is given in the command line arguments.
If a 'v' flag is given it prints the version number.
It then generates the changelog.
```

Run the CLI command in a terminal to execute.

**Environment**

Environment variables are read from `.env` file.
The following environment variables are consumed:

| VARIABLE | DEFAULT VALUE |
|:---------|:--------------|
| DOCUMATIC_API_KEY |  |
| DOCULOG_API_KEY |  |
| DOCULOG_PROJECT_NAME |  |
| DOCULOG_RUN_LOCALLY |  |


<!---Documatic-section-helloworld: setup-end--->

<!---Documatic-section-group: helloworld-end--->

<!---Documatic-section-group: dev-start--->


## Developers
<!---Documatic-section-dev: setup-start--->
* Install developer requirements with `pip install -r requirements-dev.txt`
* Run `pip install -e .` in top-level directory to install
package in edit mode locally
* Tests are present in `tests/` (using pytest)


<!---Documatic-section-dev: setup-end--->

<!---Documatic-section-dev: ci-start--->
The project uses GitHub Actions for CI/CD.

| CI File | Purpose |
|:----|:----|
| test-integration | Executes on pull request for any branch |
| test | Executes on pull request for any branch. Linting (with black, isort). Tests with python 3.8, 3.9, 3.10 |


<!---Documatic-section-dev: ci-end--->

<!---Documatic-section-group: dev-end--->

## Code Overview

The codebase has a flat structure, with 6 code files.
Some files are omitted.

### **doculog/**
<!---Documatic-section-file: doculog/main.py--->

#### main.py


File has 119 lines added and 46 lines removed
                in the past 4 weeks. Seniatical <isaja7710@gmail.com> is the inferred code owner.


main.py has 3 functions.

```python
generate_changelog(overwrite: bool = False)

This function takes a path to a directory where you want to save a changelog.
The function then checks if the directory already exists. If it does, it removes the directory.
If the directory does not exist, it creates it.
Then it creates a changelog document.

Does not raise.
```

```python
update_logger()

The function creates a new logger object, sets its level to DEBUG, creates a new handler object, sets its formatter to a custom formatter, and adds the handler to the logger.

Does not raise.
```

```python
parse()

The function parses the command line arguments.
The function updates the logger.
The function checks if the command line argument "v" is present.
The function prints the version number if the "v" command line argument is present.

Does not raise.
```

main.py has 0 classes.

<!---Documatic-section-file: doculog/git.py--->

#### git.py


* File has 85 lines added and 49 lines removed
in the past 4 weeks. Tom Titcombe <t.j.titcombe@gmail.com> is the inferred code owner.
* git.py has 5 functions.

```python
list_tags() -> List[Tuple[str, str]]

This function calls git to get the list of tags.
The code catches subprocess.CalledProcessError, FileNotFoundError
Does not raise.
```

```python
has_git() -> bool

This function checks whether the git command exists on the system.
It does this by calling the subprocess module to run the git command
and then checks the output.
If the git command exists, the function returns True.
If the git command does not exist, the function returns False
```

* git.py has 0 classes.

#### config.py

* config.py has 3 functions.

```python
configure(project_root: Path) -> Dict

It takes a project root directory as an argument.
It loads a ".env" file from the project root directory
and reads the config.
```

```python
configure_api(local)

This function is called when the program starts up. It checks whether the environment variable DOCUMATIC_API_KEY is set and if the key has been validated. If it is set and not validated, it removes it.
```
