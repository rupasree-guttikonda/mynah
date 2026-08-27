# mynah/tools/keychain.py
"""
Secure secret storage integration with macOS native Keychain.
Exposes tools to set and get sensitive credentials safely.
"""

import subprocess

def set_secret(service: str, account: str, secret: str) -> str:
    """
    Saves a password or token securely in the macOS Keychain.
    This is an irreversible tool since it overwrites/stores credentials.
    """
    try:
        # Use macOS security command line tool
        cmd = [
            "/usr/bin/security", "add-generic-password",
            "-a", account,
            "-s", service,
            "-w", secret,
            "-U" # Update password if it already exists
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=2.0)
        if res.returncode == 0:
            return f"Successfully saved secret for {service}/{account} in macOS Keychain."
        else:
            return f"Failed to save secret: {res.stderr.strip()}"
    except Exception as e:
        return f"Keychain error: {str(e)}"

def get_secret(service: str, account: str) -> str:
    """
    Retrieves a secret password or token from the macOS Keychain.
    This is classified as a safe tool.
    """
    try:
        cmd = [
            "/usr/bin/security", "find-generic-password",
            "-a", account,
            "-s", service,
            "-w" # Only output the secret string
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=2.0)
        if res.returncode == 0:
            return res.stdout.strip()
        else:
            return f"Secret not found: {res.stderr.strip()}"
    except Exception as e:
        return f"Keychain error: {str(e)}"
