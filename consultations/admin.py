from django.contrib import admin

from .models import AIResponseReview, ActivityLog, ConsultationMessage, ConsultationSession, UnansweredQuestion

admin.site.register(ConsultationSession)
admin.site.register(ConsultationMessage)
admin.site.register(UnansweredQuestion)
admin.site.register(AIResponseReview)
admin.site.register(ActivityLog)
