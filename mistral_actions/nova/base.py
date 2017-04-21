from mistral.actions.base import Action as action_base
from mistral import context

from mistral.utils.openstack import keystone as keystone_utils
from novaclient import client as novaclient


class Base(action_base):
    def __init__(self):
        self.client = self.get_client()

    def get_client(self):
        ctx = context.ctx()

        # LOG.debug("Nova action security context: %s" % ctx)

        keystone_endpoint = keystone_utils.get_keystone_endpoint_v2()
        nova_endpoint = keystone_utils.get_endpoint_for_project('nova')

        client = novaclient.Client(
            2,
            username=None,
            api_key=None,
            endpoint_type='publicURL',
            service_type='compute',
            auth_token=ctx.auth_token,
            tenant_id=ctx.project_id,
            region_name=keystone_endpoint.region,
            auth_url=keystone_endpoint.url, )

        client.client.management_url = keystone_utils.format_url(
            nova_endpoint.url, {'tenant_id': ctx.project_id})

        return client
