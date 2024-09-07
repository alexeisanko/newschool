from django.contrib import admin

from .models import CategoryLibraryStaff
from .models import LibraryStaff
from .models import TypeStaff


@admin.register(TypeStaff)
class TypeStaffAdmin(admin.ModelAdmin):
    list_display = ("type_staff",)
    search_fields = ("type_staff",)


@admin.register(CategoryLibraryStaff)
class CategoryLibraryStaffAdmin(admin.ModelAdmin):
    list_display = ("category", "get_type_staff_list")
    search_fields = ("category",)

    @admin.display(
        description="Type Staff",
    )
    def get_type_staff_list(self, obj):
        return ", ".join(obj.type_staff.values_list("type_staff", flat=True))


@admin.register(LibraryStaff)
class LibraryStaffAdmin(admin.ModelAdmin):
    list_display = ("name", "link", "category")
    search_fields = ("name", "link")
