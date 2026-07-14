from django.contrib import admin

from .models import KnowledgeCategory, KnowledgeEntry

admin.site.register(KnowledgeCategory)
admin.site.register(KnowledgeEntry)
