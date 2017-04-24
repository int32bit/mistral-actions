from glanceclient.v2 import client as glanceclient
from mistral.actions.base import Action as action_base
from mistral import context
from mistral.utils.openstack import keystone as keystone_utils


class Base(action_base):
    def __init__(self):
        self.client = self.get_client()

    def get_client(self):
        ctx = context.ctx()
        glance_endpoint = keystone_utils.get_endpoint_for_project('glance')
        return glanceclient.Client(
            glance_endpoint.url,
            region_name=glance_endpoint.region,
            token=ctx.auth_token
        )
