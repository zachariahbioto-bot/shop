from django.contrib import admin
from .models import Book, Order, OrderItem, Profile


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "price", "ai_generated", "created_at")
    search_fields = ("title", "author")


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user",)
    search_fields = ("user__username",)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ("book", "quantity")
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "phone", "paid", "created_at")
    inlines = (OrderItemInline,)
