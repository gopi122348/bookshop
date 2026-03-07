# Django ModelForm with server-side input validation

import re
from django import forms
from .models import Book


class BookForm(forms.ModelForm):
    """Form for creating and editing Book records with full validation."""

    class Meta:
        model = Book
        fields = [
            'title',
            'author',
            'isbn',
            'price',
            'stock',
            'genre',
            'description',
            'published_date'
        ]

        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. The Great Gatsby'
            }),

            'author': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. F. Scott Fitzgerald'
            }),

            'isbn': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '13-digit ISBN e.g. 9780743273565',
                'maxlength': '13'
            }),

            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0.01',
                'step': '0.01'
            }),

            'stock': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '9999'
            }),

            'genre': forms.Select(attrs={
                'class': 'form-control'
            }),

            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),

            'published_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }

    def clean_isbn(self):
        """ISBN must be exactly 13 numeric digits."""
        isbn = self.cleaned_data.get('isbn', '').replace('-', '').replace(' ', '')

        if not isbn.isdigit():
            raise forms.ValidationError("ISBN must contain digits only.")

        if len(isbn) != 13:
            raise forms.ValidationError(
                f"ISBN must be exactly 13 digits. You entered {len(isbn)}."
            )

        return isbn

    def clean_price(self):
        """Price must be a positive number."""
        price = self.cleaned_data.get('price')

        if price is not None and price <= 0:
            raise forms.ValidationError("Price must be greater than zero.")

        return price

    def clean_title(self):
        """Title cannot be blank or whitespace only."""
        title = self.cleaned_data.get('title', '').strip()

        if not title:
            raise forms.ValidationError("Title cannot be empty.")

        return title

    def clean_author(self):
        """Author name must contain only letters, spaces, hyphens or dots."""
        author = self.cleaned_data.get('author', '').strip()

        if not author:
            raise forms.ValidationError("Author name cannot be empty.")

        if not re.match(r'^[A-Za-z\s\.\-]+$', author):
            raise forms.ValidationError(
                "Author name may contain only letters, spaces, hyphens, or dots."
            )

        return author