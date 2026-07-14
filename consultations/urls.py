from django.urls import path

from .views import (
    AIResponseReviewCreateView,
    AIResponseReviewDeleteView,
    AIResponseReviewExportView,
    AIResponseReviewListView,
    AIResponseReviewUpdateView,
    ActivityLogListView,
    ConsultationChatView,
    ConsultationHistoryView,
    ConsultationSessionDeleteView,
    ConsultationSessionDetailView,
    UnansweredQuestionDeleteView,
    UnansweredQuestionExportView,
    UnansweredQuestionListView,
    UnansweredQuestionRetestView,
    UnansweredQuestionUpdateView,
)

app_name = "consultations"

urlpatterns = [
    path("chat/", ConsultationChatView.as_view(), name="chat"),
    path("chat/<int:pk>/delete/", ConsultationSessionDeleteView.as_view(), name="session_delete"),
    path("history/", ConsultationHistoryView.as_view(), name="history"),
    path("history/<int:pk>/", ConsultationSessionDetailView.as_view(), name="session_detail"),
    path("unanswered/", UnansweredQuestionListView.as_view(), name="unanswered_list"),
    path("unanswered/export/", UnansweredQuestionExportView.as_view(), name="unanswered_export"),
    path("unanswered/<int:pk>/", UnansweredQuestionUpdateView.as_view(), name="unanswered_update"),
    path("unanswered/<int:pk>/delete/", UnansweredQuestionDeleteView.as_view(), name="unanswered_delete"),
    path("unanswered/<int:pk>/retest/", UnansweredQuestionRetestView.as_view(), name="unanswered_retest"),
    path("activity-logs/", ActivityLogListView.as_view(), name="activity_log_list"),
    path("reviews/", AIResponseReviewListView.as_view(), name="review_list"),
    path("reviews/export/", AIResponseReviewExportView.as_view(), name="review_export"),
    path("reviews/<int:message_id>/create/", AIResponseReviewCreateView.as_view(), name="review_create"),
    path("reviews/<int:pk>/edit/", AIResponseReviewUpdateView.as_view(), name="review_update"),
    path("reviews/<int:pk>/delete/", AIResponseReviewDeleteView.as_view(), name="review_delete"),
]
