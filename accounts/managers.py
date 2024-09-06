from django.db import models


class CustomUserManager(models.Manager):
    def get_by_natural_key(self, username):
        return self.get(username=username)

    def specific_to_user(self, user, include_all=True):
        # Staff have the option to see all users, while everyone else only see users who have not been soft deleted.
        if user.is_staff and include_all:
            return self.all()

        return self.filter(soft_deleted=False)
