#!/usr/bin/python3

# from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
module: profile
short_description: Read Firefox's list of profiles.
notes:
  -
options:
  user:
    description:
      - User whose profiles.ini file to parse.
      - Incompatible with C(path).
    type: str
    default: ansible_user
  path:
    description:
      - Absolute path to the profiles.ini file to parse.
      - Incompatible with C(user).
    type: str
'''

EXAMPLES = r'''
- name: "Look up the default user's Firefox profiles"
  profile:
  register: profiles

- name: "Look up bob's Firefox profiles"
  profile:
    user: bob
  register: bob_profiles

- name: "Look up a specific profile file"
  profile:
    path: "/path/to/profiles.ini"
  register: specific_profiles
'''

RETURN = r'''
profiles:
  description: Dict of profiles in C(profiles.ini), indexed by their profile name.
  returned: always
  type: dict
sections:
  description: Dict of sections in C(profiles.ini) that aren't profiles, indexed by section name.
  returned: always
  type: dict
default_profile:
  description: Name of the default profile, if any.
  returned: success, in some cases
  type: str
'''

import os
import platform
# configparser: read .ini files.
import configparser
from ansible.module_utils.basic import AnsibleModule


def run_module():
    """Run the 'profile' module."""
    module = AnsibleModule(
        argument_spec=dict(
            # User: read this user's profiles.ini file.
            user=dict(type='str', required=False, default=None),
            # Path: read this specific profiles.ini file.
            # Overrides user.
            path=dict(type='str', required=False, default=None),
        ),
        mutually_exclusive=[
            ('user', 'path'),
        ],
        supports_check_mode=True,
    )

    retval = dict(
        # XXX - Should this ever show up as changed? Ideally when the
        # list of profiles changes. How easy is that to test?
        changed=False,
        profiles={},            # Dict of browser profiles
        sections={},            # Dict of other sections in the file
        default_profile=None,
    )

    user = module.params['user']        # User whose profiles we're reading
    path = module.params['path']        # Path to profile file

    # Figure out which path to open.
    #
    # On most Unix/Linux systems, it's ~/.mozilla/firefox/profiles.ini .
    #
    # On MacOS, it's ~/Library/Application
    # Support/Firefox/profiles.ini (and the profiles themselves are
    # under ~/Library/Application Support/Firefox/Profiles/).
    #
    # On Windows, it's %APPDATA%\Mozilla\Firefox\profiles.ini .
    if path is None:
        # In any case, the profile file will be in someone's home directory.
        if user is None:
            home = "~"
        else:
            home = f"~{user}"
        home = os.path.expanduser(home)

        system = platform.system()
        if system == "Darwin":
            path = f"{home}/Library/Application Support/Firefox/profiles.ini"
        else:
            path = f"{home}/.mozilla/firefox/profiles.ini"

    if not os.path.exists(path):
        # XXX - Behave differently in check mode and real mode?
        # Shouldn't fail in check mode, even if the file doesn't exist.
        #
        # In normal mode, maybe should fail: if the caller doesn't
        # want it to , they can always use 'failed_when: no'.
        retval['profiles'] = {}
        module.exit_json(**retval)

    # Read profiles.ini and parse as an ini file.
    ini = configparser.ConfigParser()
    try:
        with open(path) as inifile:
            ini.read_file(inifile)
    except FileNotFoundError as e:
        module.fail_json(msg=f"File not found error reading {profiles_path}: {e}")

    # Rewrite config to be more friendly.
    #
    # Unfortunately, 'profiles.ini' isn't organized in a friendly
    # way: it's a series of sections of the form
    #     [Profile1]
    #     Name=Surfing
    #     IsRelative=1
    #     Path=apaphDab.Surfing
    #     Default=1
    #
    #     [Profile0]
    #     Name=Projects
    #     IsRelative=1
    #     Path=Kijnekfa.Projects
    # So let's walk the list and parse it into a dict.
    for section_name in ini.sections():
        section = {}

        # Collect all the key-value pairs in this section.
        for opt_name in ini.options(section_name):
            value = ini.get(section_name, opt_name)
            section[opt_name] = value

        # Check the section name. It's either "ProfileNNN" (so it's a
        # profile) or some other section.
        if section_name.startswith("Profile"):
            # This is a profile name. It should have a name, and should
            # be stored under this name.
            if 'name' not in section:
                # XXX - Something's wrong
                module.fail_json(msg=f"Missing Name parameter in section {section_name}")

            retval['profiles'][section['name']] = section

            # If this is the default section, remember this.

            # XXX - On MacOS, no section has "Default=1". Rather,
            # section "InstallNNNNN" has "Default=Profiles/<path>"
            # which corresponds to the "Path=" entry of one of the
            # "Profile" sections.
            # Ditto on cantaloupe; and vimes has both.
            #
            # Only the first behavior is described at
            # http://kb.mozillazine.org/Profiles.ini_file.
            # (That hasn't been updated since 2017.)
            #
            # See also
            # https://support.mozilla.org/en-US/kb/understanding-depth-profile-installation
            if 'default' in section and section['default'] == "1":
                retval['default_profile'] = section['name']
        else:
            # This is not a Profile section. Save it under its section
            # name.
            retval['sections'][section_name] = section

    if module.check_mode:
        module.exit_json(**retval)

    # XXX - Not sure what else there is to do in non-check mode.

    module.exit_json(**retval)


def main():
    # Why?
    """Just a wrapper around run_module()."""
    run_module()


# Main
if __name__ == "__main__":
    main()
