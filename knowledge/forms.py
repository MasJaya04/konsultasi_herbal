from django import forms

from catalog.models import Product

from .models import KnowledgeCategory, KnowledgeEntry


class KnowledgeImportForm(forms.Form):
    csv_file = forms.FileField(
        label="File impor",
        widget=forms.ClearableFileInput(
            attrs={
                "class": "w-full rounded-xl border border-slate-200 px-4 py-3 text-sm file:mr-4 file:rounded-lg file:border-0 file:bg-slate-900 file:px-4 file:py-2 file:text-white",
                "accept": ".csv,.xlsx,text/csv,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            }
        )
    )


class KnowledgeCategoryForm(forms.ModelForm):
    class Meta:
        model = KnowledgeCategory
        fields = ("name", "description")
        labels = {
            "name": "Nama",
            "description": "Deskripsi",
        }
        widgets = {
            "name": forms.TextInput(attrs={"class": "w-full rounded-lg border px-3 py-2"}),
            "description": forms.Textarea(attrs={"class": "w-full rounded-lg border px-3 py-2", "rows": 3}),
        }


class KnowledgeEntryForm(forms.ModelForm):
    class Meta:
        model = KnowledgeEntry
        fields = ("product", "category", "title", "question", "answer", "source_type", "keywords", "status", "quality_status", "review_note")
        labels = {
            "product": "Produk",
            "category": "Kategori",
            "title": "Judul",
            "question": "Pertanyaan",
            "answer": "Jawaban",
            "source_type": "Tipe sumber",
            "keywords": "Kata kunci",
            "status": "Status",
            "quality_status": "Kualitas",
            "review_note": "Catatan tinjauan",
        }
        widgets = {
            "product": forms.Select(attrs={"class": "w-full rounded-lg border px-3 py-2"}),
            "category": forms.Select(attrs={"class": "w-full rounded-lg border px-3 py-2"}),
            "title": forms.TextInput(attrs={"class": "w-full rounded-lg border px-3 py-2"}),
            "question": forms.Textarea(attrs={"class": "w-full rounded-lg border px-3 py-2", "rows": 3}),
            "answer": forms.Textarea(attrs={"class": "w-full rounded-lg border px-3 py-2", "rows": 6}),
            "source_type": forms.Select(attrs={"class": "w-full rounded-lg border px-3 py-2"}),
            "keywords": forms.TextInput(attrs={"class": "w-full rounded-lg border px-3 py-2"}),
            "status": forms.Select(attrs={"class": "w-full rounded-lg border px-3 py-2"}),
            "quality_status": forms.Select(attrs={"class": "w-full rounded-lg border px-3 py-2"}),
            "review_note": forms.Textarea(attrs={"class": "w-full rounded-lg border px-3 py-2", "rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["product"].queryset = Product.objects.filter(is_active=True).order_by("name")
        self.fields["product"].required = True
