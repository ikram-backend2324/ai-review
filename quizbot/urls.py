from django.contrib import admin
from django.urls import path, include

admin.site.site_header = "QuizBot Control Panel"
admin.site.site_title = "QuizBot Admin"
admin.site.index_title = "Dashboard"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("quiz.urls")),
]
