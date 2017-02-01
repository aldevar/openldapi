#!/usr/bin/env python

import ConfigParser

#Get options from config file
config = ConfigParser.ConfigParser()
config.read("/home/devarieuxa/.config/apildap.conf")
def ConfigSectionMap(section):
  dictopt = {}
  options = config.options(section)
  for option in options:
    try:
      dictopt[option] = config.get(section, option)
      if dictopt[option] == -1:
        DebugPrint("skip: {}".format(option))
    except:
      print("exception on {}".format(option))
      dictopt[option] = None
  return dictopt

ldap_server = ConfigSectionMap('LdapServer')['server']
ldap_port = ConfigSectionMap('LdapServer')['port']
base_dn = ConfigSectionMap('LdapConfig')['base']
user_ou = ConfigSectionMap('LdapConfig')['user']
user_attr = ConfigSectionMap('LdapConfig')['user_attr']
ldapcred = ConfigSectionMap('Credentials')['login']
ldappass = ConfigSectionMap('Credentials')['password']
