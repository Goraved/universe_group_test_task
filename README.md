# universe_group_test_task

## Задача
Написати автоматизовані API тести для чату з використанням GPT-4. Необхідно перевірити коректність роботи API, а також реалізувати позитивні та негативні сценарії.

## Висновок

Фремворк написаний і основні тестові сценарії описані, проте я вперся в ліміт запитів
`received = 403 | error = {'message': 'Error: limit reached', 'details': {}}`,
а потім також в `502 Bad Gateway` тож не зможу закінчити полірування всіх тестів.

Для реалізації я вибрав `httpx` замість `requests`, що дає кілька істотних переваг: підтримка HTTP/2,
асинхронні запити, кращу продуктивність, сучасний API та вбудовану перевірку SSL сертифікатів.

Думаю, що для тестового завдання ходу думок та структури має вистачити.

## Features

- Positive and negative test scenarios for Chat GPT API
- JWT authentication testing
- Streaming response testing
- HTTP/2 support
- HTML test reports

## Quick Start with Docker

To run the tests using Docker:

```bash
# Build the Docker image
docker build -t chat-gpt-api-tests .

# Run tests with your API token
docker run --rm \
  -e API_TOKEN="your_jwt_token_here" \
  -v $(pwd)/reports:/app/reports \
  chat-gpt-api-tests
```

## Installation and Setup

### 1. Setting Up Python 3.12-dev

#### Option A: Using pyenv (Recommended for managing multiple Python versions)

**For Mac:**

```bash
# Install pyenv using Homebrew
brew install pyenv

# Add pyenv to your shell
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
echo 'eval "$(pyenv init -)"' >> ~/.zshrc
source ~/.zshrc

# Install Python 3.12-dev
pyenv install 3.12-dev
```

**For Linux:**

```bash
# Install pyenv
curl https://pyenv.run | bash

# Add pyenv to your shell
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc
source ~/.bashrc

# Install Python 3.12-dev
pyenv install 3.12-dev
```

#### Option B: Direct Installation

If you prefer not to use pyenv, you can install Python 3.12-dev directly:

- Download from [python.org](https://www.python.org/downloads/)
- Or use your system's package manager (apt, brew, etc.)

### 2. Setting Up the Development Environment

#### Option A: Using PyCharm (Recommended)

1. **Open your project in PyCharm** or create a new one.
2. Go to menu: **File** → **Settings** (or **Preferences** on Mac).
3. Select: **Project: <your_project>** → **Python Interpreter**.
4. Click on **Add Interpreter** → **Add Local Interpreter**.
5. Choose **Virtual Environment** and make sure the path corresponds to your project folder.
6. In the **Base interpreter** field, select Python 3.12-dev (or your installed version 3.12+).
7. Click **OK** to create and activate the virtual environment.

#### Option B: Using Terminal

1. Open a terminal in your project directory.
2. Make sure `uv` is installed (if not, install it):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
3. Create and activate a virtual environment using uv:

   **For Windows:**
   ```bash
   uv venv venv
   venv\Scripts\activate
   ```

   **For Mac/Linux:**
   ```bash
   uv venv venv
   source venv/bin/activate
   ```

4. Install dependencies from requirements.txt:
   ```bash
   uv pip install -r requirements.txt
   ```

5. Set the API token environment variable:
   ```bash
   # For Mac/Linux
   export API_TOKEN="your_jwt_token_here"
   
   # For Windows
   set API_TOKEN=your_jwt_token_here
   ```

6. Run tests:
   ```bash
   pytest
   ```

### 3. Setting Up Pre-commit Hooks (Optional)

For code quality checks and automatic formatting:

```bash
uv pip install pre-commit
pre-commit install
```

This will run linting and unit tests for the base API on each commit.

## Test Scenarios

The tests cover the following scenarios:

1. **Positive Scenario**:
   - Valid chat completion request
   - Special case for health-related questions

2. **Negative Scenario - Invalid Token**:
   - Request with invalid JWT token
   - Request with invalid headers

3. **Negative Scenario - Invalid Parameters**:
   - Request with invalid body parameters
   - Request with invalid message structures

4. **Negative Scenario - Server Error**:
   - Attempt to trigger server error conditions

5. **Positive Scenario (Streaming)**:
   - Chat completion with streaming enabled

## Project Structure

```
chat-gpt-api-tests/
├── Dockerfile                # Docker configuration
├── api/                      # API client modules
│   ├── __init__.py           # APIs factory
│   ├── base_api.py           # Base API client
│   └── chat_api.py           # Chat API client
├── config/                   # Configuration files
│   └── config.py             # API configuration
├── data/                     # Test data
│   ├── __init__.py
│   └── chat_data_generator.py # Test data generator
├── tests/                    # Test modules
│   ├── __init__.py
│   ├── conftest.py           # Test fixtures
│   └── test_chat_api.py      # Chat API tests
└── reports/                  # Test reports (generated)
```

## Environment Variables

- `API_BASE_URL`: Base URL for the API (default: https://automation-qa-test.universeapps.limited)
- `API_TOKEN`: **Required** - JWT token for authentication (no default, must be provided)