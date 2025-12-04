from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.conf import settings
from django.core.mail import send_mail
from django.views.decorators.http import require_http_methods

from .models import Book, Order, OrderItem
from .forms import CheckoutForm


def _cart_count(request):
    cart = request.session.get("cart", {})
    return sum(cart.values())


def index(request):
    books = Book.objects.all().order_by("-created_at")
    return render(request, "hezora/index.html", {"books": books, "cart_count": _cart_count(request)})


def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    return render(request, "hezora/book_detail.html", {"book": book, "cart_count": _cart_count(request)})


def add_to_cart(request, pk):
    if request.method != "POST":
        return redirect("hezora:index")
    cart = request.session.get("cart", {})
    cart[str(pk)] = cart.get(str(pk), 0) + 1
    request.session["cart"] = cart
    return redirect(request.META.get("HTTP_REFERER", reverse("hezora:index")))


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


def checkout(request):
    cart = request.session.get("cart", {})
    if not cart:
        return redirect("hezora:index")

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.paid = False
            order.save()
            total = 0
            for book_id, qty in cart.items():
                book = Book.objects.get(pk=int(book_id))
                OrderItem.objects.create(order=order, book=book, quantity=qty)
                total += book.price * qty
            request.session["cart"] = {}
            return render(request, "hezora/order_summary.html", {"order": order, "total": total, "cart_count": 0})
    else:
        form = CheckoutForm()

    return render(request, "hezora/checkout.html", {"form": form, "cart_count": _cart_count(request)})


@require_http_methods(["POST"])
def simulate_payment(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    order.paid = True
    order.save()

    subject = f"Payment receipt for Order {order.id}"
    lines = [f"Thank you for your purchase!", f"Order ID: {order.id}", "Items:"]
    for item in order.items.all():
        lines.append(f"- {item.book.title} x {item.quantity} — {item.total_price()}")
    lines.append(f"Total: {order.total()}")
    message = "\n".join(lines)
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [order.email], fail_silently=True)

    return render(request, "hezora/order_summary.html", {"order": order, "total": order.total(), "cart_count": _cart_count(request)})
