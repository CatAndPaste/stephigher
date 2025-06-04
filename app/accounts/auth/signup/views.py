import random
import string
import datetime
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail, EmailMultiAlternatives
from django.contrib.auth import login as auth_login
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.utils import timezone

from .forms import Step1Form, Step2Form, Step3Form

from accounts.models import User, RegistrationAttempt


def signup_step1(request):
    old_reg_id = request.session.pop('reg_id', None)
    if old_reg_id:
        RegistrationAttempt.objects.filter(id=old_reg_id).delete()

    if request.method == 'POST':
        form = Step1Form(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']

            code = ''.join(random.choices(string.digits, k=6))
            attempt = RegistrationAttempt.objects.create(
                username=username,
                email=email,
                code=code
            )

            request.session['reg_id'] = str(attempt.id)

            text_body = render_to_string('email/signup/registration_code.txt', {
                'username': username,
                'code': code,
                'site_name': settings.SITE_NAME,
            })
            html_body = render_to_string('email/signup/registration_code.html', {
                'username': username,
                'code': code,
                'site_name': settings.SITE_NAME,
            })

            subject = "Подтверждение регистрации на StepHigher"
            from_email = settings.DEFAULT_FROM_EMAIL
            msg = EmailMultiAlternatives(subject, text_body, from_email, [email])
            msg.attach_alternative(html_body, "text/html")
            msg.send()

            return redirect('signup_verify')
    else:
        form = Step1Form()

    return render(request, 'accounts/auth/signup/step1.html', {'form': form})


def signup_step2(request):
    reg_id = request.session.get('reg_id')

    if not reg_id:
        messages.error(request, "Сначала введите имя пользователя и email")
        return redirect('signup')

    try:
        attempt = RegistrationAttempt.objects.get(id=reg_id)
    except RegistrationAttempt.DoesNotExist:
        messages.error(request, "Сессия истекла. Пожалуйста начните регистрацию заново")
        return redirect('signup')

    if attempt.is_expired():
        attempt.delete()
        request.session.pop('reg_id', None)
        messages.error(request, "Срок действия кода истёк. Пожалуйста начните регистрацию заново")
        return redirect('signup')

    if User.objects.filter(username__iexact=attempt.username).exists() or \
       User.objects.filter(email__iexact=attempt.email).exists():
        attempt.delete()
        request.session.pop('reg_id', None)
        messages.error(request, "Выбранные вами имя или email уже были заняты. Пожалуйста начните регистрацию заново")
        return redirect('signup')

    if request.method == 'POST':
        form = Step2Form(
            request.POST,
            session={ 'reg_code': attempt.code, 'reg_code_ts': attempt.created_at.timestamp() }
        )
        if form.is_valid():
            attempt.is_verified = True
            attempt.save(update_fields=['is_verified'])
            return redirect('signup_password')
    else:
        form = Step2Form(
            session={ 'reg_code': attempt.code, 'reg_code_ts': attempt.created_at.timestamp() }
        )

    return render(request, 'accounts/auth/signup/step2.html', {
        'form': form,
        'email': attempt.email
    })


def signup_step3(request):
    reg_id = request.session.get('reg_id')
    if not reg_id:
        messages.error(request, "Сначала введите имя пользователя и email")
        return redirect('signup')

    try:
        attempt = RegistrationAttempt.objects.get(id=reg_id)
    except RegistrationAttempt.DoesNotExist:
        messages.error(request, "Сессия истекла. Пожалуйста начните регистрацию заново")
        return redirect('signup')

    if attempt.is_expired() or not attempt.is_verified:
        attempt.delete()
        request.session.pop('reg_id', None)
        messages.error(request, "Сессия истекла. Пожалуйста начните регистрацию заново")
        return redirect('signup')

    if User.objects.filter(username__iexact=attempt.username).exists() or \
       User.objects.filter(email__iexact=attempt.email).exists():
        attempt.delete()
        request.session.pop('reg_id', None)
        messages.error(request, "Выбранные вами имя или email уже были заняты. Пожалуйста начните регистрацию заново")
        return redirect('signup')

    if request.method == 'POST':
        form = Step3Form(request.POST)
        if form.is_valid():
            password = form.save()

            try:
                user = User.objects.create_user(
                    username=attempt.username,
                    email=attempt.email,
                    password=password
                )
            except IntegrityError:
                messages.error(request, "Не удалось завершить регистрацию: выбранные вами имя или email уже "
                                        "были заняты. Пожалуйста попробуйте ещё раз")
                return redirect('signup')

            attempt.delete()
            request.session.pop('reg_id', None)

            messages.success(request, "Регистрация прошла успешно! Вы можете войти")
            return redirect('login')
    else:
        form = Step3Form()

    return render(request, 'accounts/auth/signup/step3.html', {
        'form': form
    })
