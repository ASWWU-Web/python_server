# sheldon woodward
# jan 17, 2019

from src.aswwu import exceptions

admin_permission = 'administrator'
elections_permission = 'elections-admin'
notifications_permission = 'notifications-admin'


def permission_or(*perm_args):
    """
    HTTP request decorator to check a user's permissions. The user must have *any* of the specified permissions.
    :param perm_args: Permissions to be checked for.
    :return: Returns the decorated HTTP request function.
    """
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            user = getattr(self, 'current_user')
            # check permission_or
            perm_found = False
            for perm in perm_args:
                if perm in user.roles:
                    perm_found = True
            # check for admin
            if admin_permission in user.roles:
                perm_found = True
            # raise exception if no permission is found
            if not perm_found:
                raise exceptions.Forbidden403Exception('you do not have permission to do this')
            # call method
            return func(self, *args, **kwargs)
        return wrapper
    return decorator


def permission_and(*perm_args):
    """
    HTTP request decorator to check a user's permissions. The user must have *all* of the specified permissions.
    :param perm_args: Permissions to be checked for.
    :return: Returns the decorated HTTP request function.
    """
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            user = getattr(self, 'current_user')
            # check permission_or
            perm_found = True
            for perm in perm_args:
                if perm not in user.roles:
                    perm_found = False
            # check for admin
            if admin_permission in user.roles:
                perm_found = True
            # raise exception if no permission is found
            if not perm_found:
                raise exceptions.Forbidden403Exception('you do not have permission to do this')
            # call method
            return func(self, *args, **kwargs)
        return wrapper
    return decorator
