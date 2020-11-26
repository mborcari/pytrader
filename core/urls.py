from django.urls import path, re_path, include
from . import views
app_name = 'core'

urlpatterns = [
     path('', views.login_detail, name='login'),
    path('login', views.login_detail, name='login'),
    path('index', views.index_page, name='index'),
   
    #Pagamento
    path('pagamento-list', views.PagamentoList.as_view(), name='pagamento-list'),
    path('pagamento-create', views.PagamentoCreate.as_view(), name='pagamento-create'),
    re_path(r'pagamento/(?P<pag_id>\d+)', views.PagamentoDetail.as_view(), name='pagamento-detail'),
    re_path(r'pagamento-update/(?P<pag_id>\d+)', views.PagamentoUpdate.as_view(), name='pagamento-update'),
    re_path(r'pagamento-delete/(?P<pag_id>\d+)', views.PagamentoDelete.as_view(), name='pagamento-delete'),

    # Contas modelos
    path('conta-list', views.ContaList.as_view(), name='conta-list'),
    path('conta-create', views.ContaCreate.as_view(), name='conta-create'),
    re_path(r'conta/(?P<conta_id>\d+)', views.ContaDetail.as_view(), name='conta-detail'),
    re_path(r'conta-update/(?P<conta_id>\d+)', views.ContaUpdate.as_view(), name='conta-update'),
    re_path(r'conta-delete/(?P<conta_id>\d+)', views.ContaDelete.as_view(), name='conta-delete'),

    #SwingTrade
    path('swing-list', views.SwingListView.as_view(), name='swing-list'),
    path('swing-create', views.SwingCreate.as_view(), name='swing-create'),
    re_path(r'swing/(?P<swing_id>\d+)', views.SwingDetail.as_view(), name='swing-detail'),
    re_path(r'swing-update/(?P<swing_id>\d+)', views.SwingUpdate.as_view(), name='swing-update'),
    re_path(r'swing-delete/(?P<swing_id>\d+)', views.SwingDelete.as_view(), name='swing-delete'),

    #DayTrade
    path('day-list', views.DayListView.as_view(), name='day-list'),
    path('day-create', views.DayCreate.as_view(), name='day-create'),
    re_path(r'day/(?P<day_id>\d+)', views.DayDetail.as_view(), name='day-detail'),
    re_path(r'day-update/(?P<day_id>\d+)', views.DayUpdate.as_view(), name='day-update'),
    re_path(r'day-delete/(?P<day_id>\d+)', views.DayDelete.as_view(), name='day-delete'),

    #Receita
    path('receita-list', views.ReceitaList.as_view(), name='receita-list'),
    path('receita-create', views.ReceitaCreate.as_view(), name='receita-create'),
    re_path(r'receita/(?P<receita_id>\d+)', views.ReceitaDetail.as_view(), name='receita-detail'),
    re_path(r'receita-update/(?P<receita_id>\d+)', views.ReceitaUpdate.as_view(), name='receita-update'),
    re_path(r'receita-delete/(?P<receita_id>\d+)', views.ReceitaDelete.as_view(), name='receita-delete'),

    # Ativo
    path('ativo-list', views.AtivosListView.as_view(), name='ativo-list'),
    path('ativo-create', views.AtivoCreate.as_view(), name='ativo-create'),
    re_path(r'ativo/(?P<codigo>\w+)', views.AtivosDetail.as_view(), name='ativo-detail'),
    re_path(r'ativo-update/(?P<codigo>\w+)', views.AtivoUpdate.as_view(), name='ativo-update'),
    re_path(r'ativo-delete/(?P<codigo>\w+)', views.AtivoDelete.as_view(), name='ativo-delete'),

    re_path(r'confirma_buscar_historicos/(?P<dias>\d+)', views.confirma_buscar_historicos, name='confirma_buscar_historicos'),

    re_path(r'busca_historico_ativ/(?P<ativo_id>\d+)/(?P<dias>\d+)', views.busca_historico_ativ,
            name='busca_historico_ativ'),

    re_path(r'busca_historico_ativos/(?P<dias>\d+)', views.busca_historico_ativos,
            name='busca_historico_ativos'),
    path('busca_desconto_por_porcentagem', views.busca_desconto_por_porcentagem,
        name='busca_desconto_por_porcentagem'),
    path('calcula_variacao_e_diferenca', views.calcula_variacao_e_diferenca, name='calcula_variacao_e_diferenca'),


    #path('carrega_ativos', views.carrega_ativos, name='carrega_ativos'),
    #path('remove_ativos', views.deleta_ativos, name='remove_ativos'),
]