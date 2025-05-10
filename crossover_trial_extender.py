import getpass
import os
import plistlib
import subprocess
import sys
from datetime import datetime, timedelta


def backup_path(path: str) -> str:
    """
    Generate a backup path for the given file.

    :param path: Path to the file.
    :return: Backup path.
    """
    split_path = path.rsplit('.', maxsplit=1)
    split_path.insert(1, 'backup')

    return '.'.join(split_path)


def save_plist(path: str, data: dict) -> None:
    """
    Save the given data to a file in plist format.

    :param path: Path to the file.
    :param data: Data to save.
    """
    with open(path, 'wb') as file:
        plistlib.dump(data, file)


def save_reg(path: str, data: list) -> None:
    """
    Save the given data to a file in registry format.

    :param path: Path to the file.
    :param data: Data to save.
    """
    with open(path, 'w') as file:
        file.writelines(data)


def update_plist(path: str) -> None:
    """
    Update the plist file to extend the trial period by resetting the FirstRunDate.

    :param path: Path to the plist file.
    """
    with open(path, 'rb') as file:
        plist_data = plistlib.load(file)

    # save a backup of the original plist file
    new_path = backup_path(path)
    save_plist(new_path, plist_data)

    # extend the trial period by resetting the FirstRunDate and saving the plist file
    plist_data['FirstRunDate'] = datetime.now() - timedelta(days=1)  # noqa: DTZ005
    save_plist(path, plist_data)


def update_reg(path: str, block_to_skip: str) -> None:
    """
    Update the registry file to remove the trial expiration block.

    :param path: Path to the registry file.
    :param block_to_skip: The block to skip in the registry file.
    """
    with open(path) as to_read_file:
        lines = to_read_file.readlines()

    inside_target = False
    new_lines = []
    for line in lines:
        clean_line = line.strip()

        if clean_line.startswith(block_to_skip):
            inside_target = True
            continue

        if inside_target and clean_line.startswith('['):
            inside_target = False

        if not inside_target:
            new_lines.append(line)

    # save a backup of the original registry file
    new_path = backup_path(path)
    save_reg(new_path, lines)
    # save the modified registry file
    save_reg(path, new_lines)


def main() -> None:
    """Main function to execute the script."""
    try:
        current_user = getpass.getuser()

        plist_path = f'/Users/{current_user}/Library/Preferences/com.codeweavers.CrossOver.plist'
        reg_path = f'/Users/{current_user}/Library/Application Support/CrossOver/Bottles/Steam/system.reg'
        reg_key = '[Software\\\\CodeWeavers\\\\CrossOver\\\\cxoffice]'

        # Extend the trial period
        update_plist(plist_path)
        update_reg(reg_path, reg_key)

        # Run CrossOver
        subprocess.run(['/usr/bin/open', '/Applications/CrossOver.app'])  # noqa: PLW1510, S603, S607

        # Exit
        sys.exit(0)
    except Exception as e:
        script = f'display dialog "{e}" with title "error" buttons ["OK"] with icon stop'
        subprocess.run(["osascript", "-e", script])


if __name__ == '__main__':
    main()
