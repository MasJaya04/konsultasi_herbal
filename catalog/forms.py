from django import forms
from django.utils.text import slugify

from .models import Product, ProductCategory


class ProductImportForm(forms.Form):
    csv_file = forms.FileField(
        label="File impor",
        widget=forms.ClearableFileInput(
            attrs={
                "class": "w-full rounded-xl border border-slate-200 px-4 py-3 text-sm file:mr-4 file:rounded-lg file:border-0 file:bg-slate-900 file:px-4 file:py-2 file:text-white",
                "accept": ".csv,.xlsx,text/csv,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            }
        )
    )


class ProductCategoryForm(forms.ModelForm):
    class Meta:
        model = ProductCategory
        fields = ("name", "description")
        labels = {
            "name": "Nama",
            "description": "Deskripsi",
        }
        widgets = {
            "name": forms.TextInput(attrs={"class": "w-full rounded-lg border px-3 py-2"}),
            "description": forms.Textarea(attrs={"class": "w-full rounded-lg border px-3 py-2", "rows": 3}),
        }


class ProductForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["slug"].required = False

    def clean_slug(self):
        name = self.cleaned_data.get("name", "")
        slug = self.cleaned_data.get("slug", "")
        slug_value = slugify(slug or name)
        if not slug_value:
            raise forms.ValidationError("Slug tidak dapat dibuat. Isi nama produk terlebih dahulu.")
        queryset = Product.objects.filter(slug=slug_value)
        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise forms.ValidationError("Slug produk sudah digunakan. Gunakan nama produk lain.")
        return slug_value

    class Meta:
        model = Product
        fields = (
            "category",
            "name",
            "slug",
            "description",
            "benefits",
            "usage_instructions",
            "contraindications",
            "is_active",
        )
        labels = {
            "category": "Kategori",
            "name": "Nama produk",
            "slug": "Slug",
            "description": "Deskripsi",
            "benefits": "Manfaat",
            "usage_instructions": "Aturan pakai",
            "contraindications": "Kontraindikasi",
            "is_active": "Aktif",
        }
        widgets = {
            "category": forms.Select(attrs={"class": "w-full rounded-lg border px-3 py-2"}),
            "name": forms.TextInput(attrs={"class": "w-full rounded-lg border px-3 py-2"}),
            "slug": forms.TextInput(attrs={"class": "w-full rounded-lg border px-3 py-2"}),
            "description": forms.Textarea(attrs={"class": "w-full rounded-lg border px-3 py-2", "rows": 3}),
            "benefits": forms.Textarea(attrs={"class": "w-full rounded-lg border px-3 py-2", "rows": 4}),
            "usage_instructions": forms.Textarea(attrs={"class": "w-full rounded-lg border px-3 py-2", "rows": 4}),
            "contraindications": forms.Textarea(attrs={"class": "w-full rounded-lg border px-3 py-2", "rows": 4}),
            "is_active": forms.CheckboxInput(attrs={"class": "rounded border-slate-300"}),
        }
