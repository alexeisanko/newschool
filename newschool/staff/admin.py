from django.contrib import admin

from .models import CategoryLibraryStaff
from .models import LibraryStaff
from .models import SiteSection
from .models import TypeStaff


@admin.register(SiteSection)
class SiteSectionAdmin(admin.ModelAdmin):
    list_display = ("name", "url_name", "icon", "order", "is_active")
    list_editable = ("order", "is_active")
    search_fields = ("name", "url_name")
    list_filter = ("is_active",)


@admin.register(TypeStaff)
class TypeStaffAdmin(admin.ModelAdmin):
    list_display = ("type_staff", "get_sections_list")
    search_fields = ("type_staff",)
    filter_horizontal = ("site_sections",)
    
    @admin.display(description="Site Sections")
    def get_sections_list(self, obj):
        return ", ".join(obj.site_sections.values_list("name", flat=True))


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
