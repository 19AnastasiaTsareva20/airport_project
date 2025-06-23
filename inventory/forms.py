from django import forms
from .models import Product, Customer, Order

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'stock_quantity']

class ProductFilterForm(forms.Form):
    search = forms.CharField(
        max_length=255, 
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Поиск по названию или описанию...'
        })
    )
    min_price = forms.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Мин. цена'
        })
    )
    max_price = forms.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Макс. цена'
        })
    )
    min_stock = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Мин. количество'
        })
    )
    max_stock = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Макс. количество'
        })
    )
    sort_by = forms.ChoiceField(
        choices=[
            ('name', 'Название'),
            ('price', 'Цена'),
            ('stock_quantity', 'Количество'),
            ('-price', 'Цена (убыв.)'),
            ('-stock_quantity', 'Количество (убыв.)')
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

class CustomerFilterForm(forms.Form):
    search = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Поиск по имени или email...'
        })
    )
    sort_by = forms.ChoiceField(
        choices=[
            ('first_name', 'Имя'),
            ('last_name', 'Фамилия'),
            ('email', 'Email'),
            ('-first_name', 'Имя (убыв.)'),
            ('-last_name', 'Фамилия (убыв.)')
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

class OrderFilterForm(forms.Form):
    search = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Поиск по номеру заказа...'
        })
    )
    status = forms.ChoiceField(
        choices=[('', 'Все статусы')] + Order.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    sort_by = forms.ChoiceField(
        choices=[
            ('placed_at', 'Дата создания'),
            ('-placed_at', 'Дата создания (убыв.)'),
            ('total_amount', 'Сумма'),
            ('-total_amount', 'Сумма (убыв.)'),
            ('status', 'Статус')
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
