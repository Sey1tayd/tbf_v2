"""
Django management command to create all users
Railway'de çalıştırmak için: python manage.py create_all_users
"""
from django.core.management.base import BaseCommand
from accounts.models import CustomUser

# Kullanıcı listesi
USER_NAMES = [
    "ABDULLAH ÇİFTCİ",
    "ABDULLAH KOPUTAN",
    "AHMET KEMAL DİGİLLİ",
    "AHMET TOPAL",
    "ALİ EREN ÖZDEMİR",
    "ALPER GÖÇER",
    "ALPER RASİM KÜÇÜKSÜLE",
    "ANIL VEZİROĞLU",
    "ARDA ORHAN",
    "AYKUT ÇETİN",
    "AYŞENUR ELİBOL",
    "BAHADIR CEYLAN",
    "BAYRAM DÜZ",
    "BELİNAY KAPTAN",
    "BETÜL KOSTAK",
    "BEYTULLAH KARTAL",
    "BEYZA DİLARA ERBEK",
    "BEYZA ŞALVARCI",
    "BEYZA ZÜHRE YONCALIK",
    "BÜŞRA AVCI",
    "BÜŞRA ERKAN",
    "DİLARA VEZİROĞLU",
    "DURU ERTAŞ",
    "EFE BERKİN HOROZOĞLU",
    "EGE ÖZPOLAT",
    "ELMAS SELCEN DERMAN",
    "EMİNE ALTUNTAŞ",
    "EMİNE DOĞA DOĞAN",
    "EMİNE YILMAZ",
    "EMİRCAN TEKE",
    "EMRE ERYILMAZ",
    "EMRE ÖZBAŞ",
    "EMRE SAĞLIK",
    "EMRE TUNALI",
    "ERCAN ÇEKMEN",
    "ESİLA YILMAZ",
    "ESMA ÇAKICI",
    "FATİH BAHÇIVAN",
    "FATMANUR GÖK",
    "FURKAN KIZILAY",
    "FURKAN YEŞİL",
    "GAMZE NUR AYDIN",
    "HALDUN ÇOBAN",
    "HAMİ KERİM SEZER",
    "HARUN HORTU",
    "HATİCE MERVE KELEŞ",
    "HEDİYE BALIKCI",
    "İKBAL ÖZDEMİR",
    "İLKNUR NAZMİYE ÜNÜVAR",
    "MEHMET BÜYÜKTÜRK",
    "MEHMET ÇELİK",
    "MEHMET TALHA ÇELİK",
    "MELİKE EL",
    "MERVE ÖZARSLAN",
    "MUHAMMED ALİ ÖKSÜZOĞLU",
    "MUHAMMET KADİR AKGÜL",
    "MUHSİN AYHAN",
    "MUSA KAZIM ÇETİN",
    "MUSA ORHAN",
    "MUSTAFA HARTÜN",
    "MUSTAFA SERİN",
    "NİLAY GÖKÇE",
    "ORHAN ŞAHİN",
    "OSMAN BARDAKÇI",
    "OSMAN GÜVEN",
    "OSMAN KESER",
    "OSMAN SARIKAYA",
    "ÖMER FARUK SARI",
    "ÖMER GÜLŞEN",
    "ÖZGE SARI",
    "PELİN ÖZBAŞ",
    "RIDVAN TETİK",
    "ROJİN YANIK",
    "RUKİYE YILDIRIM",
    "SADETTİN YAMAN",
    "SAMİ ADAK",
    "SAYİME YALÇIN",
    "SEÇİL DOĞRU",
    "SEFA KELEŞ",
    "SELENAY IŞIK",
    "SELMA ORUÇ",
    "SELMAN BELGEN",
    "SEMİH MUAMMER EDİRNELİGİL",
    "SEYİT ALİ AYDIN",
    "SEYİT İŞ",
    "SEYİT YAĞIZ ERTOP",
    "SIDIKA HALE ÖZTÜRK",
    "SUDE MERT",
    "ŞENAY BÜYÜKER",
    "TANER GÜNER",
    "UFUK UMUTLU",
    "VAHTİ ALADAĞLI",
    "YASİN KESİK",
    "YAVUZ YILDIZ",
    "YİĞİT EMRE ŞİMŞEK",
    "YİĞİT ERDİNÇ",
    "YUNUS SERT",
    "YUSUF ASLANTAŞ",
    "ZEYNEP YELİ",
    "ZÜBEYDE NİSA KAPTAN",
]


class Command(BaseCommand):
    help = 'Tüm kullanıcıları ve admin kullanıcısını oluşturur'

    def create_username(self, first_name, last_name, existing_usernames):
        """Benzersiz kullanıcı adı oluştur"""
        # İlk deneme: isim.soyisim (küçük harf, Türkçe karakterler düzeltilmiş)
        base_username = f"{first_name.lower()}.{last_name.lower()}"
        # Türkçe karakterleri düzelt
        replacements = {
            'ç': 'c', 'ğ': 'g', 'ı': 'i', 'ö': 'o', 'ş': 's', 'ü': 'u',
            'Ç': 'C', 'Ğ': 'G', 'İ': 'I', 'Ö': 'O', 'Ş': 'S', 'Ü': 'U'
        }
        for tr_char, en_char in replacements.items():
            base_username = base_username.replace(tr_char, en_char)
        
        # Boşlukları kaldır
        base_username = base_username.replace(' ', '')
        
        username = base_username
        counter = 1
        
        # Eğer kullanıcı adı zaten varsa numara ekle
        while username in existing_usernames:
            username = f"{base_username}{counter}"
            counter += 1
        
        return username

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Kullanıcılar oluşturuluyor...'))
        
        existing_usernames = set(CustomUser.objects.values_list('username', flat=True))
        created_count = 0
        skipped_count = 0
        
        for full_name in USER_NAMES:
            # İsim ve soyisimi ayır (son kelime soyisim, geri kalanı isim)
            parts = full_name.strip().split()
            if len(parts) < 2:
                self.stdout.write(self.style.WARNING(f"Uyarı: '{full_name}' geçersiz format, atlanıyor..."))
                continue
            
            last_name = parts[-1]
            first_name = ' '.join(parts[:-1])
            
            # Kullanıcı adı oluştur
            username = self.create_username(first_name, last_name, existing_usernames)
            existing_usernames.add(username)
            
            # Kullanıcı zaten var mı kontrol et (isim ve soyisim ile)
            existing_user = CustomUser.objects.filter(
                first_name=first_name,
                last_name=last_name
            ).first()
            
            if existing_user:
                self.stdout.write(self.style.WARNING(f"Atlandı: {full_name} (zaten mevcut)"))
                skipped_count += 1
                continue
            
            # Yeni kullanıcı oluştur
            try:
                user = CustomUser.objects.create_user(
                    username=username,
                    first_name=first_name,
                    last_name=last_name,
                    password='123456'  # Varsayılan şifre
                )
                self.stdout.write(self.style.SUCCESS(f"Oluşturuldu: {full_name} (kullanıcı adı: {username})"))
                created_count += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Hata: {full_name} oluşturulamadı - {e}"))
        
        self.stdout.write(self.style.SUCCESS(f'\nToplam: {created_count} kullanıcı oluşturuldu, {skipped_count} kullanıcı atlandı'))
        
        # Superuser oluştur
        self.stdout.write(self.style.SUCCESS('\nSuperuser oluşturuluyor...'))
        if CustomUser.objects.filter(username='S3Y1T').exists():
            self.stdout.write("Superuser 'S3Y1T' zaten mevcut, güncelleniyor...")
            superuser = CustomUser.objects.get(username='S3Y1T')
            superuser.set_password('Aydin2580')
            superuser.is_superuser = True
            superuser.is_staff = True
            superuser.save()
            self.stdout.write(self.style.SUCCESS("Superuser güncellendi! (Şifre: Aydin2580)"))
        else:
            try:
                superuser = CustomUser.objects.create_superuser(
                    username='S3Y1T',
                    password='Aydin2580',
                    first_name='Seyit',
                    last_name='Aydin'
                )
                self.stdout.write(self.style.SUCCESS("Superuser 'S3Y1T' oluşturuldu! (Şifre: Aydin2580)"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Superuser oluşturulurken hata: {e}"))
