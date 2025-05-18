from django.shortcuts import render
from rest_framework.views import APIView, status
from rest_framework.response import Response

# Create your views here.


class UploadVector(APIView):
    def post(self, req):
        return Response({"message": "Vector Uploaded"}, status=201)


class RetrieveVectors(APIView):
    def get(self, req):
        return Response({"message": "Vector Uploaded"}, status=201)


class GetContent(APIView):
    def get(self, req):
        return Response({"message": "Vector Uploaded"}, status=201)
