# CRUD views: list, detail, create, update, delete

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q
from .models import Book
from .forms import BookForm


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