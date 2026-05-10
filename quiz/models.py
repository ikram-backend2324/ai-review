from django.db import models
from django.contrib.auth.models import User


class Subject(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Subject Name")
    emoji = models.CharField(max_length=10, default="📚", verbose_name="Emoji")
    description = models.TextField(blank=True, verbose_name="Description")
    is_active = models.BooleanField(default=True, verbose_name="Active")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Subject"
        verbose_name_plural = "Subjects"
        ordering = ["name"]

    def __str__(self):
        return f"{self.emoji} {self.name}"


class QuizSession(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("completed", "Completed"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sessions", verbose_name="User"
    )
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, related_name="sessions", verbose_name="Subject"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active", verbose_name="Status")
    started_at = models.DateTimeField(auto_now_add=True, verbose_name="Started At")
    ended_at = models.DateTimeField(null=True, blank=True, verbose_name="Ended At")
    average_score = models.FloatField(null=True, blank=True, verbose_name="Average Score %")
    rating = models.IntegerField(null=True, blank=True, verbose_name="Final Rating (1-5)")

    class Meta:
        verbose_name = "Quiz Session"
        verbose_name_plural = "Quiz Sessions"
        ordering = ["-started_at"]

    def __str__(self):
        return f"{self.user.username} — {self.subject.name} ({self.started_at:%Y-%m-%d %H:%M})"

    def calculate_results(self):
        answers = self.answers.all()
        if not answers:
            return
        scores = [a.score for a in answers]
        self.average_score = sum(scores) / len(scores)
        avg = self.average_score
        if avg >= 90:
            self.rating = 5
        elif avg >= 75:
            self.rating = 4
        elif avg >= 60:
            self.rating = 3
        elif avg >= 40:
            self.rating = 2
        else:
            self.rating = 1
        self.save()


class QuizAnswer(models.Model):
    session = models.ForeignKey(
        QuizSession, on_delete=models.CASCADE, related_name="answers", verbose_name="Session"
    )
    question = models.TextField(verbose_name="Question")
    user_answer = models.TextField(verbose_name="User Answer")
    ai_feedback = models.TextField(verbose_name="AI Feedback")
    score = models.IntegerField(default=0, verbose_name="Score %")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Answered At")

    class Meta:
        verbose_name = "Quiz Answer"
        verbose_name_plural = "Quiz Answers"
        ordering = ["created_at"]

    def __str__(self):
        return f"Q{self.pk}: {self.question[:60]}... [{self.score}%]"
