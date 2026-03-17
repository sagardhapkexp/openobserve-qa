# OpenObserve QA Automation Framework

A robust automation testing framework for OpenObserve using Playwright and Pytest.

## Features
- **Page Object Model (POM)**: Encapsulated locators and actions for high maintainability.
- **7 Automated Test Cases**:
  - Log Ingestion (4 cases)
  - Real-time Alerts (1 case)
  - Dashboard Data Rendering (1 case)
  - Pipeline Routing (1 case)
- **Virtual Environment**: Isolated dependencies for consistent execution.
- **Reporting**: Integrated Pytest-HTML and XML reporting.

## Project Structure
- `helpers/`: API utilities for ingestion and search.
- `pages/`: Page Objects for UI automation.
- `tests/`: Pytest test suites.
- `conftest.py`: Shared fixtures and configuration.
- `config.py`: Environment-based configuration.

## Setup
1. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```
3. Configure environment:
   Create a `.env` file based on `.env.example`.

## Running Tests
Run all tests:
```bash
pytest tests -v -n 1 --dist loadscope
```
