from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from sales.models import DoctorDetail
import json

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

class DoctorDetail(View) :
    def get(self, request) :
        doctors = DoctorDetail.objects.using('sales').all()
        doctor_list = list(doctors.values('id', 'rayon', 'info'))
        return JsonResponse({'doctors' : doctor_list})