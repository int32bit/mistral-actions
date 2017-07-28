from mistral.actions.base import Action as action_base
from mistral.actions.openstack import actions as os_actions
from mistral import context


class OpenstackBase(action_base):
    def __init__(self, service):
        self.service = service.strip().title()
        self.client = self._get_client()

    def _get_client(self):
        action_obj = getattr(os_actions, "%sAction" % self.service)()
        # New version use _create_client()
        if hasattr(action_obj, '_create_client'):
            return getattr(action_obj, '_create_client')(context.ctx())
        # Fallback to _get_client()
        return action_obj._get_client()
