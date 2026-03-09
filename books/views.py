# CRUD views: list, detail, create, update, delete
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q
from .models import Book, Order, OrderItem
from .forms import BookForm, CheckoutForm
from decimal import Decimal


def book_list(request):
    """Show all books, with optional search by title/author and genre filter."""
    
    query = request.GET.get('q', '').strip()
    genre_filter = request.GET.get('genre', '')
    
    books = Book.objects.all()

    if query:
        books = books.filter(
            Q(title__icontains=query) | Q(author__icontains=query)
        )

    if genre_filter:
        books = books.filter(genre=genre_filter)

    return render(request, 'books/book_list.html', {
        'books': books,
        'query': query,
        'genre_filter': genre_filter,
        'genres': Book.GENRE_CHOICES,
        'total_count': books.count(),
    })


def book_detail(request, pk):
    """Show full details of one book."""
    
    book = get_object_or_404(Book, pk=pk)

    return render(request, 'books/book_detail.html', {
        'book': book
    })


def book_create(request):
    """Add a new book: GET shows empty form, POST validates and saves."""

    if request.method == 'POST':
        form = BookForm(request.POST)

        if form.is_valid():
            book = form.save()
            messages.success(request, f'Book "{book.title}" added successfully!')
            return redirect('book_list')

        messages.error(request, 'Please correct the errors below.')

    else:
        form = BookForm()

    return render(request, 'books/book_form.html', {
        'form': form,
        'action': 'Add'
    })


def book_update(request, pk):
    """Edit an existing book: GET shows pre-filled form, POST saves changes."""

    book = get_object_or_404(Book, pk=pk)

    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)

        if form.is_valid():
            book = form.save()
            messages.success(request, f'Book "{book.title}" updated!')
            return redirect('book_list')

        messages.error(request, 'Please correct the errors below.')

    else:
        form = BookForm(instance=book)

    return render(request, 'books/book_form.html', {
        'form': form,
        'action': 'Edit'
    })


def book_delete(request, pk):
    """Delete a book: GET shows confirmation, POST deletes."""

    book = get_object_or_404(Book, pk=pk)

    if request.method == 'POST':
        title = book.title
        book.delete()
        messages.success(request, f'Book "{title}" deleted.')
        return redirect('book_list')

    return render(
    request, 
    'books/book_confirm_delete.html', 
    {'book': book}
)
def register(request):
    """Allow new users to create an account."""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)   # log them in immediately
            messages.success(request,
                f'Account created. Welcome, {user.username}!')
            return redirect('book_list')
        messages.error(request, 'Please correct the errors below.')
    else:
        form = UserCreationForm()
    return render(request,
                  'books/register.html', {'form': form})
def _get_cart(request):
    """
    Return the session cart dict, creating it if absent.

    Cart format:
    {
        '<book_id>': {
            'title': ...,
            'price': ...,
            'qty': ...
        }
    }
    """
    return request.session.setdefault('cart', {})


@login_required
def cart_view(request):
    """Display cart contents with per-line subtotals."""
    cart = _get_cart(request)
    items = []
    total = Decimal('0.00')

    for book_id, data in cart.items():
        sub = Decimal(str(data['price'])) * data['qty']
        total += sub

        items.append({
            **data,
            'book_id': book_id,
            'subtotal': sub
        })

    return render(
        request,
        'books/cart.html',
        {'items': items, 'total': total}
    )


@login_required
def cart_add(request, pk):
    """POST: add one copy of a book to the cart."""
    if request.method == 'POST':
        book = get_object_or_404(Book, pk=pk)
        cart = _get_cart(request)
        book_id = str(pk)

        if book_id in cart:
            cart[book_id]['qty'] += 1
        else:
            cart[book_id] = {
                'title': book.title,
                'price': str(book.price),
                'qty': 1,
            }

        request.session.modified = True
        messages.success(request, f'"{book.title}" added to cart.')

    return redirect('cart_view')


@login_required
def cart_remove(request, pk):
    """POST: remove a book from the cart entirely."""
    if request.method == 'POST':
        cart = _get_cart(request)
        cart.pop(str(pk), None)
        request.session.modified = True
        messages.info(request, 'Item removed from cart.')

    return redirect('cart_view')
@login_required
def checkout(request):
    """
    GET: Show checkout form (redirect if cart empty)
    POST: Create Order and OrderItems
    """

    cart = _get_cart(request)

    if not cart:
        messages.warning(request, 'Your cart is empty.')
        return redirect('cart_view')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)

        if form.is_valid():

            total = sum(
                Decimal(str(d['price'])) * d['qty']
                for d in cart.values()
            )

            order = Order.objects.create(
                user=request.user,
                customer_name=form.cleaned_data['customer_name'],
                customer_email=form.cleaned_data['customer_email'],
                customer_phone=form.cleaned_data.get('customer_phone', ''),
                address=form.cleaned_data['address'],
                total_price=total,
            )

            for book_id, data in cart.items():

                book = get_object_or_404(Book, pk=int(book_id))

                OrderItem.objects.create(
                    order=order,
                    book=book,
                    quantity=data['qty'],
                    price=Decimal(str(data['price']))
                )

                book.stock = max(0, book.stock - data['qty'])
                book.save()

            request.session['cart'] = {}
            request.session.modified = True

            messages.success(request, f'Order #{order.pk} placed!')
            return redirect('order_confirm', pk=order.pk)

        messages.error(request, 'Please correct the errors below.')

    else:
        form = CheckoutForm(initial={
            'customer_name': request.user.get_full_name() or request.user.username,
            'customer_email': request.user.email,
        })

    items = []
    total = Decimal('0.00')

    for book_id, data in cart.items():

        sub = Decimal(str(data['price'])) * data['qty']
        total += sub

        items.append({
            **data,
            'book_id': book_id,
            'subtotal': sub
        })

    return render(
        request,
        'books/checkout.html',
        {
            'form': form,
            'items': items,
            'total': total
        }
    )


@login_required
def order_confirm(request, pk):
    """Show confirmation page after order"""

    order = get_object_or_404(Order, pk=pk, user=request.user)

    return render(
        request,
        'books/order_confirm.html',
        {'order': order}
    )
@login_required
def order_history(request):
    """
    Display a list of all orders placed by
    the currently logged-in user, newest first.
    """
    orders = Order.objects.filter(
        user=request.user
    ).prefetch_related('items__book')
    return render(request,
                  'books/order_history.html',
                  {'orders': orders})
