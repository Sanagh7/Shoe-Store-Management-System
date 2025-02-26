from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from .models import Shoe, Category
from .forms import ShoeForm
from django.contrib import messages
from .models import CartItem
from django.contrib.auth.models import User
from .models import UserProfile
from .models import UserActivity

def home(request):
    
    shoes = Shoe.objects.all()
    categories = Category.objects.all()
    top_selling_shoes = Shoe.objects.order_by('-stock')[:5]
    return render(request, 'store/home.html',{
        'shoes': shoes,
        'shoeslen': len(shoes), 
        'top_selling_shoes': top_selling_shoes,
        'categories': categories
    })

def shoe_list(request):
    shoes = Shoe.objects.all()
    return render(request, 'store/shoe_list.html', {'shoes': shoes, 'shoeslen': len(shoes)})

def shoe_detail(request, shoe_id):
    shoe = get_object_or_404(Shoe, id=shoe_id)
    shoes = Shoe.objects.all()
    return render(request, 'store/shoe_detail.html', {'shoe': shoe, 'shoeslen': len(shoes)})

@login_required
def add_shoe(request):
    if request.method == "POST":
        form = ShoeForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('shoe_list')
    else:
        form = ShoeForm()
    return render(request, 'store/shoe_form.html', {'form': form})

@login_required
def update_shoe(request, shoe_id):
    shoe = get_object_or_404(Shoe, id=shoe_id)
    if request.method == "POST":
        form = ShoeForm(request.POST, request.FILES, instance=shoe)
        if form.is_valid():
            form.save()
            return redirect('shoe_list')
    else:
        form = ShoeForm(instance=shoe)
    return render(request, 'store/shoe_form.html', {'form': form})

@login_required
def delete_shoe(request, shoe_id):
    shoe = get_object_or_404(Shoe, id=shoe_id)
    if request.method == "POST":
        shoe.delete()
        return redirect('shoe_list')
    return render(request, 'store/confirm_delete.html', {'shoe': shoe})

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            # Check if there's a next URL in session
            next_url = request.session.get('next_url')
            if next_url == 'billing':
                del request.session['next_url']
                return redirect('billing')
            return redirect('shoe_list')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'store/login.html')

@login_required
def cart_add(request, shoe_id):
    shoe = get_object_or_404(Shoe, id=shoe_id)
    cart_item, created = CartItem.objects.get_or_create(
        user=request.user,
        shoe=shoe
    )
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    messages.success(request, 'Item added to cart.')
    return redirect('cart_view')

@login_required
def cart_remove(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    cart_item.delete()
    messages.success(request, 'Item removed from cart.')
    return redirect('cart_view')

@login_required
def cart_view(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.total_price() for item in cart_items)
    return render(request, 'store/cart.html', {
        'cart_items': cart_items,
        'total': total
    })

def check_login_and_proceed(request):
    """
    Check if user is logged in and handle navigation from cart to billing
    """
    if not request.user.is_authenticated:
        messages.warning(request, 'Please login to proceed with checkout.')
        # Store the return URL in session
        request.session['next_url'] = 'billing'
        return redirect('login')
    
    # If user is logged in, check if they have items in cart
    cart_items = CartItem.objects.filter(user=request.user)
    if not cart_items.exists():
        messages.warning(request, 'Your cart is empty.')
        return redirect('cart_view')
    
    return redirect('billing')

def sports_shoe(request):
    # Filter shoes by getting the Sports category first
    sports_category = get_object_or_404(Category, name='Sports')
    sports_shoes = Shoe.objects.filter(category=sports_category)
    return render(request, 'store/sports_shoe.html', {
        'shoes': sports_shoes,
        'shoeslen': len(sports_shoes)
    })

def category_view(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    shoes = Shoe.objects.filter(category=category)
    categories = Category.objects.all()
    return render(request, 'store/category_shoes.html', {
        'category': category,
        'shoes': shoes,
        'shoeslen': len(shoes),
        'categories': categories
    })

@login_required
def billing_view(request):
    # Clear any stored next_url
    if 'next_url' in request.session:
        del request.session['next_url']
    
    cart_items = CartItem.objects.filter(user=request.user)
    if not cart_items.exists():
        messages.warning(request, 'Your cart is empty.')
        return redirect('cart_view')
    
    total = sum(item.total_price() for item in cart_items)
    
    if request.method == "POST":
        # Process the order
        for item in cart_items:
            # Decrease stock
            shoe = item.shoe
            if shoe.stock >= item.quantity:
                shoe.stock -= item.quantity
                shoe.save()
            else:
                messages.error(request, f'Not enough stock for {shoe.name}')
                return redirect('cart_view')
        
        # Clear the cart after successful purchase
        cart_items.delete()
        messages.success(request, 'Order placed successfully!')
        return redirect('thankyou')

    return render(request, 'store/billing.html', {
        'cart_items': cart_items,
        'total': total
    })

def thankyou_view(request):
    return render(request, 'store/Thankyou.html')

def services(request):
    return render(request, 'store/services.html')

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        # Validation checks
        if password1 != password2:
            messages.error(request, 'Passwords do not match!')
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists!')
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered!')
            return redirect('register')

        try:
            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1
            )

            # Create user profile
            UserProfile.objects.create(
                user=user,
                email=email
            )

            messages.success(request, 'Registration successful! Please login.')
            return redirect('login')

        except Exception as e:
            messages.error(request, 'An error occurred during registration.')
            return redirect('register')

    return render(request, 'store/Register.html')

def user_logout(request):
    if request.user.is_authenticated:
        # Log the logout activity
        UserActivity.objects.create(
            user=request.user,
            action='logout',
            ip_address=request.META.get('REMOTE_ADDR')
        )
        logout(request)
        messages.success(request, 'You have been successfully logged out.')
    return redirect('login')