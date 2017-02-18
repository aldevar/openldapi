# openldapi
openLDAPi is a REST API webservice for OpenLDAP

## Run webserver
You have to install 2 pyhton modules:
- python-ldap 
- flask

Edit `apildap.conf` with your openLDAP informations

```
[LdapServer]
# IP Addr of the openLDAP server
server: 127.0.0.1
# Port to access the openLDAP server
port: 389

[LdapConfig]
#Root DN
base: dc=company,dc=com
# Users OU
user: ou=Users,dc=company,dc=com
# Groups OU
group: ou=Groups,dc=company,dc=com
# Attribute for user entries in Users OU
user_attr: uid
# Atribute for groups in Groups OU
group_attr: cn
# Attribute for members of groups
member_attr: memberUid

[Credentials]
login: cn=Manager,dc=company,dc=com
password: MySecretPassword
```

Then, simply execute `./webapp.py` 
You can then access the webserver on localhost, port 5000
ie : http://127.0.0.1:5000/api/v1/users/all/

## REST API
Here are the implemented endpoints
- GET `/api/v1/user/<username>/`
  Return every attr for selected username

- GET `/api/v1/users/all/?offset=1&limit=50`
  Return all the users uid. 
  Support Pagination.  
  offset : index of the first item to return 
  limit : number of item to return
  
- GET `/api/v1/group/<groupname>/`
  Return every attr for select group

- GET `/api/v1/groups/all/?offset=1&limit=50`
  Return all the groups cn.
  Support Pagination. 
  offset : index of the first item to return
  limit : number of item to return
  
- GET `/api/v1/members/<groupname>/` 
  Return list of users belonging to specified group

- GET `/api/v1/memberof/<username>/`
  Return list of groups a user is member of

- POST `/api/v1/add/user/`
  Create a user in the OpenLDAP directory. Accept a json input
```
{
uid: username,
givenName: givenname,
sn: surname,
o: organisation,
mail: email@mail.com,
telephoneNumber: 0555555555,
}
```
