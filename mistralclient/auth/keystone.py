# Copyright 2016 - Nokia Networks
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.


def authenticate(mistral_url=None, username=None,
                 api_key=None, project_name=None, auth_url=None,
                 project_id=None, endpoint_type='publicURL',
                 service_type='workflowv2', auth_token=None, user_id=None,
                 cacert=None, insecure=False):

    if project_name and project_id:
        raise RuntimeError(
            'Only project name or project id should be set'
        )

    if username and user_id:
        raise RuntimeError(
            'Only user name or user id should be set'
        )

    auth_args = {
        'username': username,
        'user_id': user_id,
        'password': api_key,
        'auth_url': auth_url,
    }
    api_version = _get_keystone_api_version(auth_url)
    if api_version == 2:
        auth_args.update({
            'tenant_id': project_id,
            'cacert': cacert,
            'endpoint': auth_url,
            'insecure': insecure,
            'token': auth_token,
            'tenant_name': project_name})
    else: 
        auth_args.update({
            'project_domain_name': 'Default',
            'user_domain_name': 'admin_domain',
            'project_name': "admin"})

    keystone = _get_keystone_client(**auth_args)
        
    #token = keystone.auth_token
    user_id = keystone.user_id
    project_id = keystone.project_id

    if not mistral_url:
        mistral_svc_id = keystone.services.find(name='mistral').id
        ep = keystone.endpoints.find(service_id=mistral_svc_id, interface='public')
        print("LY {}".format(ep))
        mistral_url = ep.url
        
#        try:
#            mistral_url = keystone.service_catalog.url_for(
#                service_type=service_type,
#                endpoint_type=endpoint_type
#            )
#        except Exception:
#            mistral_url = None

    token = keystone.auth_token
    print("TOKEN: {}".format(token))
    return mistral_url, token, project_id, user_id


def _get_keystone_api_version(auth_url):
    return 2 if "v2.0" in auth_url else 3
    
def _get_keystone_client(**kwargs):
    api_version = _get_keystone_api_version(kwargs['auth_url'])
    if api_version == 2:
        from keystoneclient.v2_0 import client
        keystone = keystone_client.Client(**kwargs)
    else:
        from keystoneclient.v3 import client as ksclient_v3
        keystone = ksclient_v3.Client(**kwargs)
#        from keystoneauth1.identity import v3
#        from keystoneauth1 import session
#        from keystoneclient.v3 import client
#        auth = v3.Password(**kwargs)
#        sess = session.Session(auth=auth)
#        keystone = client.Client(session=sess)
    return keystone
