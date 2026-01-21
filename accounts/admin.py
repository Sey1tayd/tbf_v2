from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Topic, Question, Explanation, UserAnswer


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('madde_no', 'baslik', 'sayfa', 'order')
    list_filter = ('sayfa',)
    search_fields = ('madde_no', 'baslik')
    ordering = ('order', 'madde_no')


@admin.register(Explanation)
class ExplanationAdmin(admin.ModelAdmin):
    list_display = ('topic', 'numara', 'sayfa')
    list_filter = ('topic', 'sayfa')
    search_fields = ('numara', 'metin')
    ordering = ('topic', 'numara')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('numara', 'topic', 'sayfa', 'order')
    list_filter = ('topic', 'sayfa')
    search_fields = ('numara', 'soru', 'durum')
    ordering = ('topic', 'order', 'numara')
    readonly_fields = ('numara', 'topic')


@admin.register(UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin):
    list_display = ('user', 'question', 'is_correct', 'answered_at')
    list_filter = ('is_correct', 'answered_at')
    search_fields = ('user__username', 'question__numara', 'question__soru')
    ordering = ('-answered_at',)
    readonly_fields = ('answered_at',)
