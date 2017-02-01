#! /usr/bin/env python

from flask import Flask, jsonify, request
import ldap
import json
import ConfigParser

app = Flask(__name__)

#Get options from config file
config = ConfigParser.ConfigParser()
config.read("apildap.conf")
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
  print("toto")
  return dictopt

ldap_server = ConfigSectionMap('LdapServer')['server']
ldap_port = ConfigSectionMap('LdapServer')['port']
base_dn = ConfigSectionMap('LdapConfig')['base']
user_ou = ConfigSectionMap('LdapConfig')['user']
user_attr = ConfigSectionMap('LdapConfig')['user_attr']
ldapcred = ConfigSectionMap('Credentials')['login']
ldappass = ConfigSectionMap('Credentials')['password']

@app.route('/api/v1/user/<username>/', methods=['GET'])
def api_getuser(username):
  connect = ldap.initialize('ldap://{0}:{1}'.format(ldap_server,ldap_port))
  search_filter = "{}={}".format(user_attr,username)
  try:
    result = connect.search_s(user_ou,ldap.SCOPE_SUBTREE,search_filter)
    connect.unbind_s()
  except ldap.LDAPError as e:
    connect.unbind_s()
    print(e)
  else:
    for dn,entry in result:
      for key,value in entry.items():
        entry[key] = ",".join(value)
    return jsonify("{{{}: {}}}".format(result[0][0],result[0][1]))

@app.route('/api/v1/users/all/', methods=['GET'])
def api_getalluser():
  connect = ldap.initialize('ldap://{0}:{1}'.format(ldap_server,ldap_port))
  connect.bind_s(ldapcred, ldappass)
#  search_filter = "{}=*".format(user_attr)
  search_filter = "(objectclass=*)"
  try:
    result = connect.search_s(user_ou,ldap.SCOPE_SUBTREE,search_filter,['uid', 'mail'])
    print(result)
    connect.unbind_s()
  except ldap.LDAPError as e:
    connect.unbind_s()
    return e
  else:
    for dn,entry in result:
      for key,value in entry.items():
        entry[key] = ",".join(value)
    return jsonify("{{users: {}}}".format(result))

if __name__ == '__main__':
    app.run(debug=True)



