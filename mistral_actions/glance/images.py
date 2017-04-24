from mistral_actions.glance.base import Base


class AssertStatus(Base):
    """Assert a image in special status.

    :param image_id: the uuid of image.
    :param status: (optional)expected status, default 'active'.
    """
    __export__ = True

    def __init__(self, image_id, status='active'):
        super(AssertStatus, self).__init__()
        self.image_id = image_id
        self.status = status

    def run(self):
        image = self.client.images.get(self.image_id)
        assert (image.status == self.status)
        return True
