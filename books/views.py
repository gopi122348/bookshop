"""books/views.py - CRUD views for Django BookShop."""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q, Sum
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm

from .models import Book, Order, OrderItem
from .forms import BookForm, OrderForm


def book_list(request):
    """Show all books with recommended section."""
    query = request.GET.get("q", "").strip()
    genre_filter = request.GET.get("genre", "")
    books = Book.objects.all()

    if query:
        books = books.filter(
            Q(title__icontains=query) |
            Q(author__icontains=query)
        )

    if genre_filter:
        books = books.filter(genre=genre_filter)

    recommended_books = (
        Book.objects
        .filter(orderitem__isnull=False)
        .annotate(total_sold=Sum("orderitem__quantity"))
        .order_by("-total_sold")[:3]
    )

    return render(
        request,
        "books/book_list.html",
        {
            "books": books,
            "query": query,
            "genre_filter": genre_filter,
            "genres": Book.GENRE_CHOICES,
            "total_count": books.count(),
            "recommended_books": recommended_books,
        },
    )


def book_detail(request, pk):
    """Show full details of one book."""
    book = get_object_or_404(Book, pk=pk)

    return render(
        request,
        "books/book_detail.html",
        {"book": book},
    )


def book_create(request):
    """Add a new book."""
    if request.method == "POST":
        form = BookForm(request.POST)

        if form.is_valid():
            book = form.save()
            messages.success(request, f'Book "{book.title}" added!')
            return redirect("book_list")

        messages.error(request, "Please correct the errors below.")

    else:
        form = BookForm()

    return render(
        request,
        "books/book_form.html",
        {
            "form": form,
            "action": "Add",
        },
    )


def book_update(request, pk):
    """Edit an existing book."""
    book = get_object_or_404(Book, pk=pk)

    if request.method == "POST":
        form = BookForm(request.POST, instance=book)

        if form.is_valid():
            book = form.save()
            messages.success(request, f'Book "{book.title}" updated!')
            return redirect("book_list")

        messages.error(request, "Please correct the errors below.")

    else:
        form = BookForm(instance=book)

    return render(
        request,
        "books/book_form.html",
        {
            "form": form,
            "action": "Edit",
        },
    )


def book_delete(request, pk):
    """Delete a book."""
    book = get_object_or_404(Book, pk=pk)

    if request.method == "POST":
        title = book.title
        book.delete()

        messages.success(request, f'Book "{title}" deleted.')
        return redirect("book_list")

    return render(
        request,
        "books/book_confirm_delete.html",
        {"book": book},
    )


def register(request):
    """User registration view."""
    if request.method == "POST":
        form = UserCreationForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Account created! You can now log in.")
            return redirect("login")

        messages.error(request, "Please correct the errors below.")

    else:
        form = UserCreationForm()

    return render(
        request,
        "registration/register.html",
        {"form": form},
    )


@login_required
def book_order(request, pk):
    """Place an order for a book."""
    book = get_object_or_404(Book, pk=pk)

    if request.method == "POST":
        form = OrderForm(request.POST)

        if form.is_valid():
            quantity = form.cleaned_data["quantity"]

            if quantity > book.stock:
                messages.error(
                    request,
                    f"Only {book.stock} copies available."
                )

                return render(
                    request,
                    "books/book_order.html",
                    {
                        "form": form,
                        "book": book,
                    },
                )

            order = Order.objects.create(
                user=request.user,
                customer_name=request.user.username,
                total_price=book.price * quantity,
                status="pending",
            )

            OrderItem.objects.create(
                order=order,
                book=book,
                quantity=quantity,
                price=book.price,
            )

            book.stock -= quantity
            book.save()

            messages.success(
                request,
                f'Successfully ordered {quantity}x "{book.title}"!'
            )

            return redirect("book_list")

    else:
        form = OrderForm()

    return render(
        request,
        "books/book_order.html",
        {
            "form": form,
            "book": book,
        },
    )
@login_required
def cart_add(request, pk):
    book = get_object_or_404(Book, pk=pk)
    cart = request.session.get('cart', {})
    book_id = str(pk)
    if book_id in cart:
        cart[book_id] += 1
    else:
        cart[book_id] = 1
    request.session['cart'] = cart
    messages.success(request, f'"{book.title}" added to cart!')
    return redirect('book_detail', pk=pk)


@login_required
def cart_view(request):
    cart = request.session.get('cart', {})
    items = []
    total = 0
    for book_id, qty in cart.items():
        try:
            book = Book.objects.get(pk=book_id)
            subtotal = book.price * qty
            total += subtotal
            items.append({
                'book_id': book_id,
                'title': book.title,
                'price': book.price,
                'qty': qty,
                'subtotal': subtotal,
            })
        except Book.DoesNotExist:
            pass
    return render(request, 'books/cart.html', {'items': items, 'total': total})


@login_required
def cart_remove(request, pk):
    cart = request.session.get('cart', {})
    cart.pop(str(pk), None)
    request.session['cart'] = cart
    return redirect('cart')


@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'books/order_history.html', {'orders': orders})