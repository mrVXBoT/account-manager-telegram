# Contributing to Telegram Account Manager Bot

Thank you for considering contributing to the Telegram Account Manager Bot! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct. Please be respectful and considerate of others.

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue on GitHub with the following information:

1. A clear, descriptive title
2. A detailed description of the bug
3. Steps to reproduce the bug
4. Expected behavior
5. Actual behavior
6. Screenshots (if applicable)
7. Environment information (OS, Python version, etc.)

### Suggesting Features

We welcome feature suggestions! To suggest a feature:

1. Create an issue on GitHub with a clear, descriptive title
2. Provide a detailed description of the feature
3. Explain why this feature would be useful
4. Provide examples of how the feature would work

### Pull Requests

We actively welcome pull requests:

1. Fork the repository
2. Create a new branch for your feature or bugfix
3. Make your changes
4. Add or update tests as necessary
5. Ensure all tests pass
6. Update documentation as needed
7. Submit a pull request

#### Pull Request Guidelines

- Follow the existing code style
- Write clear, descriptive commit messages
- Include tests for new features
- Update documentation for any changed functionality
- Keep pull requests focused on a single topic

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/mrVXBoT/account-manager-telegram.git
   cd account-manager-telegram
   ```

2. Set up a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your configuration:
   ```
   BOT_TOKEN=your_bot_token_here
   DATA_DIR=data
   ```

## Code Style

- Follow PEP 8 guidelines
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Keep functions focused on a single task
- Use type hints where appropriate

## Testing

- Write tests for new features
- Ensure all tests pass before submitting a pull request
- Run tests with:
  ```bash
  pytest
  ```

## Documentation

- Update the README.md file with any new features or changes
- Add docstrings to all new functions and classes
- Keep documentation up-to-date with code changes

## Contact

If you have any questions, feel free to reach out to [@KOXVX](https://t.me/KOXVX) on Telegram.

Thank you for your contributions!
