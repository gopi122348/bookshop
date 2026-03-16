import re                            #regular expression
from django import forms
from .models import Book


class BookForm(forms.ModelForm):    #defines how the form look in the browser

    class Meta:                      #defines how the form look in the browser
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

    def clean_isbn(self):        #strips out dashes(-)
        isbn = self.cleaned_data.get('isbn', '').replace('-', '').replace(' ', '')

        if not isbn.isdigit():
            raise forms.ValidationError("ISBN must contain digits only.")

        if len(isbn) != 13:
            raise forms.ValidationError(
                f"ISBN must be exactly 13 digits. You entered {len(isbn)}."
            )

        return isbn

    def clean_price(self):          #ensures the price is positive
        price = self.cleaned_data.get('price')

        if price is not None and price <= 0:
            raise forms.ValidationError("Price must be greater than zero.")

        return price

    def clean_title(self):
        title = self.cleaned_data.get('title', '').strip()

        if not title:
            raise forms.ValidationError("Title cannot be empty.")

        return title

    def clean_author(self):
        author = self.cleaned_data.get('author', '').strip()

        if not author:
            raise forms.ValidationError("Author name cannot be empty.")

        if not re.match(r'^[A-Za-z\s\.\-]+$', author):
            raise forms.ValidationError()

        return author


class CheckoutForm(forms.Form):

    customer_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Full name'
        }),
    )

    customer_email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'email@example.com'
        }),
    )

    customer_phone = forms.CharField(
        required=False,
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Optional phone number'
        }),
    )

    address = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Delivery address'
        }),
    )

    def clean_customer_name(self):
        name = self.cleaned_data.get('customer_name', '').strip()
        if not name:
            raise forms.ValidationError('Name cannot be empty.')
        return name

    def clean_address(self):
        addr = self.cleaned_data.get('address', '').strip()
        if not addr:
            raise forms.ValidationError('Please enter a delivery address.')
        return addr
class OrderForm(forms.Form):
    """Form for placing a book order with quantity validation."""
    quantity = forms.IntegerField(
        min_value=1,
        max_value=100,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '1',
            'max': '100',
        })
    )

    def __init__(self, *args, max_stock=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_stock = max_stock

    def clean_quantity(self):
        """Quantity must be at least 1 and not exceed stock."""
        quantity = self.cleaned_data.get('quantity')
        if quantity < 1:
            raise forms.ValidationError("Quantity must be at least 1.")
        if self.max_stock is not None and quantity > self.max_stock:
            raise forms.ValidationError(
                f"Only {self.max_stock} copies available."
            )
        return quantity