from django.urls import path
from . import views

urlpatterns = [
    path("", views.home_view, name="home"),
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
    path("quiz/<int:subject_id>/", views.quiz_view, name="quiz"),
    path("results/<int:session_id>/", views.results_view, name="results"),
    path("history/", views.history_view, name="history"),
    # AJAX
    path("api/question/", views.api_get_question, name="api_get_question"),
    path("api/answer/", views.api_submit_answer, name="api_submit_answer"),
    path("api/end/", views.api_end_session, name="api_end_session"),
]
