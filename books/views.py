"""books/views.py - CRUD views for Django BookShop."""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q, Sum
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.admin.views.decorators import staff_member_required
from .models import Book, Order, OrderItem, Address
from .forms import BookForm, OrderForm, CheckoutForm, AddressForm

FORM_ERROR_MESSAGE = "Please correct the errors below."


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


@staff_member_required
def book_create(request):
    """Add a new book."""
    if request.method == "POST":
        form = BookForm(request.POST)
        if form.is_valid():
            book = form.save()
            messages.success(request, f'Book "{book.title}" added!')
            return redirect("book_list")
        messages.error(request, FORM_ERROR_MESSAGE)
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


@staff_member_required
def book_update(request, pk):
    """Edit an existing book."""
    book = get_object_or_404(Book, pk=pk)
    if request.method == "POST":
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            book = form.save()
            messages.success(request, f'Book "{book.title}" updated!')
            return redirect("book_list")
        messages.error(request, FORM_ERROR_MESSAGE)
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


@staff_member_required
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
        messages.error(request, FORM_ERROR_MESSAGE)
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
        form = OrderForm(request.POST, user=request.user)
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
                    {"form": form, "book": book},
                )

            # Resolve delivery address
            saved_id = form.cleaned_data.get("saved_address")
            if saved_id:
                addr_obj = get_object_or_404(Address, pk=saved_id, user=request.user)
                delivery_address = addr_obj.as_text()
            else:
                delivery_address = form.cleaned_data.get("address", "")
                # Optionally save this new address
                if form.cleaned_data.get("save_address") and delivery_address:
                    if form.cleaned_data.get("is_default_new"):
                        Address.objects.filter(user=request.user).update(is_default=False)
                    Address.objects.create(
                        user=request.user,
                        label=form.cleaned_data.get("address_label") or "Home",
                        full_name=request.user.get_full_name() or request.user.username,
                        address_line1=delivery_address,
                        city="",
                        postcode="",
                    )

            order = Order.objects.create(
                user=request.user,
                customer_name=request.user.username,
                customer_email=request.user.email or "",
                address=delivery_address,
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
        form = OrderForm(user=request.user)
    return render(
        request,
        "books/book_order.html",
        {"form": form, "book": book},
    )


@login_required
def cart_add(request, pk):
    """Add a book to the session cart."""
    book = get_object_or_404(Book, pk=pk)
    cart = request.session.get("cart", {})
    book_id = str(pk)
    if book_id in cart:
        cart[book_id] += 1
    else:
        cart[book_id] = 1
    request.session["cart"] = cart
    messages.success(request, f'"{book.title}" added to cart!')
    return redirect("book_detail", pk=pk)


@login_required
def cart_view(request):
    """Display the current session cart."""
    cart = request.session.get("cart", {})
    items = []
    total = 0
    for book_id, qty in cart.items():
        try:
            book = Book.objects.get(pk=book_id)
            subtotal = book.price * qty
            total += subtotal
            items.append(
                {
                    "book_id": book_id,
                    "title": book.title,
                    "price": book.price,
                    "qty": qty,
                    "subtotal": subtotal,
                }
            )
        except Book.DoesNotExist:
            pass
    return render(
        request,
        "books/cart.html",
        {"items": items, "total": total},
    )


@login_required
def cart_remove(request, pk):
    """Remove a book from the session cart."""
    cart = request.session.get("cart", {})
    cart.pop(str(pk), None)
    request.session["cart"] = cart
    return redirect("cart_view")


@login_required
def order_history(request):
    """Show all past orders for the logged-in user."""
    orders = Order.objects.filter(user=request.user).order_by("-created_at")
    return render(
        request,
        "books/order_history.html",
        {"orders": orders},
    )


@login_required
def checkout(request):
    """Process cart checkout and create orders."""
    cart = request.session.get('cart', {})
    if not cart:
        messages.error(request, "Your cart is empty.")
        return redirect('cart_view')

    # Build cart items for display
    items = []
    total = 0
    for book_id, qty in cart.items():
        book = get_object_or_404(Book, pk=int(book_id))
        subtotal = book.price * qty
        total += subtotal
        items.append({'book': book, 'title': book.title, 'qty': qty, 'subtotal': subtotal})

    if request.method == 'POST':
        form = CheckoutForm(request.POST, user=request.user)
        if form.is_valid():
            # Resolve delivery address
            saved_id = form.cleaned_data.get('saved_address')
            if saved_id:
                addr_obj = get_object_or_404(Address, pk=saved_id, user=request.user)
                delivery_address = addr_obj.as_text()
            else:
                delivery_address = form.cleaned_data.get('address', '')
                if form.cleaned_data.get('save_address') and delivery_address:
                    Address.objects.create(
                        user=request.user,
                        label=form.cleaned_data.get('address_label') or 'Home',
                        full_name=form.cleaned_data.get('customer_name', ''),
                        address_line1=delivery_address,
                        city='',
                        postcode='',
                    )

            # Stock check
            for book_id, qty in cart.items():
                book = get_object_or_404(Book, pk=int(book_id))
                if qty > book.stock:
                    messages.error(
                        request,
                        f'Only {book.stock} copies of "{book.title}" available.'
                    )
                    return redirect('cart_view')

            # Create orders
            for book_id, qty in cart.items():
                book = get_object_or_404(Book, pk=int(book_id))
                order = Order.objects.create(
                    user=request.user,
                    customer_name=form.cleaned_data.get('customer_name', request.user.username),
                    customer_email=form.cleaned_data.get('customer_email', request.user.email or ''),
                    customer_phone=form.cleaned_data.get('customer_phone', ''),
                    address=delivery_address,
                    total_price=book.price * qty,
                    status='pending',
                )
                OrderItem.objects.create(
                    order=order,
                    book=book,
                    quantity=qty,
                    price=book.price,
                )
                book.stock -= qty
                book.save()

            request.session['cart'] = {}
            messages.success(request, "Order placed successfully!")
            return redirect('order_history')
    else:
        form = CheckoutForm(user=request.user)

    return render(request, 'books/checkout.html', {
        'form': form,
        'items': items,
        'total': total,
    })


@login_required
def address_list(request):
    """Show and manage saved addresses."""
    addresses = Address.objects.filter(user=request.user)
    form = AddressForm()
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            if address.is_default:
                Address.objects.filter(user=request.user).update(is_default=False)
            address.save()
            messages.success(request, 'Address saved!')
            return redirect('address_list')
    return render(request, 'books/address_list.html', {
        'addresses': addresses,
        'form': form,
    })


@login_required
def address_delete(request, pk):
    """Delete a saved address."""
    address = get_object_or_404(Address, pk=pk, user=request.user)
    if request.method == 'POST':
        address.delete()
        messages.success(request, 'Address deleted.')
    return redirect('address_list')


@login_required
def address_set_default(request, pk):
    """Set an address as the default."""
    address = get_object_or_404(Address, pk=pk, user=request.user)
    Address.objects.filter(user=request.user).update(is_default=False)
    address.is_default = True
    address.save()
    messages.success(request, f'"{address.label}" set as default address.')
    return redirect('address_list')