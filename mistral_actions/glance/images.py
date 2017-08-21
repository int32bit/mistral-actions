from mistral_actions.exceptions import NotExpectedStatusException
from mistral_actions.openstack import OpenstackBase as base


class AssertStatus(base):
    """Assert a image in special status.

    :param image_id: the uuid of image.
    :param status: (optional)expected status, default 'active'.
    """
    __export__ = True

    def __init__(self, image_id, status='active'):
        super(AssertStatus, self).__init__('glance')
        self.image_id = image_id
        self.status = status

    def run(self):
        image = self.client.images.get(self.image_id)
        if image.status != self.status:
            raise NotExpectedStatusException(
                "image status is '%s', expect '%s'" % (image.status,
                                                       self.status))
        return True


class FilterBy(base):
    """List image filtered by id, name, status, etc.

    :param kwargs: query filters.
    """
    __export__ = True
    SUPPORT_FIELDS = [
        "container_format", "disk_format", "id", "name", "status"
    ]

    def __init__(self, **kwargs):
        super(FilterBy, self).__init__('glance')
        self.filters = self._remove_invalid_fields(kwargs)
        self.kwargs = kwargs

    def _remove_invalid_fields(self, fields):
        result = {}
        for f in fields:
            if f in FilterBy.SUPPORT_FIELDS:
                result[f] = fields[f]
        return result

    def run(self):
        images = list(self.client.images.list(filters=self.filters))
        assert len(images) > 0
        return images
