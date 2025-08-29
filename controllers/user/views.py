# -*- coding: utf-8 -*-
from rest_framework.generics import RetrieveAPIView

from controllers.user.serializers import MyProfileSerializer


class MyProfileView(RetrieveAPIView):
    serializer_class = MyProfileSerializer

    def get_object(self):
        return self.request.user
