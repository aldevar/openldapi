#! /usr/bin/env python

from flask import Flask, jsonify, request
import ldap
import json
import getConfig

app = Flask(__name__)

#Endpoint returning every attributes for a given user
@app.route('/api/v1/user/<username>/', methods=['GET'])
def api_getuser(username):
  connect = ldap.initialize('ldap://{0}:{1}'.format(getConfig.ldap_server,getConfig.ldap_port))
  search_filter = "{}={}".format(getConfig.user_attr,username)
  try:
    result = connect.search_s(getConfig.user_ou,ldap.SCOPE_SUBTREE,search_filter)
    connect.unbind_s()
  except ldap.LDAPError as e:
    connect.unbind_s()
    print(e)
  else:
    for dn,entry in result:
      for key,value in entry.items():
        entry[key] = ",".join(value)
#    return jsonify(result[0][0],result[0][1])
    return jsonify(result[0])


#Endpoint returning all the users
@app.route('/api/v1/users/all/', methods=['GET'])
def api_getalluser():
  connect = ldap.initialize('ldap://{0}:{1}'.format(getConfig.ldap_server,getConfig.ldap_port))
  connect.bind_s(getConfig.ldapcred, getConfig.ldappass)
  search_filter = "(objectclass=*)"
  try:
    result = connect.search_s(getConfig.user_ou,ldap.SCOPE_SUBTREE,search_filter,['uid'])
    connect.unbind_s()
  except ldap.LDAPError as e:
    connect.unbind_s()
    return e
  else:
    for dn,entry in result:
      for key,value in entry.items():
        entry[key] = ",".join(value)
    #return jsonify("{{users: {}}}".format(result))
    return jsonify(result[1:])

if __name__ == '__main__':
    app.run(debug=True)



