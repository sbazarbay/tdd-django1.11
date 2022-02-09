from accounts.models import Token, User


class PasswordlessAuthenticationBackend(object):
    def authenticate(self, uid):
        try:
            token: Token = Token.objects.get(uid=uid)
            return User.objects.get(email=token.email)
        except (User.DoesNotExist, Token.DoesNotExist) as e:
            if type(e) is User.DoesNotExist:
                return User.objects.create(email=token.email)
            return None

    def get_user(self, email):
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            return None
