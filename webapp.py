#! /usr/bin/env python

from flask import Flask, jsonify, request
import ldap
import json
import getConfig
from ldapConn import ldapConn

app = Flask(__name__)

#Endpoint returning every attributes for asked username
@app.route('/api/v1/user/<username>/', methods=['GET'])
def api_getuser(username):
  search_filter = "{}={}".format(getConfig.user_attr,username)
  result = ldapConn(getConfig.user_ou,search_filter)
  for dn,entry in result:
    for key,value in entry.items():
      entry[key] = ",".join(value)
  return jsonify(result[0])


#Endpoint returning all the users
## TODO : Paginate
## Result is to big to be shown in a single request
@app.route('/api/v1/users/all/', methods=['GET'])
def api_getalluser():
  search_filter = "(objectclass=*)"
  result = ldapConn(getConfig.user_ou,search_filter,['uid'])
  for dn,entry in result:
    for key,value in entry.items():
      entry[key] = ",".join(value)
  return jsonify(result[1:])


if __name__ == '__main__':
    app.run(debug=True)
