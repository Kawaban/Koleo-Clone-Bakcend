from modules.users.models import User


class UserService:
    def get_user_by_sub(self, sub):
        return User.objects.get(sub=sub)

    def create_user(self, sub):
        return User.objects.create(
            email=sub
        )