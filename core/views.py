from django.shortcuts import render
from django.core.mail import send_mail
# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Order
from django.contrib.auth.decorators import user_passes_test,login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Category
from twilio.rest import Client
from django.conf import settings
from django.core.mail import send_mail
from .utils import send_whatsapp_message, send_html_email
from django.http import JsonResponse
from .models import Cart, CartItem, Product
from .models import Cart, CartItem
def home(request):
    products = Product.objects.filter(available=True)
    return render(request, 'core/home.html', {'products': products})
def product_list(request):
    category_id = request.GET.get('category')
    products = Product.objects.filter(available=True)
    categories = Category.objects.all()

    if category_id:
        products = products.filter(category_id=category_id)

    return render(request, 'core/products.html', {'products': products, 'categories': categories})
def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    request.session['cart'] = cart
    return redirect('cart')  # Redirect to cart page after adding
def cart_view(request):
    cart = request.session.get('cart', {})
    items = []
    total = 0
    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=product_id)
        item_total = product.price * quantity
        total += item_total
        items.append({
            'product': product,
            'quantity': quantity,
            'item_total': item_total
        })
    return render(request, 'core/cart.html', {'items': items, 'total': total})


@login_required
def checkout(request):
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.items.all()
        if not cart_items:
            messages.warning(request, "Your cart is empty!")
            return redirect('cart_view')
    except Cart.DoesNotExist:
        messages.warning(request, "Your cart is empty!")
        return redirect('cart_view')

    if request.method == 'POST':
        name = request.POST['name']
        address = request.POST['address']
        phone = request.POST['phone']
        email = request.user.email
        user = request.user
        order_details = []

        for item in cart_items:
            Order.objects.create(
                customer_name=name,
                address=address,
                phone=phone,
                product=item.product,
                quantity=item.quantity,
                user=user,
                email=email
            )
            order_details.append(f"{item.product.name} (x{item.quantity})")

        # Prepare email messages
        customer_subject = f"Your Bihar Desi Foods Order Confirmation"
        customer_html = f"""
        <div style="font-family: Arial, sans-serif; max-width:600px; margin:auto; padding:20px; border:1px solid #ddd; border-radius:10px;">
            <div style="text-align:center; margin-bottom:20px;">
                <img src="https://i.postimg.cc/MKvpgbTT/bihar-desi-food.png" 
                    alt="Bihar Desi Foods" 
                    style="width:100%; max-width:600px; height:auto; display:block; margin:auto; border-radius:10px;">
            </div>
            <h2 style="color:#8B0000; text-align:center;">Bihar Desi Foods</h2>
            <p>Hi {name},</p>
            <p>Thank you for shopping with us! 🎉</p>
            <p><b>Order Summary:</b><br>{'<br>'.join(order_details)}</p>
            <p><b>Delivery Address:</b><br>{name}<br>{address}<br>Phone: {phone}</p>
            <p>We will notify you when your order is shipped.</p>
            <div style="text-align:center; margin-top:20px;">
                <a href="https://yourwebsite.com" 
                style="background-color:#ff6600; color:#fff; padding:10px 20px; text-decoration:none; border-radius:5px;">
                Visit Our Site
                </a>
            </div>
            <p style="font-size:12px; color:#555; text-align:center; margin-top:20px;">
                © Bihar Desi Foods | <a href="https://yourwebsite.com" style="color:#555;">https://yourwebsite.com</a>
            </p>
        </div>
        """

        admin_subject = f"New Order Received from {name}"
        admin_html = f"""
        <h2>New Order Alert</h2>
        <div style="text-align:center; margin-bottom:20px;">
        <img src="https://i.postimg.cc/MKvpgbTT/bihar-desi-food.png" 
            alt="Bihar Desi Foods" 
            style="width:100%; max-width:150px; height:auto; display:block; margin:auto; border-radius:10px;">
        </div>
        <p>Customer: {name}<br>Phone: {phone}<br>Email: {email or 'Not Provided'}</p>
        <p><b>Items:</b><br>{'<br>'.join(order_details)}</p>
        <p>Address:<br>{address}</p>
        """

        customer_message = f"""
Hi {name}, your order has been placed successfully! 🎉
We will notify you when it’s shipped.
Thank you for supporting Bihar Desi Foods!
"""

        admin_message = f"""
📦 NEW ORDER
Customer: {name}
Phone: {phone}
Email: {email or 'Not Provided'}
Items:
{chr(10).join(order_details)}
Address:
{address}
"""

        # Send email to customer and admin
        if email:
            send_html_email(customer_subject, customer_html, [email])
        send_html_email(admin_subject, admin_html, [settings.ADMIN_EMAIL])

        # Send WhatsApp (with SMS fallback)
        from_whatsapp = settings.TWILIO_WHATSAPP_FROM
        admin_whatsapp = 'whatsapp:+917903598027'

        if phone:
            customer_whatsapp = f'whatsapp:+91{phone}'
            if customer_whatsapp != from_whatsapp:
                send_whatsapp_message(customer_whatsapp, customer_message, fallback_sms=True)

        if admin_whatsapp != from_whatsapp:
            send_whatsapp_message(admin_whatsapp, admin_message, fallback_sms=False)

        # ✅ Clear cart items after order
        cart.items.all().delete()

        messages.success(request, "Your order has been placed! Confirmation email and WhatsApp (with SMS fallback) sent.")
        return redirect('home')

    return render(request, 'core/checkout.html')




    return render(request, 'core/checkout.html')
@login_required
def ajax_increase_quantity(request, product_id):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    product = get_object_or_404(Product, id=product_id)
    cart_item, _ = CartItem.objects.get_or_create(cart=cart, product=product)
    cart_item.quantity += 1
    cart_item.save()

    total = sum(item.product.price * item.quantity for item in cart.items.all())
    item_total = cart_item.product.price * cart_item.quantity

    return JsonResponse({'success': True, 'quantity': cart_item.quantity, 'item_total': item_total, 'total': total})


@login_required
def ajax_decrease_quantity(request, product_id):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.filter(cart=cart, product=product).first()
    if cart_item:
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()

    total = sum(item.product.price * item.quantity for item in cart.items.all())
    item_total = cart_item.product.price * cart_item.quantity if cart_item else 0

    return JsonResponse({'success': True, 'quantity': cart_item.quantity if cart_item else 0, 'item_total': item_total, 'total': total})

@login_required
def ajax_remove_from_cart(request, product_id):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    product = get_object_or_404(Product, id=product_id)
    CartItem.objects.filter(cart=cart, product=product).delete()

    total = sum(item.product.price * item.quantity for item in cart.items.all())

    return JsonResponse({'success': True, 'total': total})
def admin_only(user):
    return user.is_superuser  # Only superusers allowed
@login_required
@user_passes_test(admin_only)
def order_list(request):
    orders = Order.objects.all().order_by('-order_date')
    return render(request, 'core/order_list.html', {'orders': orders})

#Login,signuo,logout functionality

def signup_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken')
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('login')
    return render(request, 'core/signup.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'core/login.html')

def logout_view(request):
    logout(request)
    return redirect('home')
@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-order_date')
    return render(request, 'core/my-orders.html', {'orders': orders})


#Adding item in Cart Logic here 

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.user.is_authenticated:
        # Logged-in user → use DB cart
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            cart_item.quantity += 1
            cart_item.save()
    else:
        # Anonymous user → use session cart
        cart = request.session.get('cart', {})
        cart[str(product_id)] = cart.get(str(product_id), 0) + 1
        request.session['cart'] = cart

    messages.success(request, f"{product.name} added to cart.")
    return redirect('cart_view')
@login_required
def cart_view(request):
    item_list = []
    total = 0

    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        items = cart.items.all()
        for item in items:
            item_total = item.product.price * item.quantity
            total += item_total
            item_list.append({
                'product': item.product,
                'quantity': item.quantity,
                'item_total': item_total,
            })
    else:
        session_cart = request.session.get('cart', {})
        for product_id_str, quantity in session_cart.items():
            product_id = int(product_id_str)
            product = get_object_or_404(Product, id=product_id)
            item_total = product.price * quantity
            total += item_total
            item_list.append({
                'product': product,
                'quantity': quantity,
                'item_total': item_total,
            })

    context = {
        'items': item_list,
        'total': total,
    }
    return render(request, 'core/cart.html', context)