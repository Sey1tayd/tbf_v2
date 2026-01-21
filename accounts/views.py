from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Case, When, IntegerField
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
from .models import CustomUser, Topic, Question, UserAnswer


def login_view(request):
    """Login sayfası - kullanıcı listesi ve giriş formu"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    # Tüm kullanıcıları getir (normal + admin)
    normal_users = CustomUser.objects.filter(is_staff=False, is_superuser=False).order_by('first_name', 'last_name')
    admin_users = CustomUser.objects.filter(Q(is_staff=True) | Q(is_superuser=True)).order_by('first_name', 'last_name')
    users = list(normal_users) + list(admin_users)
    
    # Admin kullanıcıların bilgilerini JSON olarak hazırla
    admin_usernames = {user.username for user in admin_users}
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        
        if not username:
            messages.error(request, 'Lütfen bir kullanıcı seçiniz!')
            return render(request, 'accounts/login.html', {
                'users': users,
                'admin_usernames': admin_usernames
            })
        
        try:
            user = CustomUser.objects.get(username=username)
            
            # Normal kullanıcılar için şifre gerekmez
            if not user.is_staff and not user.is_superuser:
                login(request, user)
                return redirect('dashboard')
            # Admin kullanıcılar için şifre gerekli
            elif user.is_staff or user.is_superuser:
                if password:
                    user = authenticate(request, username=username, password=password)
                    if user is not None:
                        login(request, user)
                        return redirect('admin_home')
                    else:
                        messages.error(request, 'Şifre hatalı!')
                else:
                    messages.error(request, 'Admin kullanıcılar için şifre gereklidir!')
        except CustomUser.DoesNotExist:
            messages.error(request, 'Kullanıcı bulunamadı!')
    
    return render(request, 'accounts/login.html', {
        'users': users,
        'admin_usernames': admin_usernames
    })


@login_required
def dashboard_view(request):
    """Normal kullanıcı ana sayfası (kutucuklu)"""
    # Admin kullanıcılar yanlışlıkla buraya düşerse admin ana sayfasına atalım
    if request.user.is_staff or request.user.is_superuser:
        return redirect('admin_home')
    return render(request, 'accounts/dashboard.html', {'user': request.user})


@login_required
def pdfs_view(request):
    """PDF görüntüleme ve indirme sayfası"""
    if request.user.is_staff or request.user.is_superuser:
        return redirect('admin_home')
    
    pdfs = [
        {
            'name': 'Basketbol Oyun Kuralları Resmi Yorumlar',
            'filename': 'basketbol-oyun-kurallari-resmi-yorumlar.pdf',
            'url': '/media/pdfs/basketbol-oyun-kurallari-resmi-yorumlar.pdf'
        },
        {
            'name': 'Basketbol Oyun Kuralları Değişiklikleri 2024',
            'filename': 'basketbol-oyun-kurallari-degisiklikleri2024.pdf',
            'url': '/media/pdfs/basketbol-oyun-kurallari-degisiklikleri2024.pdf'
        },
        {
            'name': 'Basketbol Oyun Kuralları 2024',
            'filename': 'basketbol-oyun-kurallari-2024.pdf',
            'url': '/media/pdfs/basketbol-oyun-kurallari-2024.pdf'
        }
    ]
    
    return render(request, 'accounts/pdfs.html', {
        'user': request.user,
        'pdfs': pdfs
    })


@login_required
def ekolarka_sorular_view(request):
    """Ekolarka Yorum Soruları sayfası"""
    if request.user.is_staff or request.user.is_superuser:
        return redirect('admin_home')
    
    # Tüm konuları getir (sorularıyla birlikte)
    topics = Topic.objects.prefetch_related('ornekler').annotate(
        question_count=Count('ornekler')
    ).order_by('order', 'madde_no')
    
    # Kullanıcının cevaplarını getir
    user_answers = UserAnswer.objects.filter(user=request.user).select_related('question')
    answered_question_ids = {answer.question_id for answer in user_answers}
    
    # Her konu için kullanıcının cevapladığı soru sayısını hesapla
    for topic in topics:
        topic_questions = topic.ornekler.all()
        topic.answered_count = sum(1 for q in topic_questions if q.id in answered_question_ids)
        topic.total_count = topic.question_count
    
    return render(request, 'accounts/ekolarka_sorular.html', {
        'user': request.user,
        'topics': topics
    })


@login_required
def gunluk_soru_view(request):
    """Günlük Soru sayfası (placeholder)"""
    if request.user.is_staff or request.user.is_superuser:
        return redirect('admin_home')
    return render(request, 'accounts/gunluk_soru.html', {'user': request.user})


def _require_admin(request):
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'Bu sayfa için yetkiniz yok!')
        return False
    return True


@login_required
def admin_home_view(request):
    """Yönetim paneli ana sayfa (kutucuklar)"""
    if not _require_admin(request):
        return redirect('dashboard')
    return render(request, 'accounts/admin_home.html', {'user': request.user})


@login_required
def user_management_view(request):
    """Kullanıcı İşlemleri (liste/ekle/sil)"""
    if not _require_admin(request):
        return redirect('dashboard')

    all_users = CustomUser.objects.filter(is_staff=False, is_superuser=False).order_by('first_name', 'last_name')
    admin_users = CustomUser.objects.filter(Q(is_staff=True) | Q(is_superuser=True)).order_by('first_name', 'last_name')

    return render(request, 'accounts/user_management.html', {
        'user': request.user,
        'all_users': all_users,
        'admin_users': admin_users,
    })


@login_required
def add_user_view(request):
    """Kullanıcı ekle"""
    if not _require_admin(request):
        return redirect('dashboard')
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        username_input = request.POST.get('username', '').strip()
        make_admin = request.POST.get('make_admin') == 'on'
        
        # Validasyon kontrolleri
        if not first_name or not last_name:
            messages.error(request, 'Lütfen isim ve soyisim alanlarını doldurun!')
            return redirect('user_management')
        
        if len(first_name) > 150:
            messages.error(request, 'İsim alanı en fazla 150 karakter olabilir!')
            return redirect('user_management')
        
        if len(last_name) > 150:
            messages.error(request, 'Soyisim alanı en fazla 150 karakter olabilir!')
            return redirect('user_management')
        
        # Kullanıcı adı belirlenmesi
        if username_input:
            # Manuel girilen kullanıcı adı
            username = username_input
            
            # Username validasyonu
            if len(username) > 150:
                messages.error(request, 'Kullanıcı adı en fazla 150 karakter olabilir!')
                return redirect('user_management')
            
            # Kullanıcı adının unique olup olmadığını kontrol et
            if CustomUser.objects.filter(username=username).exists():
                messages.error(request, f'"{username}" kullanıcı adı zaten kullanılıyor!')
                return redirect('user_management')
        else:
            # Otomatik kullanıcı adı oluştur
            base_username = f"{first_name.lower()}.{last_name.lower()}"
            # Türkçe karakterleri düzelt
            replacements = {
                'ç': 'c', 'ğ': 'g', 'ı': 'i', 'ö': 'o', 'ş': 's', 'ü': 'u',
                'Ç': 'C', 'Ğ': 'G', 'İ': 'I', 'Ö': 'O', 'Ş': 'S', 'Ü': 'U'
            }
            for tr_char, en_char in replacements.items():
                base_username = base_username.replace(tr_char, en_char)
            base_username = base_username.replace(' ', '')
            
            username = base_username
            counter = 1
            while CustomUser.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            
            try:
                user = CustomUser.objects.create_user(
                    username=username,
                    first_name=first_name,
                    last_name=last_name,
                    password='123456'  # Varsayılan şifre
                )
                if make_admin:
                    user.is_staff = True
                    user.is_superuser = True
                    user.save()
                messages.success(request, f'{first_name} {last_name} ({username}) başarıyla eklendi!')
            except ValueError as e:
                messages.error(request, f'Geçersiz değer: {str(e)}')
            except Exception as e:
                messages.error(request, f'Kullanıcı eklenirken bir hata oluştu: {str(e)}')
    
    return redirect('user_management')


@login_required
def delete_user_view(request, user_id):
    """Kullanıcı sil"""
    if not _require_admin(request):
        return redirect('dashboard')
    
    # Sadece POST metodu kabul et
    if request.method != 'POST':
        messages.error(request, 'Geçersiz istek metodu!')
        return redirect('user_management')
    
    user = get_object_or_404(CustomUser, id=user_id)
    
    # Kendini silmesini engelle
    if user.id == request.user.id:
        messages.error(request, 'Kendi hesabınızı silemezsiniz!')
        return redirect('user_management')
    
    # Son admin kullanıcının silinmesini engelle
    if user.is_staff or user.is_superuser:
        admin_count = CustomUser.objects.filter(Q(is_staff=True) | Q(is_superuser=True)).count()
        if admin_count <= 1:
            messages.error(request, 'Sistemde en az bir admin kullanıcı bulunmalıdır!')
            return redirect('user_management')
    
    user_name = f"{user.first_name} {user.last_name}"
    user.delete()
    messages.success(request, f'{user_name} başarıyla silindi!')
    
    return redirect('user_management')


def logout_view(request):
    """Çıkış yap"""
    logout(request)
    return redirect('login')


# API Endpoints for Questions

@login_required
@require_http_methods(["GET"])
def api_get_question(request, question_id):
    """Belirli bir soruyu getir"""
    if request.user.is_staff or request.user.is_superuser:
        return JsonResponse({'error': 'Admin kullanıcılar bu sayfayı kullanamaz'}, status=403)
    
    try:
        question = Question.objects.select_related('topic').get(id=question_id)
        
        # Kullanıcının bu soruya verdiği cevabı kontrol et
        user_answer = UserAnswer.objects.filter(
            user=request.user,
            question=question
        ).first()
        
        # Önceki ve sonraki soruları bul
        all_questions = list(Question.objects.filter(topic=question.topic).order_by('order', 'numara').values_list('id', flat=True))
        current_index = all_questions.index(question.id) if question.id in all_questions else -1
        
        prev_question_id = all_questions[current_index - 1] if current_index > 0 else None
        next_question_id = all_questions[current_index + 1] if current_index < len(all_questions) - 1 else None
        
        # Aynı konudaki diğer soruları bul
        topic_questions = Question.objects.filter(topic=question.topic).order_by('order', 'numara')
        
        response_data = {
            'question': {
                'id': question.id,
                'numara': question.numara,
                'durum': question.durum,
                'soru': question.soru,
                'siklar': question.siklar,
                'dogru_cevap': question.dogru_cevap,
                'sayfa': question.sayfa,
                'topic': {
                    'id': question.topic.id,
                    'madde_no': question.topic.madde_no,
                    'baslik': question.topic.baslik
                }
            },
            'user_answer': {
                'selected_answer': user_answer.selected_answer if user_answer else None,
                'is_correct': user_answer.is_correct if user_answer else None,
                'answered_at': user_answer.answered_at.isoformat() if user_answer else None
            },
            'yorum': question.yorum if user_answer else None,
            'navigation': {
                'prev_question_id': prev_question_id,
                'next_question_id': next_question_id,
                'current_index': current_index + 1,
                'total_in_topic': len(all_questions)
            },
            'topic_questions': [
                {
                    'id': q.id,
                    'numara': q.numara,
                    'answered': UserAnswer.objects.filter(user=request.user, question=q).exists(),
                    'is_correct': UserAnswer.objects.filter(user=request.user, question=q).values_list('is_correct', flat=True).first()
                }
                for q in topic_questions
            ]
        }
        
        return JsonResponse(response_data)
    except Question.DoesNotExist:
        return JsonResponse({'error': 'Soru bulunamadı'}, status=404)


@login_required
@require_http_methods(["POST"])
def api_submit_answer(request, question_id):
    """Kullanıcının cevabını kaydet"""
    if request.user.is_staff or request.user.is_superuser:
        return JsonResponse({'error': 'Admin kullanıcılar bu sayfayı kullanamaz'}, status=403)
    
    try:
        question = Question.objects.get(id=question_id)
        data = json.loads(request.body)
        selected_answer = data.get('selected_answer', '').strip()
        
        if not selected_answer:
            return JsonResponse({'error': 'Cevap seçilmedi'}, status=400)
        
        # Doğru cevabı kontrol et
        is_correct = (selected_answer == question.dogru_cevap)
        
        # Cevabı kaydet veya güncelle
        user_answer, created = UserAnswer.objects.update_or_create(
            user=request.user,
            question=question,
            defaults={
                'selected_answer': selected_answer,
                'is_correct': is_correct
            }
        )
        
        return JsonResponse({
            'success': True,
            'is_correct': is_correct,
            'correct_answer': question.dogru_cevap,
            'yorum': question.yorum,
            'created': created
        })
    except Question.DoesNotExist:
        return JsonResponse({'error': 'Soru bulunamadı'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Geçersiz JSON'}, status=400)


@login_required
@require_http_methods(["GET"])
def api_get_topics(request):
    """Tüm konuları ve ilerleme durumunu getir"""
    if request.user.is_staff or request.user.is_superuser:
        return JsonResponse({'error': 'Admin kullanıcılar bu sayfayı kullanamaz'}, status=403)
    
    topics = Topic.objects.prefetch_related('ornekler').annotate(
        question_count=Count('ornekler')
    ).order_by('order', 'madde_no')
    
    # Kullanıcının cevaplarını getir
    user_answers = UserAnswer.objects.filter(user=request.user).select_related('question')
    answered_question_ids = {answer.question_id for answer in user_answers}
    
    topics_data = []
    for topic in topics:
        topic_questions = list(topic.ornekler.all().order_by('order', 'numara'))
        answered_count = sum(1 for q in topic_questions if q.id in answered_question_ids)
        
        topics_data.append({
            'id': topic.id,
            'madde_no': topic.madde_no,
            'baslik': topic.baslik,
            'sayfa': topic.sayfa,
            'total_questions': len(topic_questions),
            'answered_questions': answered_count,
            'questions': [
                {
                    'id': q.id,
                    'numara': q.numara,
                    'answered': q.id in answered_question_ids,
                    'is_correct': next((a.is_correct for a in user_answers if a.question_id == q.id), None)
                }
                for q in topic_questions
            ]
        })
    
    return JsonResponse({'topics': topics_data})


@login_required
@require_http_methods(["GET"])
def api_get_progress(request):
    """Kullanıcının genel ilerleme durumunu getir"""
    if request.user.is_staff or request.user.is_superuser:
        return JsonResponse({'error': 'Admin kullanıcılar bu sayfayı kullanamaz'}, status=403)
    
    total_questions = Question.objects.count()
    answered_questions = UserAnswer.objects.filter(user=request.user).count()
    correct_answers = UserAnswer.objects.filter(user=request.user, is_correct=True).count()
    wrong_answers = answered_questions - correct_answers
    
    return JsonResponse({
        'total_questions': total_questions,
        'answered_questions': answered_questions,
        'correct_answers': correct_answers,
        'wrong_answers': wrong_answers,
        'progress_percentage': round((answered_questions / total_questions * 100) if total_questions > 0 else 0, 2)
    })
