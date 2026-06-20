from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import (
    Listing, CITY_CHOICES, LEGAL_CHOICES, FURNITURE_CHOICES,
    PROPERTY_TYPE_CHOICES,
)


class PredictForm(forms.Form):
    property_type = forms.ChoiceField(
        label='Loại bất động sản',
        choices=PROPERTY_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-input', 'id': 'id_property_type'})
    )
    area = forms.FloatField(
        label='Diện tích (m²)',
        min_value=10, max_value=5000,
        widget=forms.NumberInput(attrs={'placeholder': 'VD: 80', 'class': 'form-input'})
    )
    floors = forms.IntegerField(
        label='Số tầng',
        min_value=1, max_value=50, initial=1, required=False,
        widget=forms.NumberInput(attrs={'class': 'form-input'})
    )
    bedrooms = forms.IntegerField(
        label='Số phòng ngủ',
        min_value=1, max_value=20, initial=2, required=False,
        widget=forms.NumberInput(attrs={'class': 'form-input'})
    )
    bathrooms = forms.IntegerField(
        label='Số phòng tắm',
        min_value=1, max_value=20, initial=1, required=False,
        widget=forms.NumberInput(attrs={'class': 'form-input'})
    )
    city = forms.ChoiceField(
        label='Tỉnh / Thành phố',
        choices=CITY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-input'})
    )
    legal_status = forms.ChoiceField(
        label='Pháp lý',
        choices=LEGAL_CHOICES,
        widget=forms.Select(attrs={'class': 'form-input'})
    )
    furniture = forms.ChoiceField(
        label='Nội thất',
        choices=FURNITURE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-input'})
    )

    def clean(self):
        cleaned = super().clean()
        ptype = cleaned.get('property_type')
        if ptype in ('nha_pho', 'biet_thu'):
            for f, label in [('floors', 'Số tầng'), ('bedrooms', 'Phòng ngủ'), ('bathrooms', 'Phòng tắm')]:
                if cleaned.get(f) is None:
                    self.add_error(f, f'{label} là bắt buộc với loại BĐS này.')
        elif ptype == 'chung_cu':
            for f, label in [('bedrooms', 'Phòng ngủ'), ('bathrooms', 'Phòng tắm')]:
                if cleaned.get(f) is None:
                    self.add_error(f, f'{label} là bắt buộc với chung cư.')
        return cleaned


class ListingForm(forms.ModelForm):
    class Meta:
        model  = Listing
        fields = [
            'title', 'description', 'address', 'city', 'property_type',
            'area', 'floors', 'bedrooms', 'bathrooms', 'facade_width',
            'building_name', 'floor_number', 'road_width',
            'legal_status', 'furniture', 'price', 'image',
        ]
        widgets = {
            'title':         forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Tiêu đề tin rao'}),
            'description':   forms.Textarea(attrs={'class': 'form-input', 'rows': 4, 'placeholder': 'Mô tả chi tiết...'}),
            'address':       forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Địa chỉ cụ thể'}),
            'city':          forms.Select(attrs={'class': 'form-input'}),
            'property_type': forms.Select(attrs={'class': 'form-input', 'id': 'id_property_type'}),
            'area':          forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'm²'}),
            'floors':        forms.NumberInput(attrs={'class': 'form-input'}),
            'bedrooms':      forms.NumberInput(attrs={'class': 'form-input'}),
            'bathrooms':     forms.NumberInput(attrs={'class': 'form-input'}),
            'facade_width':  forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'm', 'step': '0.1'}),
            'building_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'VD: Vinhomes Central Park'}),
            'floor_number':  forms.NumberInput(attrs={'class': 'form-input'}),
            'road_width':    forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'm', 'step': '0.1'}),
            'legal_status':  forms.Select(attrs={'class': 'form-input'}),
            'furniture':     forms.Select(attrs={'class': 'form-input'}),
            'price':         forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Tỷ VNĐ', 'step': '0.1'}),
            'image':         forms.ClearableFileInput(attrs={'class': 'form-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Tất cả field riêng đều không required ở mức Django form
        # (validate thủ công theo property_type trong clean())
        for f in ['floors', 'bedrooms', 'bathrooms', 'facade_width',
                   'building_name', 'floor_number', 'road_width']:
            self.fields[f].required = False

    def clean(self):
        cleaned = super().clean()
        ptype = cleaned.get('property_type')

        # Validate field bắt buộc theo từng loại BĐS
        if ptype in ('nha_pho', 'biet_thu'):
            for f, label in [('floors', 'Số tầng'), ('bedrooms', 'Phòng ngủ'), ('bathrooms', 'Phòng tắm')]:
                if cleaned.get(f) is None:
                    self.add_error(f, f'{label} là bắt buộc với loại BĐS này.')
        elif ptype == 'chung_cu':
            for f, label in [('bedrooms', 'Phòng ngủ'), ('bathrooms', 'Phòng tắm')]:
                if cleaned.get(f) is None:
                    self.add_error(f, f'{label} là bắt buộc với chung cư.')
        elif ptype == 'dat_nen':
            if cleaned.get('facade_width') is None:
                self.add_error('facade_width', 'Mặt tiền là bắt buộc với đất nền.')

        return cleaned


class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Email'})
    )

    class Meta:
        model  = User
        fields = ('username', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Tên đăng nhập'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-input', 'placeholder': 'Mật khẩu'})
        self.fields['password2'].widget.attrs.update({'class': 'form-input', 'placeholder': 'Nhập lại mật khẩu'})
