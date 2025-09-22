from rest_framework.generics import RetrieveUpdateAPIView

from controllers.user.serializers import MyProfileSerializer


class MyProfileView(RetrieveUpdateAPIView):
    serializer_class = MyProfileSerializer

    def get_object(self):
        return self.request.user
