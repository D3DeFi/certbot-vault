import hvac
import logging

from sys import exit
from os import environ

from certbot import interfaces
from certbot.plugins import common


logger = logging.getLogger(__name__)



class Installer(common.Installer):

    description = "Certbot Vault Installer plugin"

    @classmethod
    def add_parser_arguments(cls, add):
        add('url', help='HashiCorp Vault Server where to upload SSL certificates', default=environ['VAULT_ADDR'])
        add('token', help='Vault Token required for authentication', default=environ['VAULT_TOKEN'])
        add('path', help='Path in Vault where to store SSL - e.g. kv/$domain (where $domain is appended automatically)', default='kv/letsencrypt')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = hvac.Client(self.conf('url'), token=self.conf('token'))

    def prepare(self):
        logger.info('Verifying authentication success...')
        if not self.client.is_authenticated():
            logger.error('Authentication against Vault failed!')
            exit(1)

        logger.info('Checking if token is set to expire...')
        token_info = self.client.lookup_token()
        if token_info['renewable']:
            logger.info('Attempting to renew token...')
            self.client.renew_token()

    def more_info(self):
        return "Uploads LE certificates to HashiCorp Vault Server."

    def get_all_names(self):
        return []

    def deploy_cert(self, domain, cert_path, key_path, chain_path, fullchain_path):
        path = f'{self.conf("path")}/{domain}'
        secret = {}

        logger.info(f'Attempting to upload SSL to path {path}...')
        for k, v in {'crt': cert_path, 'privkey': key_path, 'chain': chain_path}.items():
            with open(v, 'r') as f:
                secret[k] = f.read()
                
        self.client.secrets.kv.v2.create_or_update_secret(path=path, secret=secret)

    def enhance(self, domain, enhancement, options=None):
        pass

    def supported_enhancements(self):
        return []

    def get_all_certs_keys(self):
        return []

    def save(self, title=None, temporary=False):
        pass

    def rollback_checkpoints(self, rollback=1):
        pass

    def recovery_routine(self):
        pass

    def config_test(self):
        pass

    def restart(self):
        pass

