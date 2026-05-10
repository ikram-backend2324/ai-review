import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.contrib import messages

from .models import Subject, QuizSession, QuizAnswer
from .ai_service import generate_question, evaluate_answer


# ─── Auth Views ───────────────────────────────────────────────────────────────

def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("home")
        messages.error(request, "Invalid username or password.")
    return render(request, "quiz/login.html")


def register_view(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        password2 = request.POST.get("password2", "")
        if not username or not password:
            messages.error(request, "Username and password are required.")
        elif password != password2:
            messages.error(request, "Passwords do not match.")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
        else:
            user = User.objects.create_user(username=username, password=password)
            login(request, user)
            return redirect("home")
    return render(request, "quiz/register.html")


def logout_view(request):
    logout(request)
    return redirect("login")


# ─── Main Views ───────────────────────────────────────────────────────────────

@login_required
def home_view(request):
    subjects = Subject.objects.filter(is_active=True)
    recent_sessions = QuizSession.objects.filter(
        user=request.user, status="completed"
    ).order_by("-ended_at")[:5]
    total_sessions = QuizSession.objects.filter(user=request.user, status="completed").count()
    best_rating = QuizSession.objects.filter(
        user=request.user, status="completed", rating__isnull=False
    ).order_by("-rating").values_list("rating", flat=True).first()

    context = {
        "subjects": subjects,
        "recent_sessions": recent_sessions,
        "total_sessions": total_sessions,
        "best_rating": best_rating,
    }
    return render(request, "quiz/home.html", context)


@login_required
def quiz_view(request, subject_id):
    subject = get_object_or_404(Subject, pk=subject_id, is_active=True)
    # End any active session for this user
    QuizSession.objects.filter(user=request.user, status="active").update(status="completed")
    session = QuizSession.objects.create(user=request.user, subject=subject)
    return render(request, "quiz/quiz.html", {"subject": subject, "session_id": session.pk})


@login_required
def results_view(request, session_id):
    session = get_object_or_404(QuizSession, pk=session_id, user=request.user)
    answers = session.answers.all().order_by("created_at")
    return render(request, "quiz/results.html", {"session": session, "answers": answers})


@login_required
def history_view(request):
    sessions = QuizSession.objects.filter(
        user=request.user, status="completed"
    ).order_by("-started_at")
    return render(request, "quiz/history.html", {"sessions": sessions})


# ─── AJAX / API Views ─────────────────────────────────────────────────────────

@login_required
@require_POST
def api_get_question(request):
    data = json.loads(request.body)
    session_id = data.get("session_id")
    session = get_object_or_404(QuizSession, pk=session_id, user=request.user, status="active")
    question = generate_question(session.subject.name)
    # Store the current question in session (Django session, not model)
    request.session[f"current_question_{session_id}"] = question
    return JsonResponse({"question": question})


@login_required
@require_POST
def api_submit_answer(request):
    data = json.loads(request.body)
    session_id = data.get("session_id")
    user_answer = data.get("answer", "").strip()

    session = get_object_or_404(QuizSession, pk=session_id, user=request.user, status="active")
    question = request.session.get(f"current_question_{session_id}", "")

    if not question:
        return JsonResponse({"error": "No active question."}, status=400)
    if not user_answer:
        return JsonResponse({"error": "Answer cannot be empty."}, status=400)

    feedback, score = evaluate_answer(question, user_answer)

    QuizAnswer.objects.create(
        session=session,
        question=question,
        user_answer=user_answer,
        ai_feedback=feedback,
        score=score,
    )

    answer_count = session.answers.count()
    return JsonResponse({
        "feedback": feedback,
        "score": score,
        "answer_count": answer_count,
    })


@login_required
@require_POST
def api_end_session(request):
    data = json.loads(request.body)
    session_id = data.get("session_id")
    session = get_object_or_404(QuizSession, pk=session_id, user=request.user, status="active")
    session.status = "completed"
    session.ended_at = timezone.now()
    session.save()
    session.calculate_results()
    return JsonResponse({"redirect": f"/results/{session.pk}/"})
