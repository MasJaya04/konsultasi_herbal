from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect


class RoleRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    allowed_roles = ()

    def test_func(self):
        user = self.request.user
        if not user.is_authenticated:
            return False
        if user.is_superuser:
            return True
        return user.role in self.allowed_roles


class AdminRequiredMixin(RoleRequiredMixin):
    allowed_roles = ("admin",)


class StaffRequiredMixin(RoleRequiredMixin):
    allowed_roles = ("admin", "ai_trainer")


class NonCustomerRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role == "customer" and not request.user.is_superuser:
            return redirect("consultations:chat")
        return super().dispatch(request, *args, **kwargs)
