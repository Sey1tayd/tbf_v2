from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """Özel kullanıcı modeli - isim, soyisim ve unique username"""
    first_name = models.CharField(max_length=150, verbose_name="İsim", blank=False)
    last_name = models.CharField(max_length=150, verbose_name="Soyisim", blank=False)
    username = models.CharField(
        max_length=150,
        unique=True,
        verbose_name="Kullanıcı Adı",
        help_text="Her kullanıcı için benzersiz olmalıdır.",
        blank=False
    )
    
    class Meta:
        verbose_name = "Kullanıcı"
        verbose_name_plural = "Kullanıcılar"
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.username})"


class Topic(models.Model):
    """Konu/Başlık modeli - Madde numarası ve başlık"""
    madde_no = models.CharField(max_length=50, verbose_name="Madde No", db_index=True)
    baslik = models.CharField(max_length=255, verbose_name="Başlık")
    sayfa = models.IntegerField(verbose_name="Sayfa", default=1)
    order = models.IntegerField(verbose_name="Sıra", default=0, help_text="Gösterim sırası")
    
    class Meta:
        verbose_name = "Konu"
        verbose_name_plural = "Konular"
        ordering = ['order', 'madde_no']
    
    def __str__(self):
        return f"{self.madde_no} - {self.baslik}"


class Explanation(models.Model):
    """Açıklama modeli - Konuya bağlı açıklamalar"""
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='aciklamalar', verbose_name="Konu")
    numara = models.CharField(max_length=50, verbose_name="Numara")
    metin = models.TextField(verbose_name="Metin")
    sayfa = models.IntegerField(verbose_name="Sayfa", default=1)
    
    class Meta:
        verbose_name = "Açıklama"
        verbose_name_plural = "Açıklamalar"
        ordering = ['topic', 'numara']
    
    def __str__(self):
        return f"{self.topic.madde_no}-{self.numara}: {self.metin[:50]}..."


class Question(models.Model):
    """Soru modeli - Konuya bağlı sorular"""
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='ornekler', verbose_name="Konu")
    numara = models.CharField(max_length=50, verbose_name="Numara", db_index=True)
    durum = models.TextField(verbose_name="Durum", blank=True)
    soru = models.TextField(verbose_name="Soru")
    siklar = models.JSONField(verbose_name="Şıklar", help_text="Şıklar listesi")
    dogru_cevap = models.TextField(verbose_name="Doğru Cevap")
    yorum = models.TextField(verbose_name="Yorum", blank=True)
    sayfa = models.IntegerField(verbose_name="Sayfa", default=1)
    order = models.IntegerField(verbose_name="Sıra", default=0, help_text="Konu içindeki sıra")
    
    class Meta:
        verbose_name = "Soru"
        verbose_name_plural = "Sorular"
        ordering = ['topic', 'order', 'numara']
        unique_together = [['topic', 'numara']]
    
    def __str__(self):
        return f"{self.topic.madde_no}-{self.numara}: {self.soru[:50]}..."


class UserAnswer(models.Model):
    """Kullanıcı cevapları modeli - Kullanıcının verdiği cevaplar"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='answers', verbose_name="Kullanıcı")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='user_answers', verbose_name="Soru")
    selected_answer = models.TextField(verbose_name="Seçilen Cevap")
    is_correct = models.BooleanField(verbose_name="Doğru mu?", default=False)
    answered_at = models.DateTimeField(auto_now_add=True, verbose_name="Cevaplanma Tarihi")
    
    class Meta:
        verbose_name = "Kullanıcı Cevabı"
        verbose_name_plural = "Kullanıcı Cevapları"
        unique_together = [['user', 'question']]
        ordering = ['-answered_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.question.numara} ({'✓' if self.is_correct else '✗'})"