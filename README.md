Role Name
=========

Create and configure Firefox roles.

Requirements
------------

This role will try to install the following prerequisite packages:

- `jmespath` package (for parsing json):
  `python3-jmespath` in apt, or `py-jmespath` in Macports.
- `py-certifi` port in Macports.

Role Variables
--------------

`profile`
: string, optional. By default, this role will look up the name of the
default Firefox role. If provided, it should be the short name of the
profile as given in [about:profiles](about:profiles).

`addons`
: list of strings, optional. This is the list of
[addons](about:addons) to install. Use each addon's slug, not its
name. The easiest way to get the slug is from the URL of the Mozilla
page: if the URL is

    https://addons.mozilla.org/en-US/firefox/addon/privacy-badger17/

then the slug is `privacy-badger17`.

Themes are addons just like extensions. You can list them all in the
`addons` variable.

`prefs`
: dictionary, optional. This is the set of preferences to set. These can
be found in [about:config](about:config).

**Caveats**: For boolean values, don't use YAML
`true`/`false`/`yes`/`no`: the value must be a string, e.g.:

    network.proxy.share_proxy_settings: "true"

Furthermore, when the value is a string, the quotation marks _must_
also be quoted, e.g.:

    network.proxy.http: '"localhost"'

To delete a preference entirely, and effetively reset its value to
Firefox's default, set it to `null`:

    network.proxy.type: null

`security_devices`: list of dictionaries, optional. In
[Security > Privacy & Security](about:preferences#privacy), you can
set up Security Devices like hardware keys. This variable allows you
to do so in Ansible, e.g.:

    security_devices:
      - name: OpenSC PKCS#11 Module
        lib: /usr/local/lib/opensc-pkcs11.so

`firefox_cmd`
: string, optional. The command to execute to run
Firefox. Default: `firefox`.

`firefox_dir`
: string, optional. The directory containing the root of Firefox's
preferences (the directory containing `profiles.ini`). Default:
`$HOME/.mozilla/firefox` on Linux. On a Mac, set this to
`$HOME/Library/Application Support/Firefox`.

`firefox_profile_path`
: string, optional. The path to the `profiles.ini` file to use.
Default: `{{ firefox_dir }}/profiles.ini`.

`firefox_owner`, `firefox_group`
: strings, optional. The user and group who should own `firefox_dir`.
Default to `ansible_user_id` and `ansible_effective_group_id`.

Example Playbook
----------------

Including an example of how to use your role (for instance, with variables passed in as parameters) is always nice for users too:

    - name: Customize default profile
      hosts: desktops
      roles:
        # No 'profile' specified: use the default profile
        - role: firefox
          addons:
            - password-manager

    - name: More complete customization
      hosts: desktops
	  roles:
        - role: firefox
          profile: work
          addons:
            - switchyomega
            - password-manager
            # Theme:
            - solarize-fox
          security_devices:
            - name: 2FA Dongle
              lib: /usr/local/lib/opensc-pkcs15.so
          prefs:
            extensions.privatebrowsing.notification: "true"
            # Note the doubly-nested quotes. Necessary for string values.
            network.proxy.ftp: '"localhost"'
            network.proxy.ftp_port: 12345
Bugs
----
- It is not currently possible to delete a profile using this role. Mozilla does not document a way to delete a profile without going through the Profile Manager.

License
-------

BSD

Author Information
------------------

Andrew Arensburger, 2020-2022.
