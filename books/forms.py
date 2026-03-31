"""Forms for books and orders."""

import re
from django import forms
from .models import Book, Address


class BookForm(forms.ModelForm):

    class Meta:
        model = Book
        fields = [
            'title', 'author', 'isbn', 'price',
            'stock', 'genre', 'description', 'published_date'
        ]

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'author': forms.TextInput(attrs={'class': 'form-control'}),
            'isbn': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '13-digit ISBN e.g. 9780743273565',
                'maxlength': '13'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control', 'min': '0.01', 'step': '0.01'
            }),
            'stock': forms.NumberInput(attrs={
                'class': 'form-control', 'min': '0', 'max': '9999'
            }),
            'genre': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'published_date': forms.DateInput(attrs={
                'class': 'form-control', 'type': 'date'
            }),
        }

    def clean_isbn(self):
        isbn = self.cleaned_data.get('isbn', '').replace('-', '').replace(' ', '')
        if not isbn.isdigit():
            raise forms.ValidationError("ISBN must contain digits only.")
        if len(isbn) != 13:
            raise forms.ValidationError(
                f"ISBN must be exactly 13 digits. You entered {len(isbn)}."
            )
        return isbn

    def clean_price(self):
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


class AddressForm(forms.ModelForm):
    """Form for saving a new delivery address."""

    class Meta:
        model = Address
        fields = ['label', 'full_name', 'address_line1', 'address_line2',
                  'city', 'postcode', 'country', 'is_default']
        widgets = {
            'label': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'e.g. Home, Work'
            }),
            'full_name': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Full name'
            }),
            'address_line1': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Street address'
            }),
            'address_line2': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Apartment, suite, etc. (optional)'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'City'
            }),
            'postcode': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Postcode / Eircode'
            }),
            'country': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Country'
            }),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class CheckoutForm(forms.Form):

    saved_address = forms.ChoiceField(
        required=False,
        label='Deliver to a saved address',
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
    )

    customer_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 'placeholder': 'Full name'
        }),
    )

    customer_email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control', 'placeholder': 'email@example.com'
        }),
    )

    customer_phone = forms.CharField(
        required=False,
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 'placeholder': 'Optional phone number'
        }),
    )

    address = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Or type a new delivery address here'
        }),
    )

    save_address = forms.BooleanField(
        required=False,
        label='Save this address for future orders',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )

    address_label = forms.CharField(
        required=False,
        max_length=50,
        initial='Home',
        widget=forms.TextInput(attrs={
            'class': 'form-control', 'placeholder': 'Label (e.g. Home, Work)'
        }),
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        if user and user.is_authenticated:
            addresses = Address.objects.filter(user=user)
            choices = [('', '— Enter a new address —')]
            choices += [(str(a.pk), str(a)) for a in addresses]
            self.fields['saved_address'].choices = choices
            default = addresses.filter(is_default=True).first()
            if default and not self.data:
                self.fields['saved_address'].initial = str(default.pk)
        else:
            del self.fields['saved_address']
            del self.fields['save_address']
            del self.fields['address_label']

    def clean(self):
        cleaned = super().clean()
        saved = cleaned.get('saved_address')
        address_text = cleaned.get('address', '').strip()
        if not saved and not address_text:
            self.add_error('address', 'Please select a saved address or enter a new one.')
        return cleaned

    def clean_customer_name(self):
        name = self.cleaned_data.get('customer_name', '').strip()
        if not name:
            raise forms.ValidationError('Name cannot be empty.')
        return name

    def clean_address(self):
        return self.cleaned_data.get('address', '').strip()


class OrderForm(forms.Form):
    """Form for placing a single-book order with address selection."""

    saved_address = forms.ChoiceField(
        required=False,
        label='Deliver to a saved address',
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
    )

    address = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Or type a new delivery address'
        }),
    )

    save_address = forms.BooleanField(
        required=False,
        label='Save this address for future orders',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )

    address_label = forms.CharField(
        required=False,
        max_length=50,
        initial='Home',
        widget=forms.TextInput(attrs={
            'class': 'form-control', 'placeholder': 'Label (e.g. Home, Work)'
        }),
    )

    quantity = forms.IntegerField(
        min_value=1,
        max_value=100,
        widget=forms.NumberInput(attrs={
            'class': 'form-control', 'min': '1', 'max': '100',
        })
    )

    def __init__(self, *args, max_stock=None, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_stock = max_stock
        self.user = user
        if user and user.is_authenticated:
            addresses = Address.objects.filter(user=user)
            choices = [('', '— Enter a new address —')]
            choices += [(str(a.pk), str(a)) for a in addresses]
            self.fields['saved_address'].choices = choices
            default = addresses.filter(is_default=True).first()
            if default and not self.data:
                self.fields['saved_address'].initial = str(default.pk)
        else:
            del self.fields['saved_address']
            del self.fields['save_address']
            del self.fields['address_label']

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity < 1:
            raise forms.ValidationError("Quantity must be at least 1.")
        if self.max_stock is not None and quantity > self.max_stock:
            raise forms.ValidationError(f"Only {self.max_stock} copies available.")
        return quantity

    def clean(self):
        cleaned = super().clean()
        saved = cleaned.get('saved_address')
        address_text = cleaned.get('address', '').strip()
        if not saved and not address_text:
            self.add_error('address', 'Please select a saved address or enter a new one.')
        return cleaned