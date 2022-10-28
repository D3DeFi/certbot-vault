"""Vault Installer"""
import logging

from certbot import errors, interfaces
from certbot.compat import os
from certbot.plugins import common
import configobj
import hvac


logger = logging.getLogger(__name__)

class Installer(common.Installer, interfaces.RenewDeployer):
    """Certbot Vault Installer plugin

    This plugin allows certbot to push certificates to a Vault server
    """
    description = "Certbot Vault Installer plugin"

    @classmethod
    def add_parser_arguments(cls, add):
        add('credentials',
            help='HashiCorp Vault credentials INI file - absolute path')
        add('path',
            help=('Path in Vault where to store SSL - e.g. kv/$domain (where '
                  'kv is mount point of secret engine and $domain is appended'
                  ' automatically)'),
            default='kv/letsencrypt')
        add('dpath',
            help=('Overrides domain in path component if domain name is not'
                  ' desirable (e.g. wildcard)'),
                  default='')
        add('single',
            help=('Prevent Certbot from uploading SSL multiple times for each '
                  'SAN provided. It will instead upload for the 1st one'),
            action='store_true', default=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.curr = ''  # flag to test if we have multiple iterations

    def prepare(self):
        logger.info('Attempting to parse credentials INI file %s',
                    self.conf('credentials'))
        try:
            self.confobj = configobj.ConfigObj(  # pylint: disable=attribute-defined-outside-init
                self.conf('credentials'))

        except configobj.ConfigObjError as e:  # pylint: disable=invalid-name
            logger.debug('Error parsing credentials configuration: %s', e,
                         exc_info=True)
            raise errors.PluginError(
                f'Error parsing credentials configuration: {e}')

        addr = self.confobj.get(
            'vault-addr', default=os.environ.get('VAULT_ADDR', ''))
        token = self.confobj.get(
            'vault-token', default=os.environ.get('VAULT_TOKEN', ''))

        if not addr or not token:
            logger.error(
                'Error fetching "vault-addr" or "vault-token" from credentials'
                ' INI file or ENV variables')
            raise errors.PluginError(
                'Error fetching "vault-addr" or "vault-token" credentials')


        logger.info('Got URL: %s. Attempting to log in...', addr)
        self.client = hvac.Client(addr, token=token)  # pylint: disable=attribute-defined-outside-init

        logger.info('Verifying authentication success...')
        if not self.client.is_authenticated():
            logger.error('Authentication against Vault failed!')
            raise errors.PluginError(
                f"Error authenticating against Vault server: {e}")

        logger.info('Checking if token is set to expire...')
        token_info = self.client.lookup_token()
        if token_info['renewable']:
            logger.info('Attempting to renew token...')
            self.client.renew_token(token)

    def more_info(self):
        return "Uploads LE certificates to HashiCorp Vault Server."

    def get_all_names(self):
        return []

    def deploy_cert(  # pylint: disable=too-many-arguments
            self, domain, cert_path, key_path, chain_path, fullchain_path):
        """
        Parses mount-point and path, and uploads certificate(s) to the
        Vault Server, assuming that the connection was successful in the
        prepare function.

        :param domain: The domain for which the certificate was issued
        :param cert_path: The path to the cert file.
        :param key_path: The path to the private key file.
        :param chain_path: The path to the chain file.
        :param fullchain_path: The path to the fullchain file.
            Currently unused
        """
        del fullchain_path  # Unused in this plugin

        logger.info('Parsing mount point from path...')
        path_comp = self.conf('path').split('/')
        mount_point = os.path.join(path_comp[0])
        dpath = self.conf('dpath')  # override domain component in path if defined
        path = (f'{os.path.join("/", *path_comp[1:])}/'
                f'{dpath if dpath else domain}')
        print(path)

        if self.conf('single') and self.curr:
            logger.info(
                '--vault-single provided, not uploading for SAN %s', domain)
        else:
            self.curr = domain
            secret = {}

            logger.info(
                'Attempting to upload SSL to path %s under mount point %s...',
                path, mount_point)
            for k, v in {'crt': cert_path, 'privkey': key_path,  # pylint: disable=invalid-name
                         'chain': chain_path}.items():
                with open(v, 'r') as f:  # pylint: disable=invalid-name, unspecified-encoding
                    secret[k] = f.read()

            logger.info('Uploading for SAN %s...', domain)
            self.client.secrets.kv.v2.create_or_update_secret(
                path=path, secret=secret, mount_point=mount_point)

    def enhance(self, domain, enhancement, options=None):
        pass

    def supported_enhancements(self):
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

    def renew_deploy(self, lineage, *args, **kwargs):
        # To comply with pylint's style guide, the unused parameters
        # are deleted
        del args, kwargs  # Unused here
        logger.info('Triggering certificate deployer during renewal...')

        # mimick certbot behavior as each SAN calls deploy_cert() and
        # we want to let deploy_cert() sort out
        # how to upload certificates based on options in renewal/ conf
        # directory
        for san in lineage.names():
            self.deploy_cert(san, lineage.cert_path, lineage.key_path,
                             lineage.chain_path, lineage.fullchain_path)
