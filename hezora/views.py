from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.conf import settings
from django.core.mail import send_mail
from django.http import FileResponse
import os

from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from .models import Book, Order, OrderItem
from .forms import CheckoutForm, SignUpForm


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('hezora:index')
    else:
        form = SignUpForm()
    return render(request, 'hezora/signup.html', {'form': form})


def _cart_count(request):
    cart = request.session.get("cart", {})
    return sum(cart.values())


def index(request):
    books = Book.objects.all().order_by("-created_at")
    return render(request, "hezora/index.html", {"books": books, "cart_count": _cart_count(request)})


def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    return render(request, "hezora/book_detail.html", {"book": book, "cart_count": _cart_count(request)})


def download_book(request, pk):
    """Download book PDF directly"""
    book = get_object_or_404(Book, pk=pk)
    
    if book.pdf:
        # Get the file path
        file_path = book.pdf.path
        
        if os.path.exists(file_path):
            # Return the file as download
            response = FileResponse(open(file_path, 'rb'), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{book.title}.pdf"'
            return response
    
    # If file doesn't exist, redirect back
    return redirect("hezora:book_detail", pk=pk)


def add_to_cart(request, pk):
    if request.method != "POST":
        return redirect("hezora:index")
    cart = request.session.get("cart", {})
    cart[str(pk)] = cart.get(str(pk), 0) + 1
    request.session["cart"] = cart
    return redirect(request.META.get("HTTP_REFERER", reverse("hezora:index")))


@login_required
def cart_view(request):
    cart = request.session.get("cart", {})
    items = []
    total = Decimal("0.00")
    for book_id, qty in cart.items():
        try:
            book = Book.objects.get(pk=int(book_id))
        except Book.DoesNotExist:
            continue
        items.append({"book": book, "quantity": qty, "line_total": book.price * qty})
        total += book.price * qty
    return render(request, "hezora/cart.html", {"items": items, "total": total, "cart_count": _cart_count(request)})


def library_view(request):
    return render(request, "hezora/library.html", {"cart_count": _cart_count(request)})


def add_to_favorites(request, pk):
    favorites = request.session.get("favorites", [])
    if pk not in favorites:
        favorites.append(pk)
    request.session["favorites"] = favorites
    return redirect(request.META.get("HTTP_REFERER", reverse("hezora:index")))


def favorites_view(request):
    favorites = request.session.get("favorites", [])
    books = Book.objects.filter(pk__in=favorites)
    return render(request, "hezora/favorites.html", {"books": books, "cart_count": _cart_count(request)})


@login_required
def profile_view(request):
    return render(request, 'hezora/profile.html')


@login_required
def checkout(request):
    cart = request.session.get("cart", {})
    if not cart:
        return redirect("hezora:index")
    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.paid = True  # Mark as paid immediately (no payment processing)
            order.save()
            total = 0
            for book_id, qty in cart.items():
                book = Book.objects.get(pk=int(book_id))
                OrderItem.objects.create(order=order, book=book, quantity=qty)
                total += book.price * qty
            request.session["cart"] = {}
            
            # Send receipt email
            subject = f"Thank you for your order! Order {order.id}"
            lines = [f"Thank you for your purchase!", f"Order ID: {order.id}", "Items:"]
            for item in order.items.all():
                lines.append(f"- {item.book.title} x {item.quantity} — KSH {item.total_price()}")
            lines.append(f"Total: KSH {total}")
            message = "\n".join(lines)
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [order.email], fail_silently=True)
            
            return render(request, "hezora/order_summary.html", {"order": order, "total": total, "cart_count": 0})
    else:
        form = CheckoutForm()

    return render(request, "hezora/checkout.html", {"form": form, "cart_count": _cart_count(request)})