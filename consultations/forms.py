from django import forms

from catalog.models import Product
from knowledge.models import KnowledgeEntry

from .models import AIResponseReview, UnansweredQuestion


class ConsultationPromptForm(forms.Form):
    product = forms.ModelChoiceField(
        label="Produk aktif",
        required=False,
        empty_label="Pilih produk aktif (opsional)",
        queryset=Product.objects.none(),
        widget=forms.Select(
            attrs={
                "class": "w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-700 focus:border-blue-300 focus:bg-white focus:outline-none",
            }
        ),
    )
    prompt = forms.CharField(
        label="Pertanyaan",
        widget=forms.Textarea(
            attrs={
                "class": "min-h-[64px] max-h-[220px] w-full overflow-y-auto resize-none rounded-2xl border border-slate-200 px-5 py-4 pr-20 text-base text-slate-800 placeholder:text-slate-400 focus:border-blue-300 focus:outline-none",
                "rows": 1,
                "placeholder": "Tulis pertanyaan konsultasi herbal Anda...",
            }
        )
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["product"].queryset = Product.objects.filter(is_active=True).order_by("name")


class AIResponseReviewForm(forms.ModelForm):
    class Meta:
        model = AIResponseReview
        fields = ("verdict", "note")
        labels = {
            "verdict": "Keputusan evaluasi",
            "note": "Catatan",
        }
        widgets = {
            "verdict": forms.Select(attrs={"class": "w-full rounded-lg border px-3 py-2"}),
            "note": forms.Textarea(attrs={"class": "w-full rounded-lg border px-3 py-2", "rows": 3}),
        }


class UnansweredQuestionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        product = kwargs.pop("product", None)
        super().__init__(*args, **kwargs)
        queryset = KnowledgeEntry.objects.select_related("product").order_by("title")
        if product:
            queryset = queryset.filter(product=product)
        else:
            queryset = queryset.none()
        self.fields["resolved_entry"].queryset = queryset

    class Meta:
        model = UnansweredQuestion
        fields = ("status", "resolved_entry")
        labels = {
            "status": "Status",
            "resolved_entry": "Entri penyelesaian",
        }
        widgets = {
            "status": forms.Select(attrs={"class": "w-full rounded-lg border px-3 py-2"}),
            "resolved_entry": forms.Select(attrs={"class": "w-full rounded-lg border px-3 py-2"}),
        }


class ReviewImportForm(forms.Form):
    import_file = forms.FileField(
        label="File impor",
        widget=forms.ClearableFileInput(
            attrs={
                "class": "w-full rounded-xl border border-slate-200 px-4 py-3 text-sm file:mr-4 file:rounded-lg file:border-0 file:bg-slate-900 file:px-4 file:py-2 file:text-white",
                "accept": ".csv,.xlsx,text/csv,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            }
        )
    )


class UnansweredImportForm(forms.Form):
    import_file = forms.FileField(
        label="File impor",
        widget=forms.ClearableFileInput(
            attrs={
                "class": "w-full rounded-xl border border-slate-200 px-4 py-3 text-sm file:mr-4 file:rounded-lg file:border-0 file:bg-slate-900 file:px-4 file:py-2 file:text-white",
                "accept": ".csv,.xlsx,text/csv,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            }
        )
    )
