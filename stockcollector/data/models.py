from django.db import models

class Stock(models.Model):
    """Günlük (daily) hisse senedi verileri - Foreign stocks"""
    date = models.DateTimeField(null=True, blank=True)
    open_price = models.FloatField(null=True, blank=True)
    high_price = models.FloatField(null=True, blank=True)
    low_price = models.FloatField(null=True, blank=True)
    close_price = models.FloatField(null=True, blank=True)
    adjusted_close = models.FloatField(null=True, blank=True)
    volume = models.FloatField(null=True, blank=True)
    stock_name = models.CharField(max_length=255)
    daily_return = models.FloatField(null=True, blank=True)
    volatility = models.FloatField(null=True, blank=True)
    daily_change = models.FloatField(null=True, blank=True)
    high_low_spread = models.FloatField(null=True, blank=True)
    expected_change = models.FloatField(null=True, blank=True)
    magnitude = models.FloatField(null=True, blank=True)
    context = models.FloatField(null=True, blank=True)

    class Meta:
        db_table = 'data_stock'
        indexes = [
            models.Index(fields=['date', 'stock_name']),
            models.Index(fields=['-date']),  # Descending for latest queries
        ]


class StockBST(models.Model):
    """Günlük (daily) hisse senedi verileri - BIST stocks"""
    date = models.DateTimeField(null=True, blank=True)
    open_price = models.FloatField(null=True, blank=True)
    high_price = models.FloatField(null=True, blank=True)
    low_price = models.FloatField(null=True, blank=True)
    close_price = models.FloatField(null=True, blank=True)
    adjusted_close = models.FloatField(null=True, blank=True)
    volume = models.FloatField(null=True, blank=True)
    stock_name = models.CharField(max_length=255)
    daily_return = models.FloatField(null=True, blank=True)
    volatility = models.FloatField(null=True, blank=True)
    daily_change = models.FloatField(null=True, blank=True)
    high_low_spread = models.FloatField(null=True, blank=True)
    expected_change = models.FloatField(null=True, blank=True)
    magnitude = models.FloatField(null=True, blank=True)
    context = models.FloatField(null=True, blank=True)

    class Meta:
        db_table = 'data_stockbst'
        indexes = [
            models.Index(fields=['date', 'stock_name']),
            models.Index(fields=['-date']),
        ]


class StockRealtime(models.Model):
    """
    Real-time (intraday) hisse senedi verileri
    Her 30 saniyede güncellenir, 24 saatten eski veri silinir
    Grafana için optimize edilmiş
    """
    timestamp = models.DateTimeField(db_index=True)  # Dakika bazında timestamp
    stock_name = models.CharField(max_length=255, db_index=True)
    price = models.FloatField()  # Anlık fiyat
    volume = models.FloatField()  # Anlık hacim
    change_percent = models.FloatField()  # Günlük değişim %
    
    # Meta bilgiler
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'data_stock_realtime'
        indexes = [
            models.Index(fields=['timestamp', 'stock_name']),
            models.Index(fields=['-timestamp']),  # En son veriler için
            models.Index(fields=['stock_name', '-timestamp']),  # Hisse bazında sorgu için
        ]
        ordering = ['-timestamp']  # Varsayılan: en yeniden eskiye


class Fund(models.Model):
    """
    Türk Yatırım Fonları (TEFAS verileri)
    İşbankası, Garanti, Yapı Kredi vb. fonlar
    Günlük kapanış fiyatları
    """
    fund_code = models.CharField(max_length=10, db_index=True)  # Fon kodu (örn: IPD, GMF)
    fund_name = models.CharField(max_length=255)  # Fon adı (örn: İş Portföy Para Piyasası)
    price = models.FloatField()  # Birim fiyat
    period = models.CharField(max_length=10, db_index=True)  # Fon kodu (örn: IPD, GMF)
    category = models.CharField(max_length=50, null=True, blank=True)  # Kategori (örn: Para Piyasası, Hisse, Karma)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'data_fund'
        indexes = [
            models.Index(fields=['created_at', 'fund_code']),
            models.Index(fields=['-created_at']),  # En yeni veriler
            models.Index(fields=['fund_code', '-created_at']),  # Fon bazında sorgu
            models.Index(fields=['fund_name', '-created_at']),  # Banka bazında sorgu
        ]
        unique_together = ['created_at', 'fund_code']  # Aynı fon aynı gün tekrar olmasın
        ordering = ['-created_at']


