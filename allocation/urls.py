from django.urls import path
from allocation import views

app_name = 'allocation'
urlpatterns = [
    path("index", views.index.as_view(), name="index"),
    path("signup", views.signup.as_view(user_type="student"), name="student_signup"),
    path("login", views.login.as_view(user_type="student"), name="student_login"),
    path("allocate/<int:user_id>/<slug:room_number>", views.roomAllocate.as_view(), name="room_allocate"),
    path("logout", views.user_logout.as_view(), name="logout"),
]