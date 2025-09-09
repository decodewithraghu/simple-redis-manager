import redis
import sys
import os
import configparser
from typing import Dict, Optional, Any, List
from halo import Halo
import certifi

# Define type aliases for clarity
EnvConfig = Dict[str, Dict[str, str]]
ConnectionDetails = Dict[str, Any]

def clear_screen():
    """Clears the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

class RedisManager:
    """
    A command-line application for managing multiple Redis environments.
    """
    def __init__(self, config: EnvConfig):
        """Initializes the manager with loaded configuration."""
        self.config: EnvConfig = config
        self.redis_conn: Optional[redis.Redis] = None
        self.current_env_name: Optional[str] = None

        self.menu_actions = {
            '1': self._get_all_keys,
            '2': self._delete_a_key,
            '3': self._get_key_data,
            '4': self._set_key_data,
            '5': self._find_keys_by_pattern,
            '6': self._delete_keys_by_pattern,
            '7': self._flush_all_keys,
        }

    def _select_environment(self) -> Optional[str]:
        """Displays a menu for the user to select an environment or a custom connection."""
        clear_screen()
        print("--- Please select a Redis Environment ---")
        env_keys = list(self.config.keys())
        for i, env in enumerate(env_keys, 1):
            host = self.config[env].get('host', 'N/A')
            port = self.config[env].get('port', 'N/A')
            print(f"  {i}) {env.upper()} ({host}:{port})")

        print("-" * 25)
        print(f"  {len(env_keys) + 1}) ✨ Enter Custom Connection Details")
        print(f"  {len(env_keys) + 2}) Exit")
        print("-----------------------------------------")

        while True:
            try:
                choice = input("Enter your choice: ")
                choice_num = int(choice)
                if 1 <= choice_num <= len(env_keys):
                    return env_keys[choice_num - 1]
                elif choice_num == len(env_keys) + 1:
                    return 'custom'
                elif choice_num == len(env_keys) + 2:
                    return None
                else:
                    print("Invalid choice. Please try again.")
            except (ValueError, IndexError):
                print("Invalid input. Please enter a number from the list.")

    def _prompt_for_custom_details(self) -> Optional[ConnectionDetails]:
        """Prompts the user for ad-hoc Redis connection details."""
        clear_screen()
        print("--- Enter Custom Connection Details ---")
        details: ConnectionDetails = {}
        try:
            details['host'] = input("Host: ").strip()
            if not details['host']: return None

            port_str = input("Port [e.g., 6380 for TLS]: ").strip()
            details['port'] = int(port_str) if port_str else 6380

            db_str = input("DB [0]: ") or '0'
            details['db'] = int(db_str)

            details['password'] = input("Password: ") or None

            tls_choice = input("Enable TLS? (y/n) [y]: ").lower().strip() or 'y'
            if tls_choice in ('y', 'yes'):
                details['tls'] = True

                verify_choice = input("  -> Verify TLS Certificate? (y/n) [y]: ").lower().strip() or 'y'
                if verify_choice in ('n', 'no'):
                    print("  ⚠️ WARNING: Disabling TLS verification is insecure.")
                    details['tls_verify'] = False
                else:
                    details['tls_verify'] = True
                    custom_ca = input("  -> Path to custom CA bundle? (optional): ").strip()
                    if custom_ca:
                        details['tls_ca_certs_path'] = custom_ca
            else:
                details['tls'] = False

            legacy_choice = input("Enable Legacy Mode (RESP2)? (y/n) [n]: ").lower().strip() or 'n'
            details['legacymode'] = legacy_choice in ('y', 'yes')

            return details
        except (ValueError, KeyboardInterrupt, EOFError):
            print("\nInvalid input or connection cancelled.")
            return None

    def _connect(self, conn_details: ConnectionDetails, display_name: str) -> bool:
        """Establishes a connection to Redis using provided details."""
        spinner = Halo(text=f"Connecting to {display_name}...", spinner='dots')
        try:
            final_conn_details = conn_details.copy()

            # Translate user-friendly 'tls' options to library-specific 'ssl' options
            is_tls = str(final_conn_details.get('tls', 'false')).lower() in ('true', '1', 'y', 'yes')
            is_legacy = str(final_conn_details.get('legacymode', 'false')).lower() in ('true', '1', 'y', 'yes')

            final_conn_details['ssl'] = is_tls

            if is_legacy:
                final_conn_details['protocol'] = 2

            if is_tls:
                verify_tls = str(final_conn_details.get('tls_verify', 'true')).lower() in ('true', '1', 'y', 'yes')
                if not verify_tls:
                    final_conn_details['ssl_cert_reqs'] = None
                else:
                    custom_ca_path = final_conn_details.get('tls_ca_certs_path')
                    if custom_ca_path and os.path.exists(custom_ca_path):
                        final_conn_details['ssl_ca_certs'] = custom_ca_path
                    else:
                        final_conn_details['ssl_ca_certs'] = certifi.where()

            # Clean up our custom user-facing keys before passing to redis-py
            final_conn_details.pop('tls', None)
            final_conn_details.pop('tls_verify', None)
            final_conn_details.pop('tls_ca_certs_path', None)
            final_conn_details.pop('legacymode', None)

            spinner.start()
            self.redis_conn = redis.Redis(**final_conn_details, decode_responses=True, socket_connect_timeout=5)
            self.redis_conn.ping()
            self.current_env_name = display_name
            spinner.succeed(f"Successfully connected to {display_name} Redis.")
            input("   Press Enter to continue...")
            return True
        except Exception as e:
            spinner.fail(f"Failed to connect to {display_name}: {e}")
            self.redis_conn = None
            input("   Press Enter to return...")
            return False

    def _show_operations_menu(self):
        clear_screen()
        print(f"--- Connected to {self.current_env_name} ---")
        print("  1) Get all keys")
        print("  2) Delete a specific key")
        print("  3) Get the value for a key")
        print("  4) Set a new key-value pair")
        print("  ---------------------------------")
        print("  5) Find keys by pattern")
        print("  6) DANGER: Delete keys by pattern")
        print("  7) DANGER: Delete ALL keys (FLUSH)")
        print("  ---------------------------------")
        print("  8) Go back (select another environment)")
        print("  9) Exit")
        print("------------------------------------")

    def _operations_loop(self):
        while True:
            self._show_operations_menu()
            choice = input(f"[{self.current_env_name}]> ")
            if choice == '8': # Go back
                print("Returning to environment selection...")
                break
            if choice == '9': # Exit
                raise SystemExit("Goodbye!")
            action = self.menu_actions.get(choice)
            if action:
                action()
                input("\nPress Enter to continue...")
            else:
                print("Invalid choice. Please enter a number from the list.")

    def run(self):
        while True:
            choice = self._select_environment()
            if choice is None:
                raise SystemExit("Goodbye!")
            conn_details: Optional[ConnectionDetails] = None
            display_name = ""
            if choice == 'custom':
                conn_details = self._prompt_for_custom_details()
                if conn_details:
                    display_name = f"Custom ({conn_details['host']}:{conn_details['port']})"
            else:
                conn_details = self.config[choice]
                display_name = choice.upper()
            if conn_details and self._connect(conn_details, display_name):
                self._operations_loop()

    # --- CRUD and Management Methods ---
    def _get_all_keys(self):
        self._find_and_display_keys('*', 'Fetching all keys...')

    def _delete_a_key(self):
        key = input("Enter the key to delete: ").strip()
        if not key:
            print("-> Operation cancelled (no key provided).")
            return
        spinner = Halo(text=f"Deleting key '{key}'...", spinner='dots')
        try:
            spinner.start()
            deleted_count = self.redis_conn.delete(key)
            if deleted_count > 0:
                spinner.succeed(f"Key '{key}' was deleted.")
            else:
                spinner.warn(f"Key '{key}' not found.")
        except Exception as e:
            spinner.fail(f"Failed to delete key: {e}")

    def _get_key_data(self):
        key = input("Enter key to get value: ").strip()
        if not key:
            print("-> Operation cancelled (no key provided).")
            return
        spinner = Halo(text=f"Fetching value for '{key}'...", spinner='dots')
        try:
            spinner.start()
            value = self.redis_conn.get(key)
            spinner.stop()
            if value is not None:
                print(f'-> Value: "{value}"')
            else:
                print("-> (nil) - Key does not exist.")
        except Exception as e:
            spinner.fail(f"Failed to get key: {e}")

    def _set_key_data(self):
        key = input("Enter the new key: ").strip()
        if not key:
            print("-> Operation cancelled (no key provided).")
            return
        value = input(f"Enter the value for '{key}': ")
        spinner = Halo(text=f"Setting key '{key}'...", spinner='dots')
        try:
            spinner.start()
            self.redis_conn.set(key, value)
            spinner.succeed(f"OK - Key '{key}' set.")
        except Exception as e:
            spinner.fail(f"Failed to set key: {e}")

    def _find_keys_by_pattern(self):
        pattern = input("Enter search pattern (e.g., 'user:*', 'session:???'): ").strip()
        if not pattern:
            print("-> No pattern entered. Operation cancelled.")
            return
        self._find_and_display_keys(pattern, f"Scanning for keys matching '{pattern}'...")

    def _find_and_display_keys(self, pattern: str, message: str) -> List[str]:
        """Helper to find keys with SCAN and display them."""
        spinner = Halo(text=message, spinner='dots')
        try:
            spinner.start()
            keys = sorted(list(self.redis_conn.scan_iter(pattern)))
            spinner.succeed('Scan complete.')
            if not keys:
                print(f"-> No keys found matching pattern '{pattern}'.")
                return []
            else:
                print(f"-> Found {len(keys)} matching keys:")
                for i, key in enumerate(keys, 1):
                    print(f"   {i}) {key}")
                return keys
        except Exception as e:
            spinner.fail(f"Failed to scan keys: {e}")
            return []

    def _delete_keys_by_pattern(self):
        pattern = input("Enter pattern for keys to DELETE (e.g., 'temp:*'): ").strip()
        if not pattern:
            print("-> No pattern entered. Deletion cancelled.")
            return

        print("\nFirst, finding keys that match this pattern...")
        keys_to_delete = self._find_and_display_keys(pattern, f"Scanning for keys matching '{pattern}'...")
        if not keys_to_delete:
            return

        print("\n" + "="*40)
        print("⚠️  DANGER ZONE: Review the keys above carefully. ⚠️")
        print("="*40)
        confirm = input(f"Type 'DELETE' to permanently delete these {len(keys_to_delete)} keys: ")
        if confirm != 'DELETE':
            print("\nConfirmation did not match. Deletion cancelled.")
            return

        spinner = Halo(text=f'Deleting {len(keys_to_delete)} keys...', spinner='dots')
        try:
            spinner.start()
            deleted_count = 0
            chunk_size = 500
            for i in range(0, len(keys_to_delete), chunk_size):
                chunk = keys_to_delete[i:i + chunk_size]
                deleted_count += self.redis_conn.delete(*chunk)
            spinner.succeed(f"Successfully deleted {deleted_count} keys.")
        except Exception as e:
            spinner.fail(f"An error occurred during deletion: {e}")

    def _flush_all_keys(self):
        confirm = input(f"DANGER! This will delete all keys in {self.current_env_name}. Type '{self.current_env_name}' to confirm: ")
        if confirm != self.current_env_name:
            print("-> Confirmation did not match. Operation cancelled.")
            return
        spinner = Halo(text=f'Flushing database for {self.current_env_name}...', spinner='dots')
        try:
            spinner.start()
            self.redis_conn.flushdb()
            spinner.succeed("Database has been flushed.")
        except Exception as e:
            spinner.fail(f"Failed to flush database: {e}")

# --- Main execution logic ---
def load_configuration(filepath: str) -> Optional[EnvConfig]:
    parser = configparser.ConfigParser()
    if not os.path.exists(filepath):
        return None
    parser.read(filepath)
    return {section: dict(parser.items(section)) for section in parser.sections()}

def main():
    config_file = 'config.ini'
    config = load_configuration(config_file)
    if not config:
        config = {}
        print("Warning: 'config.ini' not found. Only custom connections will be available.")
    try:
        app = RedisManager(config)
        app.run()
    except (KeyboardInterrupt, SystemExit, EOFError) as e:
        print(f"\n{e}")
        sys.exit(0)

if __name__ == "__main__":
    main()
