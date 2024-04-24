from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from django.http import HttpResponseRedirect
from django.core.mail import send_mail
from .models import Cafe
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.exceptions import ValidationError 
from django.db.utils import IntegrityError



# Create your views here.
def home(request):
    cafes = Cafe.objects.all()
    return render(request, 'home.html', {'cafes': cafes})

def detalhes(request, cafe_id):
    cafe = get_object_or_404(Cafe, id=cafe_id)
    detalhes_cafe = cafe.detalhes()
    return render(request, 'detalhes.html', {'cafe': cafe, 'detalhes_cafe': detalhes_cafe})

@login_required
def favoritar(request, cafe_id):
    cafe = get_object_or_404(Cafe, id=cafe_id)
    
    if request.method == 'POST' or request.method == 'GET':
        usuario = request.user
        
        favorito_existente = Favorito.objects.filter(usuario=usuario, cafe=cafe).exists()
        
        if not favorito_existente:
            Favorito.objects.create(usuario=usuario, cafe=cafe)
            messages.success(request, 'Cafeteria favoritada com sucesso!')
            return HttpResponseRedirect(reverse('detalhes', args=[cafe_id]))
        else:
            favorito = Favorito.objects.filter(usuario=usuario, cafe=cafe).first()
            favorito.delete()  # Remove o favorito se existir
            messages.success(request, 'Cafeteria removida dos favoritos.')
            # return redirect('reverse('detalhes', args=[cafe_id])')
            return redirect('home')
        
    # return HttpResponseRedirect(reverse('detalhes', args=[cafe_id]))
    return redirect('home')

@login_required
def lista_favoritos(request):
    if request.user.is_authenticated:
        favoritos = Favorito.objects.filter(usuario=request.user)
        return render(request, 'apps/favoritos.html', {'favoritos': favoritos})
    else:
        return redirect('login')

def login_view(request):
    title = "Login"
    next_url = request.GET.get('next', '')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # return redirect(next_url or 'home')
            if request.POST.get('criar_conta'):
                tipo_usuario = request.POST.get('tipo_usuario')
                if tipo_usuario == 'cliente':
                    return redirect('cadastro_cliente')
                elif tipo_usuario == 'cafeteria':
                    return redirect('cadastro_cafeteria')
        else:
            return render(request, 'apps/login.html', {"erro": "Usuário não encontrado"})
    return render(request, 'apps/login.html', {'next': next_url})

@login_required
def enviar_whatsapp(request, cafe_id):
    cafeteria = get_object_or_404(Cafe, pk=cafe_id)
    if cafeteria.whatsapp:
        whatsapp_url = f"https://wa.me/{cafeteria.whatsapp}"
        return redirect(whatsapp_url)
    else:
        messages.error(request, "Número de WhatsApp não disponível.")
        return HttpResponseRedirect(reverse('perfil_cafeteria', args=[cafe_id]))

def enviar_email(request, cafe_id):
    cafeteria = get_object_or_404(Cafe, pk=cafe_id)
    if request.method == 'POST':
        mensagem = request.POST.get('mensagem', '')
        send_mail(
            'Mensagem do MyCafeApp',
            mensagem,
            'from@example.com',
            [cafeteria.email],
            fail_silently=False,
        )
        messages.success(request, "Email enviado com sucesso!")
        return render(request, 'email_enviado.html', {'cafeteria': cafeteria})
    return render(request, 'enviar_email.html', {'cafeteria': cafeteria})

def perfil_cafeteria(request, cafe_id):
    cafeteria = get_object_or_404(Cafe, pk=cafe_id)
    return render(request, 'perfil_cafeteria.html', {'cafeteria': cafeteria})

def logout(request):
    logout(request)
    if "usuario" in request.session:
        del request.session["usuario"]
    return redirect(home)

def cadastro_cafeteria(request):
    if request.method == 'POST':
    
        nome = request.POST.get('nome')
        endereco = request.POST.get('endereco')
        descricao = request.POST.get('descricao')
        email = request.POST.get('email')
        whatsapp = request.POST.get('whatsapp')
        horas_funcionamento = request.POST.get('horas_funcionamento')
        link_redesocial = request.POST.get('link_redesocial', '')  
        
        cafe = Cafe(
            nome=nome,
            endereco=endereco,
            descricao=descricao,
            email=email,
            whatsapp=whatsapp,
            horas_funcionamento=horas_funcionamento,
            link_redesocial=link_redesocial,
        )

        if 'foto_ambiente' in request.FILES:
            cafe.foto_ambiente = request.FILES['foto_ambiente']

        try:
            cafe.full_clean()
            cafe.save()
            return redirect('cadastro_cafeteria_sucesso.html')
        except ValidationError as e:
            return render(request, 'cadastro_cafeteria.html', {'errors': e.message_dict, 'form': request.POST})

    return render(request, 'cadastro_cafeteria.html')

def UserCadastro(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        nome_completo = request.POST.get('nome_completo')
        cpf = request.POST.get('cpf')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if UserCliente.objects.filter(username=username).exists():
            messages.error(request, 'Usuário já existe.')
            return render(request, 'cadastro_usuario.html')

        user = UserCliente(
            username=username,
            nome_completo=nome_completo,
            cpf=cpf,
            email=email,
            password=password
        )
        user.save()
        messages.success(request, 'Cadastro realizado com sucesso!')
        return redirect('home')  # Substitua 'home' pela URL de destino após o cadastro

    return render(request, 'cadastro_usuario.html')