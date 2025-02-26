from django.contrib import admin
from .models import Shoe, Category, CartItem

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(Shoe)
class ShoeAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'stock']
    list_filter = ['category']
    search_fields = ['name', 'description']

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['user', 'shoe', 'quantity']
    list_filter = ['user', 'shoe']
    search_fields = ['user__username', 'shoe__name']