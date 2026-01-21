"""
Django management command to load questions from questions.json
Railway'de çalıştırmak için: python manage.py load_questions
"""
import json
import os
from django.core.management.base import BaseCommand
from django.db import transaction
from accounts.models import Topic, Explanation, Question


class Command(BaseCommand):
    help = 'questions.json dosyasından soruları yükler'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='questions.json',
            help='Yüklenecek JSON dosyasının yolu (varsayılan: questions.json)',
        )

    def handle(self, *args, **options):
        file_path = options['file']
        
        # Dosya yolunu BASE_DIR'e göre ayarla
        if not os.path.isabs(file_path):
            from django.conf import settings
            file_path = os.path.join(settings.BASE_DIR, file_path)
        
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'Dosya bulunamadı: {file_path}'))
            return
        
        self.stdout.write(self.style.SUCCESS(f'Dosya okunuyor: {file_path}'))
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Dosya okunamadı: {e}'))
            return
        
        self.stdout.write(self.style.SUCCESS(f'{len(data)} konu bulundu'))
        
        with transaction.atomic():
            topic_count = 0
            explanation_count = 0
            question_count = 0
            
            for idx, topic_data in enumerate(data):
                madde_no = topic_data.get('madde_no', '')
                baslik = topic_data.get('baslik', '')
                sayfa = topic_data.get('sayfa', 1)
                
                # Topic oluştur veya güncelle
                topic, created = Topic.objects.get_or_create(
                    madde_no=madde_no,
                    defaults={
                        'baslik': baslik,
                        'sayfa': sayfa,
                        'order': idx
                    }
                )
                
                if not created:
                    # Mevcut topic'i güncelle
                    topic.baslik = baslik
                    topic.sayfa = sayfa
                    topic.order = idx
                    topic.save()
                
                if created:
                    topic_count += 1
                
                # Açıklamaları yükle
                aciklamalar = topic_data.get('aciklamalar', [])
                for aciklama_data in aciklamalar:
                    numara = aciklama_data.get('numara', '')
                    metin = aciklama_data.get('metin', '')
                    aciklama_sayfa = aciklama_data.get('sayfa', sayfa)
                    
                    explanation, created = Explanation.objects.get_or_create(
                        topic=topic,
                        numara=numara,
                        defaults={
                            'metin': metin,
                            'sayfa': aciklama_sayfa
                        }
                    )
                    
                    if not created:
                        explanation.metin = metin
                        explanation.sayfa = aciklama_sayfa
                        explanation.save()
                    
                    if created:
                        explanation_count += 1
                
                # Soruları yükle
                ornekler = topic_data.get('ornekler', [])
                for q_idx, ornek_data in enumerate(ornekler):
                    numara = ornek_data.get('numara', '')
                    durum = ornek_data.get('durum', '')
                    soru = ornek_data.get('soru', '')
                    siklar = ornek_data.get('siklar', [])
                    dogru_cevap = ornek_data.get('dogru_cevap', '')
                    yorum = ornek_data.get('yorum', '')
                    soru_sayfa = ornek_data.get('sayfa', sayfa)
                    
                    question, created = Question.objects.get_or_create(
                        topic=topic,
                        numara=numara,
                        defaults={
                            'durum': durum,
                            'soru': soru,
                            'siklar': siklar,
                            'dogru_cevap': dogru_cevap,
                            'yorum': yorum,
                            'sayfa': soru_sayfa,
                            'order': q_idx
                        }
                    )
                    
                    if not created:
                        question.durum = durum
                        question.soru = soru
                        question.siklar = siklar
                        question.dogru_cevap = dogru_cevap
                        question.yorum = yorum
                        question.sayfa = soru_sayfa
                        question.order = q_idx
                        question.save()
                    
                    if created:
                        question_count += 1
            
            summary = (
                f'\nYukleme tamamlandi:\n'
                f'  - {topic_count} yeni konu\n'
                f'  - {explanation_count} yeni aciklama\n'
                f'  - {question_count} yeni soru'
            )
            self.stdout.write(self.style.SUCCESS(summary))
