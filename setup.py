from setuptools import setup, find_packages
import os

def readme():
    with open("README.md", encoding="utf-8") as file:
        return file.read()

setup(
    name='certbot-vault-installer',
    version=os.getenv("GITHUB_REF", "0.0.0").split("/")[-1],
    description='Certbot plugin for interaction with HashiCorp Vault',
    url='https://github.com/D3DeFi/certbot-vault',
    author='Dusan Matejka',
    author_email='d3defi@gmail.com',
    install_requires=[
        'certbot',
        'hvac'
    ],
    classifiers=[
        "License :: OSI Approved :: Apache Software License"],
    license="License Apache 2",
    packages=find_packages(),
    entry_points={
        'certbot.plugins': [
            'vault = certbot_vault.vault:Installer',
        ],
    },
    long_description=readme(),
    long_description_content_type="text/markdown"
)
