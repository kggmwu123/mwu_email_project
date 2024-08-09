import subprocess
import sys


def install_requirements():
    packages = [
        'Flask',
        'pyTelegramBotAPI',
        'mysql-connector-python'
    ]

    for package in packages:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])


if __name__ == '__main__':
    install_requirements()
