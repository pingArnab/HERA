
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from . import utils


# Create your views here.
class Sync(APIView):
    def get(self, request, format=None):

        return Response(utils.get_all_static_file_stat())
