from django.contrib import admin
from django.utils.html import format_html
from .models import Subject, QuizSession, QuizAnswer


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("emoji", "name", "is_active", "session_count", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name",)
    list_editable = ("is_active",)

    def session_count(self, obj):
        count = obj.sessions.count()
        return format_html('<span style="font-weight:bold">{}</span>', count)
    session_count.short_description = "Sessions"


class QuizAnswerInline(admin.TabularInline):
    model = QuizAnswer
    extra = 0
    readonly_fields = ("question", "user_answer", "ai_feedback", "score", "created_at")
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(QuizSession)
class QuizSessionAdmin(admin.ModelAdmin):
    list_display = (
        "user", "subject", "status", "answer_count",
        "average_score_display", "rating_stars", "started_at"
    )
    list_filter = ("status", "subject", "rating")
    search_fields = ("user__username", "subject__name")
    readonly_fields = ("started_at", "ended_at", "average_score", "rating")
    inlines = [QuizAnswerInline]

    def answer_count(self, obj):
        return obj.answers.count()
    answer_count.short_description = "Answers"

    def average_score_display(self, obj):
        if obj.average_score is None:
            return "—"
        color = "#28a745" if obj.average_score >= 75 else "#ffc107" if obj.average_score >= 50 else "#dc3545"
        return format_html(
            '<span style="color:{}; font-weight:bold">{:.1f}%</span>',
            color, obj.average_score
        )
    average_score_display.short_description = "Avg Score"

    def rating_stars(self, obj):
        if obj.rating is None:
            return "—"
        stars = "⭐" * obj.rating
        return format_html('<span title="{}/5">{}</span>', obj.rating, stars)
    rating_stars.short_description = "Rating"


@admin.register(QuizAnswer)
class QuizAnswerAdmin(admin.ModelAdmin):
    list_display = ("session", "short_question", "score", "created_at")
    list_filter = ("score", "session__subject")
    search_fields = ("question", "user_answer")
    readonly_fields = ("session", "question", "user_answer", "ai_feedback", "score", "created_at")

    def short_question(self, obj):
        return obj.question[:80] + "..." if len(obj.question) > 80 else obj.question
    short_question.short_description = "Question"

    def has_add_permission(self, request):
        return False
