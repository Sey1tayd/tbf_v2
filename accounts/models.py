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
