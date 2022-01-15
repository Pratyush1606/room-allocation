from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework import status
from django.contrib.auth.hashers import make_password
from rest_framework.renderers import TemplateHTMLRenderer
from django.http import JsonResponse
from django.contrib.auth import logout
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render, redirect

from .models import User, Student, Room
from .serializers import UserSerializer, StudentSerializer, RoomSerializer

class index(APIView):
    renderer_classes = [TemplateHTMLRenderer]

    def get(self, request):
        return Response(template_name="index.html", status=status.HTTP_200_OK)
        
class signup(APIView):
    user_type = "student"
    renderer_classes = [TemplateHTMLRenderer]

    def get(self, request):
        if(self.user_type=="student"):
            return Response(template_name="student_signup.html", status=status.HTTP_200_OK)

    def post(self, request):
        if(self.user_type=="student"):
            data = {
                "email": request.POST.get("email"),
                "first_name": request.POST.get("first_name"),
                "last_name": request.POST.get("last_name"),
                "roll_number": request.POST.get("roll"),
                "phone_number": request.POST.get("phone"),
                "password": make_password(request.POST.get("password"))
            }
            serializer = UserSerializer(data=data)
            if(serializer.is_valid()):
                user = serializer.save()
                student_data = {
                    "user": user.user_id,
                    "roll_number": data["roll_number"],
                    "phone_number": data["phone_number"]
                }
                serializer = StudentSerializer(data=student_data)
                if(serializer.is_valid()):
                    serializer.save()
                else:
                    user.delete()
                    return Response({"error":"Invalid User Data"}, template_name="error_page.html", status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"error":"Invalid User Data"}, template_name="error_page.html", status=status.HTTP_400_BAD_REQUEST)
            return Response(template_name="student_login.html", status=status.HTTP_201_CREATED)

class login(APIView):
    user_type = "student"
    renderer_classes = [TemplateHTMLRenderer]

    def get(self, request):
        if(self.user_type=="student"):
            return Response(template_name="student_login.html", status=status.HTTP_200_OK)
    
    def post(self, request):
        user = authenticate(email=request.POST.get("email"), password=request.POST.get("password"))
        user_check = self.check_user(user)
        if(not user_check[0]):
            return Response({"error":user_check[1]}, template_name="error_page.html", status=status.HTTP_400_BAD_REQUEST)
        if(self.user_type=="student"):
            # Checking Student
            try:
                student = user.student
            except Exception as e:
                return Response({"error":"Not a valid Student."}, template_name="error_page.html", status=status.HTTP_400_BAD_REQUEST)
            user_serializer_data = UserSerializer(user).data
            stud_serializer_data = StudentSerializer(student).data
            student_data = {
                "user_id": user_serializer_data.get("user_id"),
                "email": user_serializer_data.get("email"),
                "first_name": user_serializer_data.get("first_name"),
                "last_name": user_serializer_data.get("last_name"),
                "roll_number": stud_serializer_data.get("roll_number"),
                "phone_number": stud_serializer_data.get("phone_number"),
                "is_allotted": stud_serializer_data.get("is_allotted"),
            }
            rooms = Room.objects.all()
            rooms_data = []
            for room in rooms:
                room_data = {
                    "room_number": room.room_number,
                    "roll_number": room.roll_number,
                }
                if(room.roll_number!="0"):
                    # Room is allotted
                    curr_student = Student.objects.filter(roll_number=room.roll_number)
                    if(curr_student.exists() and len(curr_student)==1):
                        curr_stud_serializer_data = StudentSerializer(curr_student[0]).data
                        curr_user_serializer_data = UserSerializer(curr_student[0].user).data
                        curr_student_data = {
                            "user_id": curr_user_serializer_data.get("user_id"),
                            "email": curr_user_serializer_data.get("email"),
                            "first_name": curr_user_serializer_data.get("first_name"),
                            "last_name": curr_user_serializer_data.get("last_name"),
                            "roll_number": curr_stud_serializer_data.get("roll_number"),
                            "phone_number": curr_stud_serializer_data.get("phone_number"),
                            "is_allotted": curr_stud_serializer_data.get("is_allotted"),
                        }
                        room_data.update(curr_student_data)
                rooms_data.append(room_data)
        return Response(data={"student": student_data, "rooms": rooms_data}, template_name="homepage.html", status=status.HTTP_200_OK)
    
    def check_user(self, user):
        if(not user):
            return False, "User is not authenticated."
        if(not user.is_active):
            return False, "User is not active."
        return True, "Valid User."
        
class roomAllocate(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    
    def post(self, request, user_id, room_number):
        try:
            user = User.objects.get(user_id=user_id)
            student = user.student
            room = Room.objects.get(room_number=room_number)
            if(room.roll_number=="0"):
                room.roll_number = student.roll_number
                room.save()
                student.is_allotted = True
                student.save()
                return JsonResponse(data={"success": True})
            return JsonResponse(data={"success": False})
        except Exception as e:
            return JsonResponse(data={"success": False})

class user_logout(APIView):

    def get(self, request):
        logout(request)
        return redirect("allocation:index")
