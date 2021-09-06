Certbot-Vault
=============

How to setup test env documented [here](https://certbot.eff.org/docs/contributing.html#running-manual-integration-tests).

Currently supports only kv store.

Generate test cert:

    certbot_test --standalone -d test.example.com

Install cert:

    certbot_test install -i vault --cert-name test.example.com

This is rather a PoC for newer versions of certbot, but it can be easily modified to support other features in Vault.
