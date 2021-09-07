import os
import hvac
import logging

from sys import exit
from certbot import interfaces
from certbot.plugins import common


logger = logging.getLogger(__name__)



class Installer(common.Installer):

    description = "Certbot Vault Installer plugin"

    @classmethod
    def add_parser_arguments(cls, add):
        add('url', help='HashiCorp Vault Server where to upload SSL certificates', default=os.environ.get('VAULT_ADDR', 'http://localhost:8200'))
        add('token', help='Vault Token required for authentication', default=os.environ.get('VAULT_TOKEN', ''))
        add('path', help='Path in Vault where to store SSL - e.g. kv/$domain (where kv is mount point of secret engine and $domain is appended automatically)', default='kv/letsencrypt')
        add('single', help='Prevent Certbot from uploading SSL multiple times for each SAN provided. It will instead upload for the 1st one', action='store_true', default=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = hvac.Client(self.conf('url'), token=self.conf('token'))
        self.curr = ''  # flag to test if we have multiple iterations

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
        logger.info('Parsing mount point from path...')
        path_comp = self.conf('path').split('/')
        mount_point = os.path.join(path_comp[0])
        path = f'{os.path.join(*path_comp[1:])}/{domain}'
        secret = {}

        if self.conf('single') and self.curr != '':
            logger.info(f'--vault-single provided, not uploading for SAN {domain}')
        else:
            self.curr = domain

            logger.info(f'Attempting to upload SSL to path {path} under mount point {mount_point}...')
            for k, v in {'crt': cert_path, 'privkey': key_path, 'chain': chain_path}.items():
                with open(v, 'r') as f:
                    secret[k] = f.read()
                
            logger.info(f'Uploading for SAN {domain}...')
            self.client.secrets.kv.v2.create_or_update_secret(path=path, secret=secret, mount_point=mount_point)

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

