"""
VS Code utility functions for opening files and directories
"""

import subprocess
from typing import List, Optional

from .settings import VSCODE_PATH


def open_in_vscode(path: str, new_window: bool = False, wait: bool = False) -> int:
    """
    Open a file or directory in VS Code

    Args:
        path: File or directory path to open
        new_window: Open in a new window
        wait: Wait for the file to be closed before returning

    Returns:
        Exit code from VS Code command
    """
    cmd: List[str] = [VSCODE_PATH]

    if new_window:
        cmd.append("-n")

    if wait:
        cmd.append("-w")

    cmd.append(path)

    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode


def open_multiple_in_vscode(
    paths: List[str],
    new_window: bool = False,
    wait: bool = False
) -> int:
    """
    Open multiple files or directories in VS Code

    Args:
        paths: List of file or directory paths to open
        new_window: Open in a new window
        wait: Wait for all files to be closed before returning

    Returns:
        Exit code from VS Code command
    """
    cmd: List[str] = [VSCODE_PATH]

    if new_window:
        cmd.append("-n")

    if wait:
        cmd.append("-w")

    cmd.extend(paths)

    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode


def open_diff_in_vscode(file1: str, file2: str) -> int:
    """
    Open a diff comparison between two files in VS Code

    Args:
        file1: First file path
        file2: Second file path

    Returns:
        Exit code from VS Code command
    """
    cmd = [VSCODE_PATH, "-d", file1, file2]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode


def open_at_line(file_path: str, line: int, column: Optional[int] = None) -> int:
    """
    Open a file at a specific line (and optionally column) in VS Code

    Args:
        file_path: File path to open
        line: Line number to jump to
        column: Optional column number to jump to

    Returns:
        Exit code from VS Code command
    """
    if column:
        path_with_position = f"{file_path}:{line}:{column}"
    else:
        path_with_position = f"{file_path}:{line}"

    cmd = [VSCODE_PATH, "-g", path_with_position]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode
