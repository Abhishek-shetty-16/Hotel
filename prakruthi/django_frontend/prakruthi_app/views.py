import requests
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings

API = settings.FLASK_API_URL


# ─── Helpers ────────────────────────────────────────────────────────────────

def api_get(path, params=None):
    try:
        r = requests.get(f"{API}{path}", params=params, timeout=10)
        return r.json() if r.ok else []
    except Exception:
        return []


def api_post(path, data):
    try:
        r = requests.post(f"{API}{path}", json=data, timeout=10)
        return r.json(), r.status_code
    except Exception as e:
        return {'error': str(e)}, 500


def api_put(path, data):
    try:
        r = requests.put(f"{API}{path}", json=data, timeout=10)
        return r.json(), r.status_code
    except Exception as e:
        return {'error': str(e)}, 500


def api_delete(path):
    try:
        r = requests.delete(f"{API}{path}", timeout=10)
        return r.json(), r.status_code
    except Exception as e:
        return {'error': str(e)}, 500


def get_customer(request):
    return request.session.get('customer')


def get_admin(request):
    return request.session.get('admin')


# ─── User Auth ───────────────────────────────────────────────────────────────

def login_view(request):
    if request.method == 'POST':
        phone = request.POST.get('phone')
        resp, status = api_post('/api/auth/customer/login', {'phone': phone})
        if status == 200:
            request.session['customer'] = resp['customer']
            return redirect('home')
        messages.error(request, resp.get('error', 'Login failed'))
    return render(request, 'user/login.html')


def register_view(request):
    if request.method == 'POST':
        data = {
            'name': request.POST.get('name'),
            'phone': request.POST.get('phone'),
            'email': request.POST.get('email'),
            'address': request.POST.get('address'),
        }
        resp, status = api_post('/api/auth/customer/register', data)
        if status == 201:
            request.session['customer'] = resp['customer']
            return redirect('home')
        messages.error(request, resp.get('error', 'Registration failed'))
    return render(request, 'user/register.html')


def logout_view(request):
    request.session.flush()
    return redirect('home')


# ─── User Pages ──────────────────────────────────────────────────────────────

def home(request):
    categories = api_get('/api/menu/categories')
    featured = api_get('/api/menu/')[:8]
    return render(request, 'user/home.html', {
        'categories': categories,
        'featured_items': featured,
        'customer': get_customer(request)
    })


def menu(request):
    categories = api_get('/api/menu/categories')
    category_id = request.GET.get('category')
    if category_id:
        items = api_get('/api/menu/', params={'category_id': category_id})
    else:
        items = api_get('/api/menu/')

    return render(request, 'user/menu.html', {
        'categories': categories,
        'items': items,
        'selected_category': int(category_id) if category_id else None,
        'customer': get_customer(request)
    })


def cart(request):
    customer = get_customer(request)
    if not customer:
        return redirect('login')
    cart_data = api_get(f"/api/cart/{customer['customer_id']}")
    total = sum(
        item['menu_item']['price'] * item['quantity']
        for item in cart_data.get('items', [])
        if item.get('menu_item')
    )
    return render(request, 'user/cart.html', {
        'cart': cart_data,
        'total': total,
        'customer': customer
    })


def checkout(request):
    customer = get_customer(request)
    if not customer:
        return redirect('login')

    cart_data = api_get(f"/api/cart/{customer['customer_id']}")
    total = sum(
        item['menu_item']['price'] * item['quantity']
        for item in cart_data.get('items', [])
        if item.get('menu_item')
    )

    if request.method == 'POST':
        # Place order
        resp, status = api_post('/api/orders/place', {'customer_id': customer['customer_id']})
        if status == 201:
            order_id = resp['order']['order_id']
            # Create payment record
            pay, pay_status = api_post('/api/payments/create-order', {'order_id': order_id})
            if pay_status == 200:
                return render(request, 'user/payment.html', {
                    'order': resp['order'],
                    'payment': pay,
                    'customer': customer,
                })
        messages.error(request, 'Failed to place order')

    return render(request, 'user/checkout.html', {
        'cart': cart_data,
        'total': total,
        'customer': customer
    })


def order_success(request, order_id):
    customer = get_customer(request)
    order = api_get(f"/api/orders/{order_id}")
    return render(request, 'user/order_success.html', {
        'order': order,
        'customer': customer
    })


def my_orders(request):
    customer = get_customer(request)
    if not customer:
        return redirect('login')
    orders = api_get(f"/api/orders/customer/{customer['customer_id']}")
    return render(request, 'user/my_orders.html', {
        'orders': orders,
        'customer': customer
    })


# ─── Admin Auth ──────────────────────────────────────────────────────────────

def admin_login(request):
    if request.method == 'POST':
        resp, status = api_post('/api/auth/admin/login', {
            'username': request.POST.get('username'),
            'password': request.POST.get('password')
        })
        if status == 200:
            request.session['admin'] = resp['admin']
            return redirect('admin_dashboard')
        messages.error(request, 'Invalid credentials')
    return render(request, 'admin/login.html')


def admin_logout(request):
    request.session.pop('admin', None)
    return redirect('admin_login')


# ─── Admin Pages ─────────────────────────────────────────────────────────────

def admin_dashboard(request):
    admin = get_admin(request)
    if not admin:
        return redirect('admin_login')
    stats = api_get('/api/admin/stats')
    recent_orders = api_get('/api/admin/orders')[:10]
    return render(request, 'admin/dashboard.html', {
        'admin': admin,
        'stats': stats,
        'recent_orders': recent_orders
    })


def admin_menu(request):
    admin = get_admin(request)
    if not admin:
        return redirect('admin_login')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add':
            data = {
                'name': request.POST.get('name'),
                'description': request.POST.get('description'),
                'price': float(request.POST.get('price', 0)),
                'category_id': int(request.POST.get('category_id')) if request.POST.get('category_id') else None,
                'image_url': request.POST.get('image_url'),
                'is_available': request.POST.get('is_available') == 'on'
            }
            api_post('/api/admin/menu', data)

        elif action == 'edit':
            item_id = request.POST.get('item_id')
            data = {
                'name': request.POST.get('name'),
                'description': request.POST.get('description'),
                'price': float(request.POST.get('price', 0)),
                'category_id': int(request.POST.get('category_id')) if request.POST.get('category_id') else None,
                'image_url': request.POST.get('image_url'),
                'is_available': request.POST.get('is_available') == 'on'
            }
            api_put(f'/api/admin/menu/{item_id}', data)

        elif action == 'delete':
            item_id = request.POST.get('item_id')
            api_delete(f'/api/admin/menu/{item_id}')

        elif action == 'add_category':
            api_post('/api/admin/categories', {'category_name': request.POST.get('category_name')})

        return redirect('admin_menu')

    items = api_get('/api/admin/menu')
    categories = api_get('/api/admin/categories')
    return render(request, 'admin/menu.html', {
        'admin': admin,
        'items': items,
        'categories': categories
    })


def admin_orders(request):
    admin = get_admin(request)
    if not admin:
        return redirect('admin_login')

    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        new_status = request.POST.get('order_status')
        api_put(f'/api/admin/orders/{order_id}/status', {'order_status': new_status})
        return redirect('admin_orders')

    status_filter = request.GET.get('status', '')
    orders = api_get('/api/admin/orders', params={'status': status_filter} if status_filter else None)
    return render(request, 'admin/orders.html', {
        'admin': admin,
        'orders': orders,
        'status_filter': status_filter,
        'statuses': ['pending', 'confirmed', 'preparing', 'ready', 'delivered', 'cancelled']
    })
