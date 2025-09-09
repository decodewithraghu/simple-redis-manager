# Redis Environment Manager CLI

A powerful and user-friendly command-line tool for managing multiple Redis instances across different environments. It provides a safe, menu-driven interface, supporting both pre-configured environments and custom on-the-fly connections.

This project is managed using [Poetry](https://python-poetry.org/) for dependency management and packaging.

## Key Features

-   **Modern Project Management**: Uses Poetry for deterministic builds and easy dependency management.
-   **Secure External Configuration**: Keeps credentials and connection details separate from source code in a `config.ini` file.
-   **Multi-Environment Support**: Easily switch between different Redis instances defined in your configuration.
-   **Custom On-the-fly Connections**: Connect to any Redis instance by providing connection details directly in the CLI.
-   **Visual Feedback**: An animated spinner provides feedback while performing Redis operations.
-   **Advanced Key Management**:
    -   Find keys using wildcard patterns (`user:*`, `session:???`) using the production-safe `SCAN` command.
    -   Safely delete keys in bulk by pattern with a **"show and confirm"** step to prevent accidental data loss.
-   **Advanced Connection Control**:
    -   **TLS Support**: Securely connect to cloud-based Redis instances (like Azure or AWS) using TLS.
    -   **Certificate Verification**: Intelligently uses `certifi` for reliable certificate validation, with options to provide a custom CA bundle or disable verification for trusted environments.
    -   **Legacy Mode**: Ensures compatibility with older Redis servers or proxies by using the RESP2 protocol.
-   **Interactive & Safe**: A clear, menu-driven interface with confirmation prompts for destructive operations.

## Prerequisites

-   Python 3.8+
-   [Poetry](https://python-poetry.org/docs/#installation)

## Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/redis-cli-tool.git
    cd redis-cli-tool
    ```

2.  **Install dependencies:**
    This command will create a dedicated virtual environment and install all required packages (`redis`, `halo`, `certifi`).
    ```bash
    poetry install
    ```

3.  **Create your configuration file:**
    Copy the example configuration file. This file is safely ignored by Git to protect your credentials.
    ```bash
    cp config.ini.example config.ini
    ```

4.  **Edit your configuration:**
    Open `config.ini` and replace the placeholder values with your actual Redis connection details. See the **Configuration** section below for details on all available options.

## Usage

To run the application, use the `poetry run` command, which executes the script entry point defined in `pyproject.toml`:

```bash
poetry run redis-manager
