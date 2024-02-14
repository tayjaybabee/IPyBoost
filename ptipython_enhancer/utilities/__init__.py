# ptipython_enhancer/utilities.py

import subprocess
import requests
import pkg_resources
from pkg_resources import parse_version
import sys
from rich.progress import Progress

__all__ = [
    "PackageManager",
    "PyPIManager",
    "pip_install"
]


INSTALL_COMMAND = [
        'pip',
        'install',
        ]


class PyPIManager:
    @staticmethod
    def get_pypi_package_versions(package_name):
        """Gets all available versions of a package from PyPI.

        Args:
            package_name (str): The name of the package.

        Returns:
            list: A list of available versions.
        """
        url = f"https://pypi.org/pypi/{package_name}/json"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            versions = sorted(data["releases"].keys(), key=parse_version)
            return versions
        else:
            print(f"Failed to fetch versions for {package_name} from PyPI.")
            return []

    @staticmethod
    def get_latest_stable_version(package_name):
        """Gets the latest stable version of a package from PyPI.

        Args:
            package_name (str): The name of the package.

        Returns:
            str: The latest stable version, or None if not found.
        """
        versions = PyPIManager.get_pypi_package_versions(package_name)
        stable_versions = [v for v in versions if "a" not in v and "b" not in v and "rc" not in v]
        if stable_versions:
            return stable_versions[-1]
        else:
            print(f"No stable versions found for {package_name}.")
            return None


class PackageManager:

    @staticmethod
    def get_install_command(package_name) -> list[str]:
        """
        Gets the pip install command for a package.

        Parameters:
            package_name (str, list):
                The name(s) of the package(s) you wish to install.

        Returns:
            list:
                A list containing the pip install command and the package name(s).
        """
        if isinstance(package_name, list):
            return INSTALL_COMMAND.copy() + package_name
        else:
            return INSTALL_COMMAND.copy() + [package_name]

    @staticmethod
    def install_package(package_name, show_output=True) -> None:
        """Installs a package using pip, capturing and printing the reason for any installation failures, including the error output.

        Args:
            package_name (str):
                The name of the package to install.

            show_output (bool):
                Whether to show the output of the installation command. Defaults to `True`.
        """
        try:
            cmd = PackageManager.get_install_command(package_name)

            if show_output:
                res = subprocess.run(cmd, text=True, capture_output=True, check=False)
                print(res.stdout)
                if res.stderr:
                    print(res.stderr, file=sys.stderr)

            else:
                subprocess.run(['pip', 'install', package_name], check=False)

            print(f"{package_name} has been installed successfully.")
        except subprocess.CalledProcessError as e:
            # Decode the stderr to a string if it's in bytes
            error_output = e.stderr.decode('utf-8') if e.stderr else 'No error output captured.'
            print(f"Failed to install {package_name}. Error: {e}\nError Output:\n{error_output}")
        except Exception as e:
            print(f"An unexpected error occurred while trying to install {package_name}: {e}")

    @staticmethod
    def is_package_installed(package_name):
        """Checks if a package is installed.

        Args:
            package_name (str): The name of the package to check.

        Returns:
            bool: True if the package is installed, False otherwise.
        """
        installed_packages = {d.key for d in pkg_resources.working_set}
        return package_name.lower() in installed_packages

    @staticmethod
    def get_package_info(package_name):
        """Gets information about a package, if installed.

        Args:
            package_name (str): The name of the package to get information about.

        Returns:
            dict: A dictionary containing 'version', 'location', and 'can_import' keys.
        """
        try:
            package = pkg_resources.get_distribution(package_name)
            can_import = True
            try:
                __import__(package_name)
            except ImportError:
                can_import = False
            return {
                "version": package.version,
                "location": package.location,
                "can_import": can_import,
            }
        except pkg_resources.DistributionNotFound:
            print(f"{package_name} is not installed.")
            return {}

    @staticmethod
    def get_pip_version():
        """
        Gets the installed version of pip.

        Returns:
            str:
                The installed version of pip.

        Example:
            >>> PackageManager.get_pip_version()
            '20.2.3'
        """
        return pkg_resources.get_distribution('pip').version

    @staticmethod
    def update_pip():
        """
        Updates pip to its latest version.

        Note:
            This method captures and prints any errors during the update process, including detailed error output,

        Returns:
            None

        Example:
            >>> PackageManager.update_pip()
            pip has been updated to the latest version successfully.
        """
        try:
            res = subprocess.run(['pip', 'install', '--upgrade', 'pip'], text=True, capture_output=True, check=False)
            print(res.stdout)
            if res.stderr:
                print(res.stderr, file=sys.stderr)
            print("pip has been updated to the latest version successfully.")
        except subprocess.CalledProcessError as e:
            # Decode the stderr to a string if it's in bytes
            error_output = e.stderr.decode('utf-8') if e.stderr else 'No error output captured.'
            print(f"Failed to update pip. Error: {e}\nError Output:\n{error_output}")
        except Exception as e:
            print(f"An unexpected error occurred while trying to update pip: {e}")


def pip_install(packages):
    """
    Installs a list of packages using pip.

    Parameters:
        packages (list, str):
            A list of package names to install.

    Returns:
        None
    """
    if isinstance(packages, str):
        packages = [packages]

    # Use the Progress class from Rich to display a progress bar
    with Progress() as progress:
        task = progress.add_task('[green]Installing packages...', total=len(packages))

        for package in packages:
            PackageManager.install_package(package)
            progress.advance(task)
