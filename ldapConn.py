#!/usr/bin/env Python

import ldap
import getConfig

def ldapConn(base_ou,search_filter,attr=None):
  connect = ldap.initialize('ldap://{0}:{1}'.format(getConfig.ldap_server,getConfig.ldap_port)
)
  connect.bind_s(getConfig.ldapcred, getConfig.ldappass)
#  search_filter = "(objectclass=*)"
  try:
    if attr is None:
      result = connect.search_s(base_ou,ldap.SCOPE_SUBTREE,search_filter)
    else:
      result = connect.search_s(base_ou,ldap.SCOPE_SUBTREE,search_filter,attr)
    connect.unbind_s()
  except ldap.LDAPError as e:
    connect.unbind_s()
    return e
  else:
    return result
