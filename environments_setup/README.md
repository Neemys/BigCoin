# Setup server environments [![Build Status](https://travis-ci.org/bigdata-project-march-2018-team2/BigCoin.svg?branch=environments_setup)](https://travis-ci.org/bigdata-project-march-2018-team2/BigCoin)
Create the integration and production environments using ansible.

## Requirements
 * Ansible v2.4.0+
 * Already got the private key for server connexion in ``~/.ssh/id_rsa``.
 * Server setup with user ansible.

# Execution

```bash
ansible-playbook playbook.yml
```

Then every time necessary, type the passphrase for the rsa key.
