from time import localtime, strftime, time
from datetime import datetime, date, timedelta
from sys import exc_info
import traceback
from json import dumps
import requests
from requests.exceptions import RequestException
import numpy as np
import csv
from pandas_datareader import data as pd_data
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, View
from django.views.generic.edit import CreateView, DeleteView, UpdateView, SingleObjectMixin
from .models import Ativos, SwingTrade, DayTrade, Conta, Pagamento, Receita, HistoricoAtivo
from .forms import AtivoForm, DayForm, SwingForm, UserForm, ContaForm, PagamentoForm, ReceitaForm
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.conf import settings

def login_detail(request):
    ''' Metódo que autentica usuário no sistema
        Recebe uname1 e pwd1 com argumentos.
    '''
    print("chamei login detail")
    if  request.method == 'POST':
        username = request.POST['uname1']
        password = request.POST['pwd1']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('core:index')
        else:
            return render(request, 'core/login.html', {'error_message' : 'Usuário e senha inválidos.'})
    else:
        if request.user.is_authenticated:
            return redirect('core:index')
        else:
            return render( request,'core/login.html')

@login_required
def index_page(request):
    ''' Define path do index.
    '''
    return render(request, 'core/index.html')

#User
class UserView(View):
    form_class = UserForm
    template_name = 'core/login.html'

    #sobrescreve método get
    def get(self, request):
        form = UserForm
        return render(request, self.template_name, {'form' : form})

    #Mostra usuário instanciado.
    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)

            if user is not None:
                if user.active:
                    login(request, user)
                    render(request, 'core/index.html')
                else:
                    render(request, 'core/login.html')
        else:
            render(request, 'core/login.html')


# Listas
#@method_decorator(login_required, name='dispatch')
class AtivosListView(LoginRequiredMixin, ListView):
    ''' View da lista de ativos. Ordenado pelo código
    '''
    template_name = 'core/ativo_list.html'
    model = Ativos
    context_object_name = 'ativos_list'
    queryset = Ativos.objects.all().order_by('codigo')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        count_ativos = Ativos.objects.all().count()
        context['quantidade_ativos'] = count_ativos
        return context

#@method_decorator(login_required, name='dispatch')
class SwingListView(LoginRequiredMixin, ListView):
    ''' View da lista de operações swingtrades
    '''
    template_name = 'core/swing_list.html'
    model = SwingTrade
    context_object_name = 'swing_list'

    def get_context_data(self, *args, **kwargs):
        ''' Filtrar operação day trade por mês
        '''
        
        context = super().get_context_data(**kwargs)
        if self.request.method == 'GET':
            get_paramenters = dict(self.request.GET)
            if 'mes' in get_paramenters and 'ano' in get_paramenters:
                lista_swing_trade = SwingTrade.objects.filter(data_acao__month=get_paramenters['mes'][0],  
                                                              data_acao__year=get_paramenters['ano'][0]).order_by('data_acao')
                context['swing_list'] = lista_swing_trade
            return context
        else:
            context['swing_list'] = SwingTrade.objects.all().order_by('data_acao')
            return context

#@method_decorator(login_required, name='dispatch')
class DayListView(ListView):
    ''' Classe que traz a lista de day trade.
        GET - Parametros no get de mês e ano.
        Default é o mês corrente.
    '''
    template_name = 'core/day_list.html'
    model = DayTrade
    context_object_name = 'day_list'

    def get_context_data(self, *args, **kwargs):
        ''' Filtrar operação day trade por mês
        '''
        context = super().get_context_data(**kwargs)
        if self.request.method == 'GET':
            get_paramenters = dict(self.request.GET)
            if 'mes' in get_paramenters and 'ano' in get_paramenters:
                if get_paramenters['mes'][0] != '0':
                    lista_day_trade = DayTrade.objects.filter(data_acao__month=get_paramenters['mes'][0], 
                                                              data_acao__year=get_paramenters['ano'][0]).order_by('data_acao')
                    context['day_list'] = lista_day_trade
                    return context
                else:
                    lista_day_trade = DayTrade.objects.filter(data_acao__year=get_paramenters['ano'][0]).order_by('data_acao')
                    context['day_list'] = lista_day_trade
                    return context
            else:
                mes_atual = datetime.today().month
                ano_atual = datetime.today().year
                context['day_list'] = DayTrade.objects.filter(data_acao__month=mes_atual, data_acao__year=ano_atual).order_by('data_acao')
                return context
   
            

class ContaList(ListView):
    ''' View que mostra as contas cadastradas
    '''

    template_name = 'core/conta_list.html'
    model = Conta
    context_object_name = 'conta_list'
    queryset = Conta.objects.all().order_by('dia_vencimento')

class PagamentoList(ListView):
    ''' View que mostra a lista de pagamentos feitos no mês.
        GET - Recebe mês e ano como parâmetro.
    '''

    template_name = 'core/pagamento_list.html'
    model = Pagamento
    queryset = Pagamento.objects.all().order_by('data_pagamento')

    def get_context_data(self, *args, **kwargs):
        ''' Filtrar pagamento pelo mês
        '''

        context = super().get_context_data(**kwargs)
        if self.request.method == 'GET':
            get_paramenters = dict(self.request.GET)
            if 'mes' in get_paramenters and 'ano' in get_paramenters:
                lista_conta_pendente = []
                lista_contas = Conta.objects.all()
                for conta in lista_contas:
                    if Pagamento.objects.filter(mes_vigente=get_paramenters['mes'][0],
                                                ano_vigente=get_paramenters['ano'][0], conta=conta.id).exists():                     
                        continue
                    else:
                        lista_conta_pendente.append(conta)
                context['contas_pendente'] = lista_conta_pendente
                context['object_list'] = Pagamento.objects.filter(mes_vigente=get_paramenters['mes'][0],
                                                                    ano_vigente=get_paramenters['ano'][0]).order_by('data_pagamento')
                return context
            else:
                mes_atual = datetime.today().month
                ano_atual = datetime.today().year
                lista_conta_pendente = []
                lista_contas = Conta.objects.all()
                for conta in lista_contas:
                    if Pagamento.objects.filter(mes_vigente=mes_atual, ano_vigente=ano_atual, conta=conta.id).exists():    
                        continue
                    else:
                        lista_conta_pendente.append(conta)
                context['contas_pendente'] = lista_conta_pendente
                context['object_list'] = Pagamento.objects.filter(mes_vigente=mes_atual, ano_vigente=ano_atual).order_by('data_pagamento')
                return context

class ReceitaList(ListView):
    ''' View que lista demais receitas
    '''
    template_name = 'core/receita_list.html'
    model = Receita
    queryset = Receita.objects.all().order_by('data_receita')

# Detail
#@method_decorator(login_required, name='dispatch')
class AtivosDetail(DetailView):
    ''' View que mostra detalhes de um ativo pelo seu ID
    '''

    template_name = 'core/ativo_detail.html'
    model = Ativos
    form_class = AtivoForm
    slug_field = 'codigo'
    slug_url_kwarg = 'codigo'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['historico'] = HistoricoAtivo.objects.filter(ativo=self.get_object()).order_by('-data')
        return context

#@method_decorator(login_required, name='dispatch')
class SwingDetail(DetailView):
    template_name = 'core/swing_detail.html'
    model = SwingTrade
    form_class = SwingForm
    pk_url_kwarg = 'swing_id'

class DayDetail(DetailView):
    template_name = 'core/day_detail.html'
    model = DayTrade
    form_class = DayForm
    pk_url_kwarg = 'day_id'

#@method_decorator(login_required, name='dispatch')
class PagamentoDetail(DetailView):
    template_name = 'core/pagamento_detail.html'
    model = Pagamento
    form_class = PagamentoForm
    pk_url_kwarg = 'pag_id'

#@method_decorator(login_required, name='dispatch')
class ContaDetail(DetailView):
    template_name = 'core/conta_detail.html'
    model = Conta
    form_class = ContaForm
    pk_url_kwarg = 'conta_id'

#@method_decorator(login_required, name='dispatch')
class ReceitaDetail(DetailView):
    template_name = 'core/receita_detail.html'
    model = Receita
    form_class = ReceitaForm
    pk_url_kwarg = 'receita_id'



# Create
class AtivoCreate(CreateView):
    template_name = 'core/ativo_create.html'
    model = Ativos
    form_class = AtivoForm
    success_url = 'ativo-list'

class SwingCreate(CreateView):
    template_name = 'core/swing_create.html'
    model = SwingTrade
    form_class = SwingForm
    success_url = 'swing-list'

class DayCreate(CreateView):
    template_name = 'core/day_create.html'
    model = DayTrade
    form_class = DayForm
    success_url = 'day-list'

class PagamentoCreate(CreateView):
    template_name = 'core/pagamento_create.html'
    model = Pagamento
    form_class = PagamentoForm
    success_url = 'pagamento-list'

class ContaCreate(CreateView):
    template_name = 'core/conta_create.html'
    model = Conta
    form_class = ContaForm
    success_url = 'conta-list'

class ReceitaCreate(CreateView):
    template_name = 'core/Receita_create.html'
    model = Receita
    form_class = ReceitaForm
    success_url = 'receita-list'


# Update
class AtivoUpdate(UpdateView):
    template_name = 'core/ativo_update.html'
    model = Ativos
    form_class = AtivoForm
    slug_field = 'codigo'
    slug_url_kwarg = 'codigo'

class SwingUpdate(UpdateView):
    template_name = 'core/swing_update.html'
    model = SwingTrade
    form_class = SwingForm
    pk_url_kwarg = 'swing_id'

class DayUpdate(UpdateView):
    template_name = 'core/day_update.html'
    model = DayTrade
    form_class = DayForm
    pk_url_kwarg = 'day_id'

class PagamentoUpdate(UpdateView):
    template_name = 'core/pagamento_update.html'
    model = Pagamento
    form_class = PagamentoForm
    pk_url_kwarg = 'pag_id'

class ContaUpdate(UpdateView):
    template_name = 'core/conta_update.html'
    model = Conta
    form_class = ContaForm
    pk_url_kwarg = 'conta_id'

class ReceitaUpdate(UpdateView):
    template_name = 'core/receita_update.html'
    model = Receita
    form_class = ReceitaForm
    pk_url_kwarg = 'receita_id'


# Delete
class AtivoDelete(DeleteView):
    template_name = 'core/ativo_delete.html'
    model = Ativos
    slug_field = 'codigo'
    slug_url_kwarg = 'codigo'
    success_url = reverse_lazy('core:ativo-list')

class SwingDelete(DeleteView):
    template_name = 'core/swing_delete.html'
    model = SwingTrade
    pk_url_kwarg = 'swing_id'
    success_url = reverse_lazy('core:swing-list')

class DayDelete(DeleteView):
    template_name = 'core/day_delete.html'
    model = DayTrade
    pk_url_kwarg = 'day_id'
    success_url = reverse_lazy('core:day-list')

class PagamentoDelete(DeleteView):
    template_name = 'core/pagamento_delete.html'
    model = Pagamento
    pk_url_kwarg = 'pag_id'
    success_url = reverse_lazy('core:pagamento-list')

class ContaDelete(DeleteView):
    template_name = 'core/conta_delete.html'
    model = Conta
    pk_url_kwarg = 'conta_id'
    success_url = reverse_lazy('core:conta-list')

class ReceitaDelete(DeleteView):
    template_name = 'core/receota_delete.html'
    model = Conta
    pk_url_kwarg = 'receita_id'
    success_url = reverse_lazy('core:receita-list')




def confirma_buscar_historicos(request, dias):
    ''' Função para renderizar formulário de confirmação
        para buscar histórico dos ativos.
        Dias - Recebe o número de dias.
    '''
    context = {'dias' : dias}
    return render(request, 'core/confirma_busca_historico.html', context)


def convert_datetime(epoch):
    ''' Converte segundos epoch em data de banco de dados sqllite
    '''

    class_time = localtime(epoch)
    return datetime(class_time.tm_year, class_time.tm_mon, class_time.tm_mday, 0, 0)


def calcula_variacao_dia_ativo(ativo, data=None):
    ''' Calcula a variação do valor de cada dia do ativo e salva no campo variacao_dia
        Ativo - instância do ativo
        Data - datetime - data de filtro
        Retorna dicionario com atividade e status
    '''

    flag_debug = 0
    lista_feriados = ('10/04', '21/04', '01/05', '11/06', '07/09', '12/10', '02/11', '25/12', '31/12', '01/01')

    print('Iniciando calculo de variacao por dia do ativo %s' % (ativo.codigo))

    # Se a data for informada, aplica no filtro para registros
    # Com 'data maior que'
    if data is None:
        historicos = HistoricoAtivo.objects.filter(ativo=ativo).order_by('-data')
    else:
        historicos = HistoricoAtivo.objects.filter(ativo=ativo, data__gte=data).order_by('-data')

    for line in historicos:
        # A variação é calculada com o fechamento do dia anterior
        data_dia_menos = line.data - timedelta(days=1)
        # Se a data dia menos cair em um feriado, remove mais um dia
        if data_dia_menos.strftime('%d/%m') in lista_feriados:
            data_dia_menos = data_dia_menos - timedelta(days=1)

        if flag_debug == 1:
            print("Data da linha", line.data, "Data do dia anterior:",
                    data_dia_menos, "Valor do dia anterior", data_dia_menos.weekday())

        # Se dia anteior é domingo (6), calcula para sexta, voltando mais 2 dias
        if data_dia_menos.weekday() == 6:
            data_dia_menos = data_dia_menos - timedelta(days=2)
            if flag_debug == 1:
                print("Caiu no domingo, removendo mais 2 dias:",data_dia_menos)
        # Se dia anteior é sabado (5), calcula para sexta, voltando mais 1 dias
        if data_dia_menos.weekday() == 5:
            data_dia_menos = data_dia_menos - timedelta(days=1)
            if flag_debug == 1:
                print("Caiu no sabádo, removendo mais 1 dia:",data_dia_menos)
        #Se cai em um feriado, tira mais 1 dia.
        if data_dia_menos.strftime('%d/%m') in lista_feriados:
            data_dia_menos = data_dia_menos - timedelta(days=1)
            if flag_debug == 1:
                print("Caiu em um feriado, removendo mais 1 dia:",data_dia_menos)

        # confirma que a data calulada existe para o ativo.
        if HistoricoAtivo.objects.filter(ativo=ativo, data=data_dia_menos).exists():
            line_data_dia_menos = HistoricoAtivo.objects.get(ativo=ativo, data=data_dia_menos)
            # Verifica se o valor de chamento não é nulo na data anterior.
            # Se for seta variação do dia como None.
            if line.valor_fechamento is not None and line_data_dia_menos.valor_fechamento is not None:
                line.variacao_dia = ((line.valor_fechamento / line_data_dia_menos.valor_fechamento) - 1) * 100
            else:
                line.variacao_dia = None

            if line.valor_minima is not None and line.valor_minima != 0:
                if line_data_dia_menos.valor_fechamento is not None and line_data_dia_menos.valor_fechamento != 0:
                    line.diff_minima_fechamento_dia_anterior = ((line.valor_minima / line_data_dia_menos.valor_fechamento) - 1) * 100
                else:
                    line.diff_minima_fechamento_dia_anterior = None
            else:
                line.diff_minima_fechamento_dia_anterior = None
        try:
            line.save()
        # return {'calculo_ativo_dia' : {'status' : 'sucesso',
        #         'mensagem' : 'Calculo da variacao do dia do ativo %s feito com sucesso' % (ativo.codigo)}}
        except Exception as e:
            print(exc_info()[1])
            print(e)
            continue
    # return {'calculo_ativo_dia' : {'status' : 'erro', 'mensagem' : 'Calculo da variacao do dia com erro'}} 


def calcula_diferenca_variacao_ibov_ativo(ativo, data=None):
    ''' Calcula a diferenca de variação de todos os ativos com a ibov
        e salva no campo diferenca_variacao_com_ibov

        Ativo - Instância do ativo
        Data - Data para filtrar o histórico.
    '''

    #ativo = Ativos.objects.get(id=ativo_id)
    print('Iniciando calculo da diferença de variação do ativo %s com IBOV' % (ativo.codigo))
    # Conferei se o ativo existe.
    if Ativos.objects.filter(codigo='IBOV').exists():
        ibov = Ativos.objects.get(codigo='IBOV')
        # Se tem data, aplica filtro na consulta
        if data is None:
            historicos_ibov = HistoricoAtivo.objects.filter(ativo=ibov).order_by('-data')
            historicos_ativo = HistoricoAtivo.objects.filter(ativo=ativo).order_by('-data')
        else:
            historicos_ibov = HistoricoAtivo.objects.filter(ativo=ibov, data__gte=data).order_by('-data')
            historicos_ativo = HistoricoAtivo.objects.filter(ativo=ativo, data__gte=data).order_by('-data')

        for line in historicos_ativo:
            try:
                line_ibov = HistoricoAtivo.objects.get(ativo=ibov, data=line.data)
                # Se variação do dia da IBOV não é nula e do ativo também não é nula.
                # Se é nulo, seta diferenca_variacao_com_ibov como nulo.
                if line_ibov.variacao_dia is not None and line.variacao_dia is not None:
                    if line_ibov.data.day == line.data.day:
                        line.diferenca_variacao_com_ibov = line.variacao_dia - line_ibov.variacao_dia
                    else:
                        print('falha ao calcular diferença com IBOV do historico do ativo %s' % (ativo))
                else:
                    line.diferenca_variacao_com_ibov = None
            except Exception as e:
                print(exc_info()[1])
                print(e)
            try:
                line.save()
            except Exception as e:
                print(exc_info()[1])
                print(e)
        return


def busca_historico_ativ(request, ativo_id, dias):
    ''' Busca e cria o historico de uma ação.
        Setado default 120 dias corridos atrás.
        No final, calcula a variação do dia
        e a diferença do fechamento do dia
        com IBOV.
        
        ativo_id - ID do ativo.
        dias - dias para calcular a data.
    '''

    flag_debug = 0

    ativo = Ativos.objects.get(id=ativo_id)
    start_date = date.today() - timedelta(days=int(dias))
    end_date = date.today() - timedelta(days=1)

    if ativo.codigo == 'IBOV':
        nome_ativo = '^BVSP'
    else:
        nome_ativo = str(ativo.codigo) + ".SA"
    
    print("Buscando histórico do ativo %s dos últimos %s dias a base do yahoo." % (nome_ativo, str(dias)))

    try:
        historico = pd_data.DataReader(nome_ativo, "yahoo", start_date, end_date)
    except Exception as e:
        print(traceback.print_exc())
    else:
        for index in historico.index:
            try:
                data = index
                if nome_ativo == '^BVSP':
                    response_quotes_open = int(historico.loc[index, 'Open'])
                    response_quotes_close = int(historico.loc[index, 'Close'])
                    response_quotes_low = int(historico.loc[index, 'Low'])
                    response_quotes_high = int(historico.loc[index, 'High'])		 
                else:
                    response_quotes_open = historico.loc[index, 'Open']
                    response_quotes_close = historico.loc[index, 'Close']
                    response_quotes_low = historico.loc[index, 'Low']
                    response_quotes_high = historico.loc[index, 'High']		 

                if response_quotes_low is not None and response_quotes_low != 0.0:
                    if response_quotes_close is not None and response_quotes_close != 0.0:
                        diff_minima_fechamento = ((response_quotes_close * 100) / response_quotes_low) - 100
                    else:
                        diff_minima_fechamento = None
                else:
                    diff_minima_fechamento = None
        
                if flag_debug == 1:
                    print("Resultado do dia:", data)
                    print("response_quotes_open", response_quotes_open)
                    print("response_quotes_close", response_quotes_close)
                    print("response_quotes_low", response_quotes_low)
                    print("response_quotes_high", response_quotes_high)
                
                object_temp = HistoricoAtivo(
                        ativo=ativo,
                        data=data,
                        valor_abertura=response_quotes_open,
                        valor_fechamento=response_quotes_close,
                        valor_minima=response_quotes_low,
                        valor_maxima=response_quotes_high,
                        diff_minima_fechamento=diff_minima_fechamento
                    )

                # Se o historico já existe, somente o atualiza
                if HistoricoAtivo.objects.filter(ativo=ativo, data=data).exists():
                    ativo_historico = HistoricoAtivo.objects.get(ativo=ativo, data=data)
                    ativo_historico.valor_abertura = response_quotes_open
                    ativo_historico.valor_fechamento = response_quotes_close
                    ativo_historico.valor_minima = response_quotes_low
                    ativo_historico.valor_maxima = response_quotes_high
                    ativo_historico.diff_minima_fechamento = diff_minima_fechamento
                    ativo_historico.save()
                    if flag_debug == 1:
                        print("Registro do ativo %s atualizado com sucesso, data %s" % (nome_ativo, data))
                else:
                    try:
                        object_temp.save()
                        if flag_debug == 1:
                            print("Novo registro do %s salvo com sucesso, data %s" % (nome_ativo, data))
                    except Exception as e:
                        print(exc_info())
                        print("Falha ao salvar novo registro do ativo %s, data %s" % (nome_ativo, data))
                        continue
            except Exception as e:
                print(traceback.print_exc())
                print("Erro ao buscar histórico do ativo: ", nome_ativo)
                continue
    # Calcula a variação do dia 
    calcula_variacao_dia_ativo(ativo, start_date)
    # Calcula a diferença da variação com a IBOV
    calcula_diferenca_variacao_ibov_ativo(ativo, start_date)
    return redirect('core:ativo-detail', ativo.codigo)


def calcula_variacao_dia_todos_ativos(data):
    ''' Calcula a variação de todos os ativos
        a partir da data e salva no campo variacao_dia
        Chama a função calcula_variacao_dia_ativo.
        
        data - filtro de data para buscar os históricos
    '''

    ativos = Ativos.objects.all().order_by('codigo')
    for ativo in ativos:
        calcula_variacao_dia_ativo(ativo, data)
    return


def calcula_diferenca_variacao_ibov_todos_ativos(data):
    ''' Calcula a diferenca de variação de todos os ativos com a ibov
        e a partir da data informada
        e salva no campo diferenca_variacao_com_ibov
    '''

    ativos = Ativos.objects.exclude(codigo='IBOV').order_by("codigo")
    if Ativos.objects.filter(codigo='IBOV').exists():
        for ativo in ativos:
            calcula_diferenca_variacao_ibov_ativo(ativo, data)
        return
    else:
        return


def calcula_variacao_e_diferenca(request):
    ''' Função que chama o cálculo da variação e diferença
        de variação com a IBOV de todos os ativos.
    '''

    dias = 150
    data_menos_dias = date.today() - timedelta(days=dias)
    calcula_variacao_dia_todos_ativos(data_menos_dias)
    calcula_diferenca_variacao_ibov_todos_ativos(data_menos_dias)
    return redirect('core:ativo-list')

def busca_historico_ativos(request, dias=120):
    ''' Busca e cria os historicos de todas as ações da tabela Ativos
        Padrão é de hoje até 120 dias atrás
    '''

    flag_debug = 0

    start_date = date.today() - timedelta(days=int(dias))
    end_date = date.today() - timedelta(days=1)
    
    # Busca os históricos de cada ativo
    ativos = Ativos.objects.all().order_by('codigo')
    if ativos.count() > 0:
        for ativo in ativos:
            if ativo.codigo == 'IBOV':
                nome_ativo = '^BVSP'
            else:
                nome_ativo = str(ativo.codigo) + ".SA"
            print("Buscando histórico do ativo %s dos últimos %s dias a base do yahoo." % (nome_ativo, str(dias)))

            try:
                historico = pd_data.DataReader(nome_ativo, "yahoo", start_date, end_date)
            except Exception as e:
                print(traceback.print_exc())
                continue
            
            for index in historico.index:
                data = index
                if nome_ativo == '^BVSP':
                    response_quotes_open = int(historico.loc[index, 'Open'])
                    response_quotes_close = int(historico.loc[index, 'Close'])
                    response_quotes_low = int(historico.loc[index, 'Low'])
                    response_quotes_high = int(historico.loc[index, 'High'])		 
                else:
                    response_quotes_open = historico.loc[index, 'Open']
                    response_quotes_close = historico.loc[index, 'Close']
                    response_quotes_low = historico.loc[index, 'Low']
                    response_quotes_high = historico.loc[index, 'High']		 

                if response_quotes_low is not None and response_quotes_close is not None:
                    diff_minima_fechamento = ((response_quotes_close - response_quotes_low) * 100) / response_quotes_low
                else:
                    diff_minima_fechamento = None

                if flag_debug == 1:
                    print("response_quotes_open", response_quotes_open)
                    print("response_quotes_close", response_quotes_close)
                    print("response_quotes_low", response_quotes_low)
                    print("response_quotes_high", response_quotes_high)
                object_temp = HistoricoAtivo(
                    ativo=ativo,
                    data=data,
                    valor_abertura=response_quotes_open,
                    valor_fechamento=response_quotes_close,
                    valor_minima=response_quotes_low,
                    valor_maxima=response_quotes_high,
                    diff_minima_fechamento=diff_minima_fechamento
                    )
                    # Se o historico já existe, somente o atualiza
                if HistoricoAtivo.objects.filter(ativo=ativo, data=data).exists():
                    ativo_historico = HistoricoAtivo.objects.get(ativo=ativo, data=data)
                    ativo_historico.valor_abertura = response_quotes_open
                    ativo_historico.valor_fechamento = response_quotes_close
                    ativo_historico.valor_minima = response_quotes_low
                    ativo_historico.valor_maxima = response_quotes_high
                    ativo_historico.diff_minima_fechamento = diff_minima_fechamento
                    try:
                        ativo_historico.save()
                        if flag_debug == 1:
                            print("Registro do ativo %s atualizado com sucesso, data %s" % (nome_ativo, data))
                    except Exception as e:
                        print(exc_info())
                        print("Falha ao salvar novo registro do ativo %s, data %s" % (nome_ativo, data))
                        continue
                else:
                    try:
                        object_temp.save()
                        if flag_debug == 1:
                            print("Novo registro do %s salvo com sucesso, data %s" % (nome_ativo, data))
                    except Exception as e:
                        print(exc_info())
                        print("Falha ao salvar novo registro do ativo %s, data %s" % (nome_ativo, data))
                        continue
        
        # Apos finalizar loop do for, 
        # realiza o calculo da variação do ativo e da diferença da variação
        # com a IBOV
        print('loop finalizado')
        calcula_variacao_dia_todos_ativos(start_date)
        calcula_diferenca_variacao_ibov_todos_ativos(start_date)
        busca_descontos_padroes(50, 70)
        busca_descontos_padroes(50, 80)
        busca_descontos_padroes(50, 85)
        busca_descontos_padroes(50, 90)
        return redirect('core:ativo-list')
    else:
        return redirect('core:ativo-list')

def busca_ativos_rankiado(request):
    ''' Busca o valor do fechamento de acordo com uma porcetagem.

    '''

    array_ativos = []
    valor = -4
    dias = 10
    ativos = Ativos.objects.exclude(codigo='IBOV')
    for ativo in ativos:
        array_ativos.append([ativo.codigo, float(ativo.porcentagem_em_dias_maior_valor(-4.5, 10))])

    array_ativos = np.array(array_ativos)
    new_array_ativos = array_ativos[array_ativos[:, 1].argsort()[::-1]]
    for index in new_array_ativos:
        print(index[0].index[1])
    return redirect('core:ativo-list')

def busca_desconto_por_porcentagem(request):
    ''' Método GET
        Busca o desconto ideal para um ação de acordo com a porcentagem
        dentro de um determinado dia. Limite mínimo é -15
    '''

    if request.method == 'GET':
        get_paramenters = dict(request.GET)
        if 'porcentagem' in get_paramenters and 'dias' in get_paramenters \
            and "filtro_fechamento" in get_paramenters:
            lista_descontos_temp = []
            dicionario_descontos = {}
            dias = int(get_paramenters['dias'][0])
            porcentagem_alvo = float(get_paramenters['porcentagem'][0])
            filtro_fechamento = float(get_paramenters['filtro_fechamento'][0].replace(',', '.'))
            ativos = Ativos.objects.exclude(codigo='IBOV').exclude(flag_habilitado_operar=False).order_by('codigo')
            for ativo in ativos:
                valores = ativo.calcula_metricas_desconto(dias, porcentagem_alvo)
                if valores is not None:
                    lista_descontos_temp.append(valores)
                    # remove com slice o codigo do ativo no index 0
                    dicionario_descontos[ativo.codigo + "-ct1"] = valores[1:]
                    lista_descontos_csv = lista_descontos_temp[1:]
                    lista_descontos_csv.append(ativo.codigo)
            
            lista_descontos_temp = np.array(lista_descontos_temp)
            # cria um lista ordenando pelo fechamento bons e retorna 'dados' para requisição
            lista_descontos = list(lista_descontos_temp[lista_descontos_temp[:,2].argsort()[::-1]])
            dados = {
                        "lista_descontos" :  lista_descontos,
                        "porcentagem_alvo" : porcentagem_alvo,
                        "pregoes" : dias,
                        "filtro_fechamento" : filtro_fechamento
                    }

            return render(request, "core/busca_descontos_ativos.html", dados)
        else:
            return render(request, "core/busca_descontos_ativos.html")


def busca_descontos_padroes(dias, porcentagem):
    ''' Função quer realiza calculos de desconto e gerar arquivos csv
    '''

    lista_descontos_temp = []
    dicionario_descontos = {}
    dias = int(dias)
    porcentagem_alvo = float(porcentagem)
    ativos = Ativos.objects.exclude(codigo='IBOV').exclude(flag_habilitado_operar=False).order_by('codigo')
    for ativo in ativos:
        valores = ativo.calcula_metricas_desconto(dias, porcentagem_alvo)
        if valores is not None:
            lista_descontos_temp.append(valores)
            # remove com slice o codigo do ativo no index 0
            dicionario_descontos[ativo.codigo + "-ct1"] = valores[1:]
            lista_descontos_csv = lista_descontos_temp[1:]
            lista_descontos_csv.append(ativo.codigo)
 
    # # Cria arquivo CSV
    # file_name_csv = "descontos_" + str(int(porcentagem_alvo)) + ".csv"
    # with open(file_name_csv, mode='w', newline='') as file_csv:
    #     file_csv_write = csv.writer(file_csv, delimiter=';')
    #     file_csv_write.writerow(['ativo','desconto','fechamentos_bons_ibov', 'fechamentos_bons_da_minina',
    #                             'ultima_variacao','variacao_ultimo_7_dias','variacao_ultimo_30_dias',
    #                             'variacao_ultimo_60_dias'])
    #     for line in lista_descontos_csv:
    #         file_csv_write.writerow(line)

def carrega_ativos(request):
    '''
    Função pra carregar ativos da bovespa
    '''
    return
    from os import path
    print(__file__)
    print(path.abspath(__file__))
    print(path.dirname(path.abspath(__file__)))
    file_path = path.dirname(path.abspath(__file__)) + '\\csv\\'
    arquivo = 'carga_ativos.csv'
    path_full = file_path + arquivo
    import csv
    try:
        with open(path_full, encoding='ISO-8859-1') as csv_file:
            csv_read = csv.reader(csv_file, delimiter=',')
            for row in csv_read:
                object_temp = Ativos(
                    codigo=row[0],
                    nome=row[1],
                    setor=row[2]
                )
                try:
                    if Ativos.objects.filter(codigo=object_temp.codigo).exists() is not False:
                        object_temp.save()
                except Exception as e:
                    print(exc_info()[1])
                    print(e)
        ativos_inseridos = ", </BR>".join(ativos.nome for ativos in Ativos.objects.all())
        ativos_inseridos = 'Carga de ativos realizada com sucesso: </BR>' + ativos_inseridos
        ativos = Ativos.objects.all()
        return render(request, 'core/ativo_list.html', {"ativos_list": ativos})
    except Exception:
        return HttpResponse('Falha ao ler arquivo CSV: %s. Erro %s' % (arquivo, str(exc_info())))


def deleta_ativos(request):
    return
    try:
        ativos_deletar = ", </BR>".join(ativo.codigo for ativo in Ativos.objects.all())
        Ativos.objects.all().delete()
        ativos = Ativos.objects.all()
        return render(request, 'core/ativo_list.html', {"ativos_list": ativos})
        # return HttpResponse('Ativos deletos do banco de dados com sucesso: <BR>' + ativos_deletar)
    except Exception:
        return HttpResponse('Falha deletar ativos, erro: %s' % (str(exc_info())))
