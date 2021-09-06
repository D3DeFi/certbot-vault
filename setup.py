from setuptools import setup

setup(
    name='certbot-vault',
    version='0.1.0',
    description='Certbot plugin for interaction with HashiCorp Vault',
    package='vault.py',
    install_requires=[
        'certbot',
        'hvac'
    ],
    entry_points={
        'certbot.plugins': [
            'vault = vault:Installer',
        ],
    },
)
