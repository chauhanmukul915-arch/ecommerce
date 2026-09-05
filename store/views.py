from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Product, Order, OrderItem, Wishlist
def home(request):
    query = request.GET.get('q', '').strip()
    category = request.GET.get('category', '').strip()
    products = Product.objects.all()
    if query:
        products = products.filter(name__icontains=query)
    if category:
        products = products.filter(category=category)
    cart = request.session.get('cart', {})
    cart_count = sum(cart.values())
    return render(request, 'store/home.html', {
        'products': products,
        'query': query,
        'category': category,
        'cart_count': cart_count
    })
def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})
    product_id = str(product_id)
    product = Product.objects.get(id=product_id)
    current_quantity = cart.get(product_id, 0)
    if current_quantity < product.stock:
        cart[product_id] = current_quantity + 1
    request.session['cart'] = cart
    return redirect('home')
def cart(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0
    for product_id, quantity in cart.items():
        product = Product.objects.get(id=product_id)
        item_total = product.price * quantity
        total += item_total
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'item_total': item_total
        })
    return render(request, 'store/cart.html', {
        'cart_items': cart_items,
        'total': total
    })
def increase_quantity(request, product_id):
    cart = request.session.get('cart', {})
    product_id = str(product_id)
    product = Product.objects.get(id=product_id)
    if product_id in cart:
        if cart[product_id] < product.stock:
            cart[product_id] += 1
    request.session['cart'] = cart
    return redirect('cart')
def decrease_quantity(request, product_id):
    cart = request.session.get('cart', {})
    product_id = str(product_id)
    if product_id in cart:
        if cart[product_id] > 1:
            cart[product_id] -= 1
        else:
            del cart[product_id]
    request.session['cart'] = cart
    return redirect('cart')
def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    product_id = str(product_id)
    if product_id in cart:
        del cart[product_id]
    request.session['cart'] = cart
    return redirect('cart')
@login_required
def checkout(request):
    cart = request.session.get('cart', {})
    total = 0
    for product_id, quantity in cart.items():
        product = Product.objects.get(id=product_id)
        if quantity > product.stock:
            return redirect('cart')
        total += product.price * quantity
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        city = request.POST.get('city')
        pincode = request.POST.get('pincode')
        for product_id, quantity in cart.items():
            product = Product.objects.get(id=product_id)
            product.stock -= quantity
            product.save()
        order = Order.objects.create(
            user=request.user,
            name=name,
            phone=phone,
            address=address,
            city=city,
            pincode=pincode,
            total=total
        )
        for product_id, quantity in cart.items():
            product = Product.objects.get(id=product_id)
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=product.price
            )
        request.session['cart'] = {}
        return render(request, 'store/order_success.html', {
            'name': name,
            'total': total
        })
    return render(request, 'store/checkout.html', {
        'total': total
    })
def product_detail(request, product_id):
    product = Product.objects.get(id=product_id)
    return render(request, 'store/product_detail.html', {
        'product': product
    })
def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if User.objects.filter(username=username).exists():
            return render(request, 'store/register.html', {
                'error': 'Username already exists'
            })
        User.objects.create_user(
            username=username,
            password=password
        )
        return redirect('login')
    return render(request, 'store/register.html')
def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(
            request,
            username=username,
            password=password
        )
        if user is not None:
            login(request, user)
            return redirect('home')
        return render(request, 'store/login.html', {
            'error': 'Invalid username or password'
        })
    return render(request, 'store/login.html')
def user_logout(request):
    logout(request)
    return redirect('home')
@login_required
def order_history(request):
    orders = Order.objects.filter(
        user=request.user
    ).prefetch_related(
        'items__product'
    ).order_by('-created_at')
    return render(request, 'store/order_history.html', {
        'orders': orders
    })
@login_required
def toggle_wishlist(request, product_id):
    product = Product.objects.get(id=product_id)
    wishlist_item = Wishlist.objects.filter(
        user=request.user,
        product=product
    ).first()
    if wishlist_item:
        wishlist_item.delete()
    else:
        Wishlist.objects.create(
            user=request.user,
            product=product
        )
    return redirect('product_detail', product_id=product_id)
@login_required
def wishlist(request):
    wishlist_items = Wishlist.objects.filter(
        user=request.user
    ).select_related(
        'product'
    ).order_by('-created_at')
    return render(request, 'store/wishlist.html', {
        'wishlist_items': wishlist_items
    })
@login_required
def wishlist_add_to_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    cart = request.session.get('cart', {})
    product_id = str(product_id)
    current_quantity = cart.get(product_id, 0)
    if current_quantity < product.stock:
        cart[product_id] = current_quantity + 1
    request.session['cart'] = cart
    return redirect('wishlist')