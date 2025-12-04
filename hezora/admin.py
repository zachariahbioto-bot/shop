from django.contrib import admin
from .models import Book, Order, OrderItem


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "price", "ai_generated", "created_at")
    search_fields = ("title", "author")


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ("book", "quantity")
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "phone", "paid", "created_at")
    inlines = (OrderItemInline,)
