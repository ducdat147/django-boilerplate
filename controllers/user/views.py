from rest_framework.generics import RetrieveUpdateAPIView

from controllers.user.serializers import MyProfileSerializer


class MyProfileView(RetrieveUpdateAPIView):
    serializer_class = MyProfileSerializer

    def get_object(self):
        if self.request.user.is_anonymous_user:
            raise Exception("Anonymous user does not have profile")
        return self.request.user.userprofile
