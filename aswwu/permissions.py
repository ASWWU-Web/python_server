# sheldon woodward
# jan 17, 2019

from aswwu import exceptions


election_permission = 'elections-admin'


def permission(permission_name):
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            user = getattr(self, 'current_user')
            # check permission
            if permission_name not in user.roles and 'administrator' not in user.roles:
                raise exceptions.Forbidden403Exception('you do not have permission to do this')
            # call method
            return func(self, *args, **kwargs)
        return wrapper
    return decorator
