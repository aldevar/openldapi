#! /usr/bin/env python

from flask import Flask, jsonify, request, abort, make_response
import ldap
import ldap.modlist as modlist
import json
import getConfig
from ldapConn import ldapConn

app = Flask(__name__)

#Endpoint returning every attributes for asked username
@app.route('/api/v1/user/<username>/', methods=['GET'])
def api_getUser(username):
    search_filter = "{}={}".format(getConfig.user_attr,username)
    result = ldapConn(getConfig.user_ou,search_filter)
    for dn,entry in result:
        for key,value in entry.items():
            entry[key] = ",".join(value)
    dictresult = {}
    dictresult[result[0][0]] = result[0][1]
    return jsonify(dictresult)


#Endpoint returning all the users
#Returns paginated results with optional parameters
# limit: number of result to return (default to max)
# offset: index of the first result (default to 1)
# ie /api/V1/users/all/?offset=1&limit=50
# TODO : Add first, next, previous, last page in header
# TODO : Partial Content Header
@app.route('/api/v1/users/all/', methods=['GET'])
def api_getAllUsers():
    search_filter = "(objectclass=*)"
    result = ldapConn(getConfig.user_ou,search_filter,[getConfig.user_attr])
    sorted_result = sorted(result, key=lambda x: x[1])
    dictresult = {}
    #for elem in result[1:]:
    for elem in sorted_result[1:]:
        entry = {}
        dn = elem[0]
        for key,value in elem[1].items():
            entry[key] = value[0]
        dictresult[dn] = entry
    total_range = len(dictresult.keys())
    range_start = request.args.get('offset', 1)
    range_start = int(range_start) - 1
    range_limit = request.args.get('limit', total_range)
    range_end = range_start + int(range_limit)
    # Case Sensitive sorted results
    req_range = {k: dictresult[k] for k in
                 sorted(dictresult.keys())[range_start:range_end]}
                 # this sorted code tries to sort case insensitive
                 # Not working well
                 #sorted(dictresult.keys(), key=lambda y: y.lower())[range_start:range_end]}
    return jsonify(req_range)

#Endpoint returning every attributes for asked group
@app.route('/api/v1/group/<groupname>/', methods=['GET'])
def api_getGroup(groupname):
    search_filter = "{}={}".format(getConfig.group_attr,groupname)
    result = ldapConn(getConfig.group_ou,search_filter)
    for dn,entry in result:
        for key,value in entry.items():
            entry[key] = ",".join(value)
    dictresult = {}
    dictresult[result[0][0]] = result[0][1]
    return jsonify(dictresult)

#Endpoint returning all the groups
# Pagination included
@app.route('/api/v1/groups/all/', methods=['GET'])
def api_getAllGroups():
    search_filter = "(objectclass=*)"
    result = ldapConn(getConfig.group_ou,search_filter,[getConfig.group_attr])
    sorted_result = sorted(result, key=lambda x: x[1])
    dictresult = {}
    for elem in sorted_result:
        print elem
        entry = {}
        if elem[0].startswith("cn"):
            dn = elem[0]
            for key,value in elem[1].items():
                entry[key] = value[0]
            dictresult[dn] = entry
        total_range = len(dictresult.keys())
        range_start = request.args.get('offset', 1)
        range_start = int(range_start) - 1
        range_limit = request.args.get('limit', total_range)
        range_end = range_start + int(range_limit)
    # Case Sensitive sorted results
        req_range = {k: dictresult[k] for k in
                     sorted(dictresult.keys())[range_start:range_end]}
 

    return jsonify(req_range)

#Endoint returning list of users in group
@app.route('/api/v1/members/<groupname>/', methods=['GET'])
def api_getGroupMembers(groupname):
    search_filter = "(objectclass=*)"
    search_ou = "{}={},{}".format(
                           getConfig.group_attr,
                           groupname,
                           getConfig.group_ou)
    result = ldapConn(search_ou,search_filter,[getConfig.member_attr])
    return jsonify(result[0][1])

#Endpoint returning list of groups for a user
@app.route('/api/v1/memberof/<username>/', methods=['GET'])
def api_getMemberOf(username):
    search_filter = "(&({}=*)({}={}))".format(
                                       getConfig.group_attr,
                                       getConfig.member_attr,
                                       username)
    result = ldapConn(getConfig.base_dn,search_filter)
    output = []
    for dn,entry in result:
    #    for key,value in entry.items():
        output.append(entry[getConfig.group_attr][0])
    dictresult = {}
    dictresult["memberof"] = output
    return jsonify(dictresult)

#Endpoint adding a new user
# Request should provide a json dictionnary
# groups key is not mandatory
# {
#   uid: username,
#   givenName: givenname,
#   sn: surname,
#   o: organisation,
#   mail: email@mail.com,
#   telephoneNumber: 0555555555,
#   groups: [group1,group2,group3]
# }
@app.route('/api/v1/add/user/', methods=['POST'])
def api_createuser():
    if not request.json or \
       not 'uid' in request.json or \
       not 'givenName' in request.json or \
       not 'sn' in request.json or \
       not 'o' in request.json or\
       not 'mail' in request.json:
        abort(400)
    attrs = {}
    attrs['uid'] = str(request.json['uid'])
    attrs['givenName'] = str(request.json['givenName'])
    attrs['sn'] = str(request.json['sn'])
    attrs['cn'] = "{} {}".format(attrs['givenName'],attrs['sn'])
    attrs['o'] = str(request.json['o'])
    attrs['mail'] = str(request.json['mail'])
    attrs['telephoneNumber'] = str(request.json['telephoneNumber'])
    if 'personalTitle' in request.json:
        attrs['personalTitle'] = str(request.json['personalTitle'])
    attrs['objectClass'] = ['top',
                   'person',
                   'inetOrgPerson',
                   'pilotPerson',
                   'organizationalPerson',
                   'OpenLDAPperson',
                   'SIBObject']
    dn = 'uid={},{}'.format(attrs['uid'],getConfig.user_ou)
    ldif = modlist.addModlist(attrs)
    try:
        connect = ldap.initialize('ldap://{0}:{1}'.format(getConfig.ldap_server,
                                                    getConfig.ldap_port))
        connect.bind_s(getConfig.ldapcred, getConfig.ldappass)
        result = connect.add_s(dn,ldif)
    except ldap.LDAPError as e:
        connect.unbind_s()
        return make_response(jsonify({"Erreur LDAP": e.message['desc']}), 400)
    return api_getUser(attrs['uid'])




















if __name__ == '__main__':
    app.run(debug=True)
