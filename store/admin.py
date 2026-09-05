from django.contrib import admin
from .models import Product, Order, Wishlist


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'category',
        'price',
        'stock'
    )

    list_filter = (
        'category',
    )

    search_fields = (
        'name',
        'description'
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'phone',
        'city',
        'pincode',
        'total',
        'status',
        'created_at'
    )

    list_filter = (
        'status',
        'created_at'
    )

    search_fields = (
        'name',
        'phone',
        'city'
    )


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):

    list_display = (
        'user',
        'product',
        'created_at'
    )

    list_filter = (
        'created_at',
    )

    search_fields = (
        'user__username',
        'product__name'
    )