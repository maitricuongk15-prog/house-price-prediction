from django.db import models
from django.contrib.auth.models import User


CITY_CHOICES = [
    ('Hồ Chí Minh', 'TP. Hồ Chí Minh'),
    ('Hà Nội', 'Hà Nội'),
    ('Đà Nẵng', 'Đà Nẵng'),
    ('Bình Dương', 'Bình Dương'),
    ('Đồng Nai', 'Đồng Nai'),
    ('Hải Phòng', 'Hải Phòng'),
    ('Khánh Hòa', 'Khánh Hòa'),
    ('Long An', 'Long An'),
    ('Vũng Tàu', 'Vũng Tàu'),
    ('Quảng Ninh', 'Quảng Ninh'),
    ('Cần Thơ', 'Cần Thơ'),
    ('Huế', 'Huế'),
    ('Khác', 'Khác'),
]

LEGAL_CHOICES = [
    ('Sổ đỏ', 'Sổ đỏ / Sổ hồng'),
    ('Hợp đồng mua bán', 'Hợp đồng mua bán'),
    ('Đang chờ sổ', 'Đang chờ sổ'),
    ('Unknown', 'Chưa rõ'),
]

FURNITURE_CHOICES = [
    ('Đầy đủ', 'Đầy đủ nội thất'),
    ('Cơ bản', 'Nội thất cơ bản'),
    ('Bàn giao thô', 'Bàn giao thô'),
    ('Unknown', 'Chưa rõ'),
]

STATUS_CHOICES = [
    ('active', 'Đang rao bán'),
    ('sold', 'Đã bán'),
    ('hidden', 'Đã ẩn'),
]

PROPERTY_TYPE_CHOICES = [
    ('nha_pho',   'Nhà phố'),
    ('chung_cu',  'Chung cư'),
    ('dat_nen',   'Đất nền'),
    ('biet_thu',  'Biệt thự'),
]


class Listing(models.Model):
    owner         = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings')
    title         = models.CharField(max_length=200)
    description   = models.TextField(blank=True)
    address       = models.CharField(max_length=300)
    city          = models.CharField(max_length=50, choices=CITY_CHOICES)
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPE_CHOICES, default='nha_pho')

    # ── Field chung cho mọi loại ──────────────────────────
    area          = models.FloatField(help_text='Diện tích (m²)')
    legal_status  = models.CharField(max_length=50, choices=LEGAL_CHOICES, default='Unknown')
    furniture     = models.CharField(max_length=50, choices=FURNITURE_CHOICES, default='Unknown')
    price         = models.FloatField(help_text='Giá (tỷ VNĐ)')
    predicted_price = models.FloatField(null=True, blank=True, help_text='Giá dự đoán ML (tỷ)')
    image         = models.ImageField(upload_to='listings/', blank=True, null=True)
    status        = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    # ── Field riêng: Nhà phố / Biệt thự ───────────────────
    floors        = models.IntegerField(null=True, blank=True, help_text='Số tầng')
    bedrooms      = models.IntegerField(null=True, blank=True, help_text='Số phòng ngủ')
    bathrooms     = models.IntegerField(null=True, blank=True, help_text='Số phòng tắm')
    facade_width  = models.FloatField(null=True, blank=True, help_text='Mặt tiền (m)')

    # ── Field riêng: Chung cư ─────────────────────────────
    building_name = models.CharField(max_length=150, blank=True, help_text='Tên toà / dự án')
    floor_number  = models.IntegerField(null=True, blank=True, help_text='Tầng số mấy')

    # ── Field riêng: Đất nền ───────────────────────────────
    road_width    = models.FloatField(null=True, blank=True, help_text='Đường vào rộng (m)')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def price_diff(self):
        """Chênh lệch giá thực tế vs dự đoán (%)"""
        if self.predicted_price and self.predicted_price > 0:
            return round((self.price - self.predicted_price) / self.predicted_price * 100, 1)
        return None

    def relevant_fields(self):
        """Trả về list field cần hiển thị theo từng loại BĐS, dùng cho template."""
        common = [
            ('area', f'{self.area} m²', 'Diện tích'),
        ]
        if self.property_type in ('nha_pho', 'biet_thu'):
            return common + [
                ('floors', f'{self.floors or "—"} tầng', 'Số tầng'),
                ('bedrooms', self.bedrooms or '—', 'Phòng ngủ'),
                ('bathrooms', self.bathrooms or '—', 'Phòng tắm'),
                ('facade_width', f'{self.facade_width or "—"} m', 'Mặt tiền'),
            ]
        elif self.property_type == 'chung_cu':
            return common + [
                ('bedrooms', self.bedrooms or '—', 'Phòng ngủ'),
                ('bathrooms', self.bathrooms or '—', 'Phòng tắm'),
                ('floor_number', self.floor_number or '—', 'Tầng số'),
                ('building_name', self.building_name or '—', 'Toà / dự án'),
            ]
        elif self.property_type == 'dat_nen':
            return common + [
                ('facade_width', f'{self.facade_width or "—"} m', 'Mặt tiền'),
                ('road_width', f'{self.road_width or "—"} m', 'Đường vào'),
            ]
        return common


class SavedListing(models.Model):
    user    = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='saved_by')
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'listing')

    def __str__(self):
        return f'{self.user.username} → {self.listing.title}'
