from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("email", "username", "avatar", "is_active", "created_at")
    # list_editable = ("username", "avatar")
    list_filter = ("created_at", "is_active")
    search_fields = ("email", "username")

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ("email", "created_at")
        
        return ("created_at",)