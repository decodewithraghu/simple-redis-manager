# Redis Environment Manager CLI

A powerful and user-friendly command-line tool for managing multiple Redis instances across different environments. It provides a safe, menu-driven interface, supporting both pre-configured environments and custom on-the-fly connections.

This project is managed using [Poetry](https://python-poetry.org/) for dependency management and packaging.

## Key Features

-   **Modern Project Management**: Uses Poetry for deterministic builds and easy dependency management.
-   **Secure External Configuration**: Keeps credentials and connection details separate from source code in a `config.ini` file.
-   **Multi-Environment Support**: Easily switch between different Redis instances defined in your configuration.
-   **Custom On-the-fly Connections**: Connect to any Redis instance by providing connection details directly in the CLI.
-   **Visual Feedback**: An animated spinner provides feedback while performing Redis operations, so you know the application is working.
-   **Advanced Connection Control**:
    -   **TLS Support**: Securely connect to cloud-based Redis instances (like Azure or AWS) using TLS.
    -   **Certificate Verification**: Intelligently uses `certifi` for reliable certificate validation, with options to provide a custom CA bundle or disable verification for trusted environments.
    -   **Legacy Mode**: Ensures compatibility with older Redis servers or proxies by using the RESP2 protocol.
-   **Interactive & Safe**: A clear, menu-driven interface with confirmation prompts for destructive operations like `FLUSH`.

## Demo

```
--- Please select a Redis Environment ---
  1) DEV (localhost:6379)
  2) QA-AZURE (your-azure-redis.redis.cache.windows.net:6380)
-------------------------
  3) ✨ Enter Custom Connection Details
  4) Exit
-----------------------------------------
Enter your choice: 2

⠧ Connecting to QA-AZURE...
✔ Successfully connected to QA-AZURE Redis.
   Press Enter to continue...

--- Connected to QA-AZURE ---
  1) Get all keys
  2) Delete a specific key
  ...
[QA-AZURE]> 1
⠧ Fetching keys...
✔ Keys fetched.
-> Found 3 keys:
   1) session:user:123
   2) cache:product:456
   3) queue:high-priority

Press Enter to continue...
```

## Prerequisites

-   Python 3.8+
-   [Poetry](https://python-poetry.org/docs/#installation)
-   (Optional but Recommended) [uv](https://github.com/astral-sh/uv) for faster performance.

## Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/redis-cli-tool.git
    cd redis-cli-tool
    ```

2.  **(Optional) Configure Poetry to use `uv` for lightning-fast installs:**
    ```bash
    pipx install uv
    poetry config virtualenvs.installer uv
    ```

3.  **Install dependencies:**
    This command will create a dedicated virtual environment and install all required packages (`redis`, `halo`, `certifi`).
    ```bash
    poetry install
    ```

4.  **Create your configuration file:**
    Copy the example configuration file. This file is safely ignored by Git to protect your credentials.
    ```bash
    cp config.ini.example.example config.ini.example
    ```

5.  **Edit your configuration:**
    Open `config.ini` and replace the placeholder values with your actual Redis connection details. See the **Configuration** section below for details on all available options.

## Usage

To run the application, use the `poetry run` command, which executes the script entry point defined in `pyproject.toml`:

```bash
poetry run redis-manager
```

The program will guide you through selecting a pre-configured environment or entering custom connection details.

## Configuration (`config.ini`)

The `config.ini` file allows you to define reusable connection profiles for your different Redis environments.

```ini
# Example Environment for Azure Redis
[qa-azure]
# The server hostname or IP address.
host = your-azure-redis.redis.cache.windows.net

# The port number. Use 6380 for TLS, 6379 for non-TLS.
port = 6380

# The Redis database number (0-15).
db = 0

# The password or access key for the Redis instance.
password = your_azure_password

# Set to true to enable a secure TLS connection.
tls = true

# (Optional) Set to false to disable RESP3 and use the older RESP2 protocol.
legacymode = false

# (Optional, Advanced) Set to false to disable TLS certificate verification. INSECURE.
tls_verify = true

# (Optional, Advanced) Provide a path to a custom CA certificate bundle file.
tls_ca_certs_path = 
```

## Troubleshooting

#### Error: `(54, 'Connection reset by peer')`

-   **Cause**: This is a networking error, usually caused by an SSL/TLS mismatch. You are likely trying to make a non-secure connection to a port that requires TLS.
-   **Solution**:
    1.  Ensure you are using the correct TLS port (usually **6380**).
    2.  Set `tls = true` in your `config.ini` for that environment, or answer **'y'** to the "Enable TLS?" prompt for a custom connection.

#### Error: `SSL: CERTIFICATE_VERIFY_FAILED`

-   **Cause**: The program cannot verify the server's TLS certificate against its list of trusted Certificate Authorities (CAs). This is common on corporate networks with proxies or on systems with outdated CA stores.
-   **Solution**:
    1.  **Recommended**: The tool automatically uses the `certifi` package's up-to-date CA bundle, which should resolve this in most cases. Ensure you have run `poetry install`.
    2.  **Corporate Proxy**: If your company uses a proxy, get the company's CA certificate file and provide the path in the `tls_ca_certs_path` setting in your `config.ini`.
    3.  **Insecure Last Resort**: If you are in a secure, trusted development environment, you can set `tls_verify = false` in your `config.ini` or answer **'n'** to the "Verify TLS Certificate?" prompt to bypass the check. **Do not do this in production.**

## License

This project is licensed under the MIT License.