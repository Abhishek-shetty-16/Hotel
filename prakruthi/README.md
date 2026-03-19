# 🌿 Prakruthi Refreshment — Food Ordering Web Application

A full-stack food ordering system for **Prakruthi Refreshment Hotel** built with:
- **Frontend**: Django 5 (Python)
- **Backend API**: Flask (Python)
- **Database**: PostgreSQL
- **Payments**: Razorpay

---

## 📁 Project Structure

```
prakruthi/
├── flask_api/                  # Flask REST API (Port 5000)
│   ├── app.py                  # App factory & entry point
│   ├── config.py               # Configuration (DB, Razorpay keys)
│   ├── requirements.txt
│   ├── models/
│   │   └── models.py           # SQLAlchemy ORM models
│   └── routes/
│       ├── auth.py             # Customer & Admin authentication
│       ├── menu.py             # Menu & categories
│       ├── cart.py             # Cart operations
│       ├── orders.py           # Order placement & tracking
│       ├── payments.py         # Razorpay integration
│       └── admin.py            # Admin CRUD operations
│
├── django_frontend/            # Django Frontend (Port 8000)
│   ├── manage.py
│   ├── requirements.txt
│   ├── prakruthi/
│   │   ├── settings.py
│   │   └── urls.py
│   ├── prakruthi_app/
│   │   ├── views.py            # All Django views
│   │   └── urls.py             # URL routing
│   └── templates/
│       ├── base.html           # User base layout
│       ├── user/
│       │   ├── home.html       # Landing page
│       │   ├── menu.html       # Menu browsing
│       │   ├── cart.html       # Shopping cart
│       │   ├── checkout.html   # Checkout form
│       │   ├── payment.html    # Razorpay payment page
│       │   ├── order_success.html
│       │   ├── my_orders.html
│       │   ├── login.html
│       │   └── register.html
│       └── admin/
│           ├── base_admin.html # Admin sidebar layout
│           ├── login.html      # Admin login
│           ├── dashboard.html  # Stats & recent orders
│           ├── menu.html       # Menu management (CRUD)
│           └── orders.html     # Order tracking & status update
│
├── setup_db.sql                # PostgreSQL database setup
├── .env.example                # Environment variables template
└── README.md
```

---

## 🗄️ Database Schema

Matches your provided schema exactly:

| Table | Description |
|---|---|
| `admin_users` | Admin accounts with hashed passwords |
| `customers` | Registered customers |
| `categories` | Menu categories (Juices, Snacks, etc.) |
| `menu_items` | Food items with price, image, availability |
| `cart` | One active cart per customer |
| `cart_items` | Items in a customer's cart |
| `orders` | Placed orders with status tracking |
| `order_items` | Line items within each order |
| `payments` | Razorpay payment records |

---

## ⚡ Quick Setup

### 1. PostgreSQL Database

```bash
# Create database and user
psql -U postgres -f setup_db.sql

# Or manually:
psql -U postgres
CREATE DATABASE prakruthi_db;
CREATE USER prakruthi_user WITH ENCRYPTED PASSWORD 'prakruthi123';
GRANT ALL PRIVILEGES ON DATABASE prakruthi_db TO prakruthi_user;
\q
```

---

### 2. Flask API Setup

```bash
cd flask_api

# Create virtual environment
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp ../.env.example .env
# Edit .env with your actual DATABASE_URL and Razorpay keys

# Start the API server
python app.py
# Flask API running at http://localhost:5000
```

**Create the first admin user** (one-time setup):
```bash
curl -X POST http://localhost:5000/api/admin/setup \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

---

### 3. Django Frontend Setup

```bash
cd django_frontend

# Create virtual environment
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp ../.env.example .env
# Edit .env with your settings

# Run migrations (for Django session tables)
python manage.py migrate

# Start Django development server
python manage.py runserver 8000
# Django app running at http://localhost:8000
```

---

## 🔑 Razorpay Setup

1. Sign up at [https://razorpay.com](https://razorpay.com)
2. Go to **Dashboard → Settings → API Keys**
3. Generate a Test API Key
4. Add to both `.env` files:
   ```
   RAZORPAY_KEY_ID=rzp_test_XXXXXXXXXXXXXXXX
   RAZORPAY_KEY_SECRET=XXXXXXXXXXXXXXXXXXXXXXXX
   ```

---

## 🌐 URL Reference

### User-Facing Pages
| URL | Page |
|---|---|
| `/` | Home / Landing page |
| `/menu/` | Browse menu (filter by category) |
| `/menu/?category=1` | Filter by category |
| `/cart/` | Shopping cart |
| `/checkout/` | Checkout & payment |
| `/order-success/<id>/` | Order confirmation |
| `/my-orders/` | Customer order history |
| `/login/` | Customer login |
| `/register/` | Customer registration |

### Admin Panel
| URL | Page |
|---|---|
| `/admin-panel/login/` | Admin login |
| `/admin-panel/` | Dashboard with stats |
| `/admin-panel/menu/` | Menu CRUD (add/edit/delete/toggle) |
| `/admin-panel/orders/` | Order management & status updates |

### Flask REST API Endpoints
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/customer/register` | Register customer |
| POST | `/api/auth/customer/login` | Customer login |
| POST | `/api/auth/admin/login` | Admin login |
| GET | `/api/menu/` | Get available menu items |
| GET | `/api/menu/categories` | Get all categories |
| GET | `/api/cart/<customer_id>` | Get customer cart |
| POST | `/api/cart/add` | Add item to cart |
| PUT | `/api/cart/update` | Update item quantity |
| DELETE | `/api/cart/remove/<id>` | Remove cart item |
| POST | `/api/orders/place` | Place order from cart |
| GET | `/api/orders/customer/<id>` | Get customer orders |
| GET | `/api/orders/all` | (Admin) All orders |
| PUT | `/api/orders/<id>/status` | (Admin) Update order status |
| POST | `/api/payments/create-order` | Create Razorpay order |
| POST | `/api/payments/verify` | Verify payment signature |
| GET | `/api/admin/stats` | Dashboard statistics |
| GET | `/api/admin/menu` | All menu items (admin) |
| POST | `/api/admin/menu` | Add menu item |
| PUT | `/api/admin/menu/<id>` | Edit menu item |
| DELETE | `/api/admin/menu/<id>` | Delete menu item |
| PUT | `/api/admin/menu/<id>/toggle` | Toggle availability |
| GET | `/api/admin/orders` | All orders (admin) |
| PUT | `/api/admin/orders/<id>/status` | Update order status |

---

## 🔄 Order Status Flow

```
pending → confirmed → preparing → ready → delivered
                                        ↘ cancelled
```

---

## 💳 Payment Flow

```
1. Customer adds items → Cart
2. Customer clicks Checkout → Order placed in DB (status: pending)
3. Flask creates Razorpay order → Returns order ID + amount
4. Django renders Razorpay checkout widget
5. Customer pays via UPI / Card / Wallet
6. Razorpay sends payment response to browser
7. Browser POSTs to Flask /api/payments/verify
8. Flask verifies HMAC signature → Updates order to paid + confirmed
9. Django redirects to /order-success/<id>/
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Django 5, HTML5, CSS3, Vanilla JS |
| Backend API | Flask 3, Flask-SQLAlchemy, Flask-CORS |
| Database | PostgreSQL + psycopg2 |
| ORM | SQLAlchemy |
| Payments | Razorpay Python SDK |
| Fonts | Playfair Display + DM Sans (Google Fonts) |
| Icons | Font Awesome 6 |

---

## 🌿 Features Summary

### Customer Side
- ✅ Register / Login with phone number
- ✅ Browse menu by category
- ✅ Add to cart with quantity controls
- ✅ View and manage cart
- ✅ Checkout with delivery details
- ✅ Pay via Razorpay (UPI, Cards, Wallets, Netbanking)
- ✅ Order confirmation with status tracker
- ✅ View full order history

### Admin Side
- ✅ Secure admin login
- ✅ Dashboard with stats (revenue, orders, items)
- ✅ Add / Edit / Delete menu items
- ✅ Toggle item availability (on/off switch)
- ✅ Add / manage categories
- ✅ View all orders with expandable details
- ✅ Filter orders by status
- ✅ Update order status (pending → confirmed → preparing → ready → delivered)
- ✅ Search orders by ID or customer name
