# Python Boilerplate <!-- omit in toc -->

<details open="open">
<summary>Table of Contents</summary>

<!-- TOC -->

- [About this project](#about-this-project)
  - [Made with](#made-with)
- [Getting started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Local installation](#local-installation)
- [Usage](#usage)
- [Vision and roadmap](#vision-and-roadmap)
- [Contributing](#contributing)
- [License](#license)
- [Maintainers](#maintainers)
- [Acknowledgements](#acknowledgements)

<!-- /TOC -->

</details>

## About this project

<!-- TODO: Replace with a brief description of your own project -->

SchemaVer is a python package and command line tool to help users manage the [Schema Version](https://docs.snowplow.io/docs/pipeline-components-and-applications/iglu/common-architecture/schemaver/) of JSON schemas and OpenAPI schema objects.

### Made with

- [poetry](https://python-poetry.org/) - Dependency management library that makes creating and installing packages more streamlined.
- [pytest](https://docs.pytest.org/en/6.2.x/) - Simplifies the design and execution of both unit and integration testing.
- [black](https://black.readthedocs.io/en/stable/) - Autoformats code for consistent styling.
- [ruff]() - Lints and formats code.
- [pylint](https://www.pylint.org/) - Checks that code follows idiomatic best practices for Python.
- [pre-commit](https://pre-commit.com/) - Runs code quality checks before code is committed.

## Getting started

### Prerequisites

- Python installed on your local machine, a version 3.11 or greater
- Poetry installed on your local machine

In order to check that you have both Python and Poetry installed, run the following in your command line, and the output should look something like this:

> **NOTE**: in all of the code blocks below, lines preceded with $ indicate commands you should enter in your command line (excluding the $ itself), while lines preceded with > indicate the expected output from the previous command.

```
$ python --version && poetry --version
> Python 3.9.0
> Poetry version 1.1.6
```

**TROUBLESHOOTING:** If you receive an error message, or the version of python you have installed is not between 3.7 and 3.9, consider using a tool like [pyenv](https://github.com/pyenv/pyenv) (on Mac/Linux) or [pyenv-win](https://github.com/pyenv-win/pyenv-win) (on Windows) to manage multiple python installations.

If you have python installed but not poetry, follow these installation instructions:

- [Global install on Mac/Linux](https://python-poetry.org/docs/#osx--linux--bashonwindows-install-instructions)
- [Global install on Windows](https://python-poetry.org/docs/#windows-powershell-install-instructions)
- Local install inside a virtual environment using `pip` **NOTE:** This is not recommended because of potential package conflicts:
  - Create a virtual environment: `python -m venv env`
  - Acvitate the virtual environment. **NOTE:** This virtual environment must be active any time you are working with this project:
    - Mac/Linux: `source env/bin/activate`
    - Windows: `env\Scripts\activate`
  - Install poetry: `pip install poetry`

### Local installation

1. [Clone the repository](https://docs.github.com/en/github/creating-cloning-and-archiving-repositories/cloning-a-repository-from-github/cloning-a-repository) on your local machine
2. Change directory into the cloned project: `cd schemaver`
3. Set up the project: `make setup`

## Usage

TODO

## Vision and roadmap

The vision for this package and CLI tool is to simplify the process of managing migrations between JSON schemas to ensure that a schema repository is versioned using the [SchemaVer format proposed by Snowplow](https://docs.snowplow.io/docs/pipeline-components-and-applications/iglu/common-architecture/schemaver/)

- Adopting a common python package file structure
- Implementing basic linting and code quality checks
- Reinforcing compliance with those code quality checks using CI/CD
- Providing templates for things like documentation, issues, and pull requests
- Offering pythonic implementation examples of common data structures and scripting tasks like:
  - Creating classes, methods, and functions
  - Setting up unit and integration testing
  - Reading and writing to files

For a more detailed breakdown of the feature roadmap and other development priorities please reference the following links:

- [Feature Roadmap](https://github.com/widal001/python-boilerplate/projects/1)
- [Architecture Decisions](https://github.com/widal001/python-boilerplate/projects/2)
- [Bug Fixes](https://github.com/widal001/python-boilerplate/projects/3)
- [All Issues](https://github.com/widal001/python-boilerplate/issues)

## Contributing

Contributions are always welcome! We encourage contributions in the form of discussion on issues in this repo and pull requests for improvements to documentation and code.

See [CONTRIBUTING.md](CONTRIBUTING.md) for ways to get started.

## License

Distributed under the MIT License. See [LICENSE](LICENSE) for more information.

## Maintainers

- [@widal001](https://github.com/widal001)

## Acknowledgements

- [Python Packaging Authority Sample Project](https://github.com/pypa/sampleproject)
- [Best README Template](https://github.com/othneildrew/Best-README-Template)
