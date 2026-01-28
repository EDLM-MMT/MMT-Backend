from rest_framework import permissions

APP_LABELS_MODEL_NAME = "%(app_label)s.view_%(model_name)s"


class CustomObjectPermissions(permissions.DjangoObjectPermissions):
    """
    Similar to `DjangoObjectPermissions`, but adding 'view' permissions.
    """
    perms_map = {
        'GET': [APP_LABELS_MODEL_NAME],
        'OPTIONS': [APP_LABELS_MODEL_NAME],
        'HEAD': [APP_LABELS_MODEL_NAME],
        'POST': ['%(app_label)s.add_%(model_name)s'],
        'PUT': ['%(app_label)s.change_%(model_name)s'],
        'PATCH': ['%(app_label)s.change_%(model_name)s'],
        'DELETE': ['%(app_label)s.delete_%(model_name)s'],
    }
