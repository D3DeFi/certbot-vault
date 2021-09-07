from setuptools import setup
from setuptools import find_packages

setup(
    name='certbot-vault',
    version='0.1.1',
    description='Certbot plugin for interaction with HashiCorp Vault',
    url='https://github.com/D3DeFi/certbot-vault',
    author='Dusan Matejka',
    author_email='d3defi@gmail.com',
    install_requires=[
        'certbot',
        'hvac'
    ],
    python_requires='>=3.6',
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'certbot.plugins': [
            'vault = certbot_vault.vault:Installer',
        ],
    },
)
