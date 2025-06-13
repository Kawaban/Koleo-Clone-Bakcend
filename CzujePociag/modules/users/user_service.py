from modules.users.models import User


class UserService:
    def get_user_by_email(self, email):
        return User.objects.get(email=email)

    def create_user(self, email):
        return User.objects.create(
            email=email
        )