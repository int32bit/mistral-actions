from mistral.actions.base import Action as action_base
from mistral.actions.openstack import actions as os_actions


class Base(action_base):
    def __init__(self):
        self.client = self.get_client()

    def get_client(self):
        return os_actions.CinderAction()._get_client()
