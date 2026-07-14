from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import ValidationError

from .models import User


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Nama pengguna",
        widget=forms.TextInput(attrs={"class": "w-full rounded-lg border px-3 py-2", "placeholder": "Nama pengguna"})
    )
    password = forms.CharField(
        label="Kata sandi",
        widget=forms.PasswordInput(attrs={"class": "w-full rounded-lg border px-3 py-2", "placeholder": "Kata sandi"})
    )


class UserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "username", "email", "role", "password1", "password2")
        labels = {
            "first_name": "Nama depan",
            "last_name": "Nama belakang",
            "username": "Nama pengguna",
            "email": "Email",
            "role": "Peran",
        }
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "w-full rounded-lg border px-3 py-2"}),
            "last_name": forms.TextInput(attrs={"class": "w-full rounded-lg border px-3 py-2"}),
            "username": forms.TextInput(attrs={"class": "w-full rounded-lg border px-3 py-2"}),
            "email": forms.EmailInput(attrs={"class": "w-full rounded-lg border px-3 py-2"}),
            "role": forms.Select(attrs={"class": "w-full rounded-lg border px-3 py-2"}),
        }

    password1 = forms.CharField(label="Kata sandi", widget=forms.PasswordInput(attrs={"class": "w-full rounded-lg border px-3 py-2"}))
    password2 = forms.CharField(label="Konfirmasi kata sandi", widget=forms.PasswordInput(attrs={"class": "w-full rounded-lg border px-3 py-2"}))


class UserUpdateForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Kata sandi baru",
        required=False,
        widget=forms.PasswordInput(attrs={"class": "w-full rounded-lg border px-3 py-2"}),
    )
    password2 = forms.CharField(
        label="Konfirmasi kata sandi baru",
        required=False,
        widget=forms.PasswordInput(attrs={"class": "w-full rounded-lg border px-3 py-2"}),
    )

    class Meta:
        model = User
        fields = ("first_name", "last_name", "username", "email", "role", "password1", "password2")
        labels = {
            "first_name": "Nama depan",
            "last_name": "Nama belakang",
            "username": "Nama pengguna",
            "email": "Email",
            "role": "Peran",
        }
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "w-full rounded-lg border px-3 py-2"}),
            "last_name": forms.TextInput(attrs={"class": "w-full rounded-lg border px-3 py-2"}),
            "username": forms.TextInput(attrs={"class": "w-full rounded-lg border px-3 py-2"}),
            "email": forms.EmailInput(attrs={"class": "w-full rounded-lg border px-3 py-2"}),
            "role": forms.Select(attrs={"class": "w-full rounded-lg border px-3 py-2"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 or password2:
            if password1 != password2:
                raise ValidationError("Kata sandi baru dan konfirmasi kata sandi harus sama.")
            if len(password1) < 8:
                raise ValidationError("Kata sandi baru minimal 8 karakter.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        password1 = self.cleaned_data.get("password1")
        if password1:
            user.set_password(password1)
        if commit:
            user.save()
        return user


class UserImportForm(forms.Form):
    import_file = forms.FileField(
        label="File impor",
        widget=forms.ClearableFileInput(
            attrs={
                "class": "w-full rounded-xl border border-slate-200 px-4 py-3 text-sm file:mr-4 file:rounded-lg file:border-0 file:bg-slate-900 file:px-4 file:py-2 file:text-white",
                "accept": ".csv,.xlsx,text/csv,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            }
        )
    )
