Certbot-Vault
=============

Running
-------

Create file with credentials (e.g. /etc/letsencrypt/.hashicorp-vault-creds):
```ini
vault-addr=https://vault.example.com:8200/
vault-token=s.AADSFSDHJGJHGDFGSERWETTRHTT
```

Or define ENV files:
```bash
export VAULT_ADDR=https://vault.example.com:8200/
export VAULT_TOKEN=s.AADSFSDHJGJHGDFGSERWETTRHTT
```

Run installer plugin separately (skip `--vault-credentials` if creds were provided via ENV variables):
```bash
certbot install -i vault --vault-credentials=/etc/letsencrypt/.hashicorp-vault-creds --vault-path='secret/le-certs' --vault-single --cert-name example.com
```

Or as a part or certbot run:
```bash
certbot run -a ..... -i vault ... -d example.com,www.example.com
```

CLI arguments
-------------

* `--vault-credentials` - INI file with `vault-addr=XYZ` and `vault-token=XYZ` key pairs. If not provided, script will attempt to read ENV variables `VAULT_ADDR` and `VAULT_TOKEN`.
* `--vault-path` - path in Vault where to store certificates, first component is expected to be engine mount point (e.g. secret, kv, etc...).
* `--vault-dpath` - last component of path is always taken from certificate's SAN (e.g. kv/\*.example.com). This option can override the domain to something else.
* `--vault-single` - upload certs only once if provided multiple SANs via `-d example.com,www.example.com` - in this case only kv/letsencrypt/example.com will be created.

Developing
----------

How to setup test env documented [here](https://certbot.eff.org/docs/contributing.html#running-manual-integration-tests). Tl;dr version below:

    # clone upstream certbot
    git clone https://github.com/certbot/certbot.git
    cd certbot

    # setup virtualenv and install our plugin
    python3 tools/venv.py
    source venv/bin/activate
    pip install -e ../certbot-vault

    # run testing ACME server
    run_acme_server &

    # start Vault dev server and copy root token
    vault server -dev &

    # generate credentials file for certbot-vault plugin
    echo -e 'vault-addr=http://127.0.0.1:8200\nvault-token=ABCDEFG' > ~/dev-hashi-certbot

    # issue test certficate
    certbot_test run --standalone -d test.example.com -i vault --vault-credentials ~/dev-hashi-certbot --vault-path secret/

    # now it should be present in Vault, after checking it, you can try to renew for example
    certbot_test renew

Currently supports only kv store.

Generate test cert:

    certbot_test certonly --standalone -d test.example.com

Install cert:

    certbot_test install -i vault --cert-name test.example.com

This is rather a PoC for newer versions of certbot, but it can be easily modified to support other features in Vault.
