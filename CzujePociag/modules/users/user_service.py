from modules.authentication.models import CustomUser


class UserService:
    def get_user_by_email(self, email):
        return CustomUser.objects.get(email=email)

    def create_user(self, email):
        return CustomUser.objects.create(
            email=email
        )