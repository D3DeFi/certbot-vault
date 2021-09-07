from setuptools import setup

setup(
    name='certbot-vault',
    version='0.1.0',
    description='Certbot plugin for interaction with HashiCorp Vault',
    url='https://github.com/D3DeFi/certbot-vault',
    package='vault.py',
    author='Dusan Matejka',
    author_email='d3defi@gmail.com',
    install_requires=[
        'certbot',
        'hvac'
    ],
    python_requires='>=3.6',
    include_package_data=True,
    entry_points={
        'certbot.plugins': [
            'vault = vault:Installer',
        ],
    },
)
