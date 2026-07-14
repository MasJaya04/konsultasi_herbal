from django.urls import path

from .views import (
    KnowledgeCategoryCreateView,
    KnowledgeCategoryDeleteView,
    KnowledgeCategoryListView,
    KnowledgeCategoryUpdateView,
    KnowledgeEntryCreateView,
    KnowledgeEntryDeleteView,
    KnowledgeEntryExportView,
    KnowledgeEntryListView,
    KnowledgeQualityMonitorView,
    KnowledgeEntryUpdateView,
)

app_name = "knowledge"

urlpatterns = [
    path("categories/", KnowledgeCategoryListView.as_view(), name="category_list"),
    path("categories/create/", KnowledgeCategoryCreateView.as_view(), name="category_create"),
    path("categories/<int:pk>/edit/", KnowledgeCategoryUpdateView.as_view(), name="category_update"),
    path("categories/<int:pk>/delete/", KnowledgeCategoryDeleteView.as_view(), name="category_delete"),
    path("", KnowledgeEntryListView.as_view(), name="entry_list"),
    path("quality-monitor/", KnowledgeQualityMonitorView.as_view(), name="quality_monitor"),
    path("export/", KnowledgeEntryExportView.as_view(), name="entry_export"),
    path("create/", KnowledgeEntryCreateView.as_view(), name="entry_create"),
    path("<int:pk>/edit/", KnowledgeEntryUpdateView.as_view(), name="entry_update"),
    path("<int:pk>/delete/", KnowledgeEntryDeleteView.as_view(), name="entry_delete"),
]
