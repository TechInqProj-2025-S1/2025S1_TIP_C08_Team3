# PyLint GitHub Action

This repository uses GitHub Actions to automatically run PyLint for code quality checks. This README explains how the PyLint workflow is set up and how to work with it.

## How It Works

The PyLint GitHub Action will run automatically when:
- You push code to the `main` branch
- You create or update a Pull Request targeting the `main` branch

The workflow only runs on Python (.py) files.

## What It Checks

PyLint will check your code for:
- Syntax errors
- Potential bugs
- Style issues
- Bad practices

## Customizing Rules

The repository includes two files that control the PyLint behavior:

1. `.github/workflows/pylint.yml` - This defines the GitHub Action workflow
2. `.pylintrc` - This configures PyLint rules and settings

### Current Configuration

We've disabled some common rules that are often too strict for game development:
- `missing-docstring` (C0111) - Not requiring docstrings on every function/class
- `invalid-name` (C0103) - Allowing shorter variable names
- `trailing-whitespace` (C0303) - Not enforcing trailing whitespace removal
- `line-too-long` (C0301) - Allowing lines longer than 100 characters
- `too-few-public-methods` (R0903) - Allowing classes with few public methods (common in game dev)
- `too-many-instance-attributes` (R0902) - Allowing classes with many attributes
- `too-many-arguments` (R0913) - Allowing functions with many arguments
- `no-else-return` (R1705) - Allowing else after return for readability

## Handling Errors

If the PyLint action fails:

1. Check the GitHub Actions tab in your repository
2. Look at the build logs to find the errors
3. Fix the issues in your code
4. Commit and push the changes

## Running PyLint Locally

To run the same checks locally before pushing:

1. Install PyLint: `pip install pylint`
2. Run: `pylint --rcfile=.pylintrc <your_python_file.py>` 
   or: `pylint --rcfile=.pylintrc games/` to check all Python files in a directory

## Benefits

Using PyLint helps:
- Maintain consistent code style
- Catch potential bugs early
- Make code reviews easier
- Improve code readability
