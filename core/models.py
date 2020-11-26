from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.urls import reverse
from datetime import datetime, timedelta, date
from .choices import LISTA_BOLSA, LISTA_CORRETORA, LISTA_TIPO_MOV, LISTA_RECEITA, LISTA_SETOR
from django.core.validators import MaxValueValidator, MinValueValidator
import numpy as np

class Ativos(models.Model):
    ''' Modelo de dados com as informações do ativo
    '''
    codigo = models.SlugField(max_length=20, unique=True, verbose_name='Código')
    nome = models.CharField(max_length=200, blank=False, verbose_name='Nome')
    setor = models.CharField(max_length=200, choices=LISTA_SETOR, verbose_name='Setor')

    # Sinaliza se esse ativo está habilitado para ser operado.
    flag_habilitado_operar = models.BooleanField(default=True, verbose_name='Habilitado para operar?')

    # Utilizado no calculo de proabilidade do ativo subir dentro de um período.
    dias_calculo = models.IntegerField(verbose_name='Dias para calculo',
                                        default=42, validators=[
                                    MaxValueValidator(100),
                                    MinValueValidator(1)
                                ])

    #Porcentagem para calcular o valor de desconto ideal.
    porcentagem_desconto =  models.IntegerField(verbose_name='Porcentagem para desconto',
                                        default=80, validators=[
                                        MaxValueValidator(100),
                                        MinValueValidator(70)
                                    ])
    desconto_calculado =  models.DecimalField(max_digits=10, decimal_places=2, 
                                        verbose_name='Desconto calculado',
                                        default=0)
    # objects = models.Manager()
    # DiferencaIndexAtivosIbov = DiferencaIndexAtivosIbov()


    def dias_primeiro_filtro(self):
        return 21

    def dias_segundo_filtro(self):
        return 42

    def dias_terceiro_filtro(self):
        return 64

    def lista_dias_primeiro_filtro(self):
        return HistoricoAtivo.objects.values("diferenca_variacao_com_ibov").filter(ativo=self).order_by('-data')[:self.dias_primeiro_filtro()]

    def lista_dias_segundo_filtro(self):
        return HistoricoAtivo.objects.values("diferenca_variacao_com_ibov").filter(ativo=self).order_by('-data')[:self.dias_segundo_filtro()]

    def lista_dias_terceiro_filtro(self):
        return HistoricoAtivo.objects.values("diferenca_variacao_com_ibov").filter(ativo=self).order_by('-data')[:self.dias_terceiro_filtro()]

    def filtra_lista_de_dias(self, menor_filtro=None, maior_filtro=None):
        '''
            Filtra lista de dias com o filtro informado 
        '''
        def filtra_lista(lista):
            if lista["diferenca_variacao_com_ibov"] is None:
                return False
            if maior_filtro == None:
                if lista["diferenca_variacao_com_ibov"] > menor_filtro:
                    return True
                else:
                    return False
            elif menor_filtro == None:
                if lista["diferenca_variacao_com_ibov"]  <= maior_filtro:
                    return True
                else:
                    return False
            else:
                if lista["diferenca_variacao_com_ibov"]  > menor_filtro and lista["diferenca_variacao_com_ibov"]  <= maior_filtro:
                    return True
                else:
                    return False
        return filtra_lista

    def primeiro_filtro_e_menor_4_5(self):
        filtro = self.filtra_lista_de_dias(maior_filtro=-4.5)
        quantidade = filter(filtro,self.lista_dias_primeiro_filtro())
        return len(list(quantidade))

    def segundo_filtro_e_menor_4_5(self):
        filtro = self.filtra_lista_de_dias(maior_filtro=-4.5)
        quantidade = filter(filtro, self.lista_dias_segundo_filtro())
        return len(list(quantidade))

    def terceiro_filtro_e_menor_4_5(self):
        filtro = self.filtra_lista_de_dias(maior_filtro=-4.5)
        quantidade = filter(filtro, self.lista_dias_terceiro_filtro())
        return len(list(quantidade))
    
    def primeiro_filtro_4_5_3_5(self):
        filtro = self.filtra_lista_de_dias(menor_filtro=-4.5, maior_filtro=-3.5)
        quantidade = filter(filtro,self.lista_dias_primeiro_filtro())
        return len(list(quantidade))

    def segundo_filtro_4_5_3_5(self):
        filtro = self.filtra_lista_de_dias(menor_filtro=-4.5, maior_filtro=-3.5)
        quantidade = filter(filtro,self.lista_dias_segundo_filtro())
        return len(list(quantidade))

    def terceiro_filtro_4_5_3_5(self):
        filtro = self.filtra_lista_de_dias(menor_filtro=-4.5, maior_filtro=-3.5)
        quantidade = filter(filtro,self.lista_dias_terceiro_filtro())
        return len(list(quantidade))
    
    def primeiro_filtro_3_5_2_5(self):
        filtro = self.filtra_lista_de_dias(menor_filtro=-3.5, maior_filtro=-2.5)
        quantidade = filter(filtro,self.lista_dias_primeiro_filtro())
        return len(list(quantidade))

    def segundo_filtro_3_5_2_5(self):
        filtro = self.filtra_lista_de_dias(menor_filtro=-3.5, maior_filtro=-2.5)
        quantidade = filter(filtro,self.lista_dias_segundo_filtro())
        return len(list(quantidade))

    def terceiro_filtro_3_5_2_5(self):
        filtro = self.filtra_lista_de_dias(menor_filtro=-3.5, maior_filtro=-2.5)
        quantidade = filter(filtro,self.lista_dias_terceiro_filtro())
        return len(list(quantidade))

    def primeiro_filtro_2_5_1_5(self):
        filtro = self.filtra_lista_de_dias(menor_filtro=-2.5, maior_filtro=-1.5)
        quantidade = filter(filtro,self.lista_dias_primeiro_filtro())
        return len(list(quantidade))

    def segundo_filtro_2_5_1_5(self):
        filtro = self.filtra_lista_de_dias(menor_filtro=-2.5, maior_filtro=-1.5)
        quantidade = filter(filtro,self.lista_dias_segundo_filtro())
        return len(list(quantidade))

    def terceiro_filtro_2_5_1_5(self):
        filtro = self.filtra_lista_de_dias(menor_filtro=-2.5, maior_filtro=-1.5)
        quantidade = filter(filtro,self.lista_dias_terceiro_filtro())
        return len(list(quantidade))

    def primeiro_filtro_1_5_0_5(self):
        filtro = self.filtra_lista_de_dias(menor_filtro=-1.5, maior_filtro=-0.5)
        quantidade = filter(filtro,self.lista_dias_primeiro_filtro())
        return len(list(quantidade))

    def segundo_filtro_1_5_0_5(self):
        filtro = self.filtra_lista_de_dias(menor_filtro=-1.5, maior_filtro=-0.5)
        quantidade = filter(filtro,self.lista_dias_segundo_filtro())
        return len(list(quantidade))

    def terceiro_filtro_1_5_0_5(self):
        filtro = self.filtra_lista_de_dias(menor_filtro=-1.5, maior_filtro=-0.5)
        quantidade = filter(filtro,self.lista_dias_terceiro_filtro())
        return len(list(quantidade))

    def primeiro_filtro_0_5_0_5(self):
        filtro = self.filtra_lista_de_dias(menor_filtro=-0.5, maior_filtro=0.5)
        quantidade = filter(filtro,self.lista_dias_primeiro_filtro())
        return len(list(quantidade))

    def segundo_filtro_0_5_0_5(self):
        filtro = self.filtra_lista_de_dias(menor_filtro=-0.5, maior_filtro=0.5)
        quantidade = filter(filtro,self.lista_dias_segundo_filtro())
        return len(list(quantidade))

    def terceiro_filtro_0_5_0_5(self):
        filtro = self.filtra_lista_de_dias(menor_filtro=-0.5, maior_filtro=0.5)
        quantidade = filter(filtro,self.lista_dias_terceiro_filtro())
        return len(list(quantidade))

    def primeiro_filtro_0_5_1_5(self):
        filtro = self.filtra_lista_de_dias(menor_filtro=0.5, maior_filtro=1.5)
        quantidade = filter(filtro,self.lista_dias_primeiro_filtro())
        return len(list(quantidade))

    def segundo_filtro_0_5_1_5(self):
        filtro = self.filtra_lista_de_dias(menor_filtro=0.5, maior_filtro=1.5)
        quantidade = filter(filtro,self.lista_dias_segundo_filtro())
        return len(list(quantidade))

    def terceiro_filtro_0_5_1_5(self):
        filtro = self.filtra_lista_de_dias(menor_filtro=0.5, maior_filtro=1.5)
        quantidade = filter(filtro,self.lista_dias_terceiro_filtro())
        return len(list(quantidade))
    
    def primeiro_filtro_1_5_2_5(self):
        filtro = self.filtra_lista_de_dias(menor_filtro=1.5, maior_filtro=2.5)
        quantidade = filter(filtro,self.lista_dias_primeiro_filtro())
        return len(list(quantidade))

    def segundo_filtro_1_5_2_5(self):
        filtro = self.filtra_lista_de_dias(menor_filtro=1.5, maior_filtro=2.5)
        quantidade = filter(filtro,self.lista_dias_segundo_filtro())
        return len(list(quantidade))

    def terceiro_filtro_1_5_2_5(self):
        filtro = self.filtra_lista_de_dias(menor_filtro=1.5, maior_filtro=2.5)
        quantidade = filter(filtro,self.lista_dias_terceiro_filtro())
        return len(list(quantidade))

    def primeiro_filtro_2_5_3_5(self):
        filtro = self.filtra_lista_de_dias(menor_filtro=2.5, maior_filtro=3.5)
        quantidade = filter(filtro,self.lista_dias_primeiro_filtro())
        return len(list(quantidade))

    def segundo_filtro_2_5_3_5(self):
        filtro = self.filtra_lista_de_dias(menor_filtro=2.5, maior_filtro=3.5)
        quantidade = filter(filtro,self.lista_dias_segundo_filtro())
        return len(list(quantidade))

    def terceiro_filtro_2_5_3_5(self):
        filtro = self.filtra_lista_de_dias(menor_filtro=2.5, maior_filtro=3.5)
        quantidade = filter(filtro,self.lista_dias_terceiro_filtro())
        return len(list(quantidade))


    def primeiro_filtro_3_5_4_5(self):
        filtro = self.filtra_lista_de_dias(menor_filtro=3.5, maior_filtro=4.5)
        quantidade = filter(filtro,self.lista_dias_primeiro_filtro())
        return len(list(quantidade))

    def segundo_filtro_3_5_4_5(self):
        filtro = self.filtra_lista_de_dias(menor_filtro=3.5, maior_filtro=4.5)
        quantidade = filter(filtro,self.lista_dias_segundo_filtro())
        return len(list(quantidade))

    def terceiro_filtro_3_5_4_5(self):
        filtro = self.filtra_lista_de_dias(menor_filtro=3.5, maior_filtro=4.5)
        quantidade = filter(filtro,self.lista_dias_terceiro_filtro())
        return len(list(quantidade))

    def primeiro_filtro_e_maior_4_5(self):
        filtro = self.filtra_lista_de_dias(menor_filtro=4.5)
        quantidade = filter(filtro,self.lista_dias_primeiro_filtro())
        return len(list(quantidade))

    def segundo_filtro_e_maior_4_5(self):
        filtro = self.filtra_lista_de_dias(menor_filtro=4.5)
        quantidade = filter(filtro,self.lista_dias_segundo_filtro())
        return len(list(quantidade))

    def terceiro_filtro_e_maior_4_5(self):
        filtro = self.filtra_lista_de_dias(menor_filtro=4.5)
        quantidade = filter(filtro,self.lista_dias_terceiro_filtro())
        return len(list(quantidade))


    def porcentagem_em_dias_maior_3_5(self, dias=None):
        ''' Porcetagem cuja diferenca com a ibov
            é maior que -3,5 dentro de um periodo de dias, 
            Se dias é None, usa valor definido em self.dias_calculo
        '''
        if dias is None:
            dias = self.dias_calculo
        if HistoricoAtivo.objects.values('diferenca_variacao_com_ibov').filter(diferenca_variacao_com_ibov__isnull=False,ativo=self)[:dias].exists():
            total = HistoricoAtivo.objects.values('diferenca_variacao_com_ibov').filter(diferenca_variacao_com_ibov__isnull=False,
                                                                ativo=self).order_by('-data')[:dias]
            filtro = self.filtra_lista_de_dias(menor_filtro=-3.5)
            parcial = len(list(filter(filtro,total)))
            return '%.2f' % ((parcial * 100) / total.count())
        else:
            return 0
    
    def porcentagem_em_dias_maior_2_5(self, dias=None):
        ''' Porcetagem cuja diferenca com a ibov
            é maior que -2,5 dentro de um periodo de dias, 
            Se dias é None, usa valor definido em self.dias_calculo
        '''

        if dias is None:
            dias = self.dias_calculo
        if HistoricoAtivo.objects.values('diferenca_variacao_com_ibov').filter(diferenca_variacao_com_ibov__isnull=False,ativo=self)[:dias].exists():
            total = HistoricoAtivo.objects.values('diferenca_variacao_com_ibov').filter(diferenca_variacao_com_ibov__isnull=False,
                                                                ativo=self).order_by('-data')[:dias]
            filtro = self.filtra_lista_de_dias(menor_filtro=-2.5)
            parcial = len(list(filter(filtro,total)))
            return '%.2f' % ((parcial * 100) / total.count())
        else:
            return 0

    def porcentagem_em_dias_maior_1_5(self, dias=None):
        ''' Porcetagem  cuja diferenca com a ibov
            é maior que -1,5 dentro de um periodo de dias, 
            Se dias é None, usa valor definido em self.dias_calculo
        '''

        if dias is None:
            dias = self.dias_calculo
        if HistoricoAtivo.objects.values('diferenca_variacao_com_ibov').filter(diferenca_variacao_com_ibov__isnull=False,ativo=self)[:dias].exists():
            total = HistoricoAtivo.objects.values('diferenca_variacao_com_ibov').filter(diferenca_variacao_com_ibov__isnull=False,
                                                                ativo=self).order_by('-data')[:dias]
            filtro = self.filtra_lista_de_dias(menor_filtro=-1.5)
            parcial = len(list(filter(filtro,total)))
            return '%.2f' % ((parcial * 100) / total.count())
        else:
            return 0

    def calcula_porcentagem_em_dias_maior_que_valor(self, desconto, dias=None):
        ''' Argumentos
            Desconto  - inteiro - Informa o desconto como: -1, -2 -3
            Dias  - inteiro - Quantidade de dias para calcular amostragem

            Calcula a probabilidade em porcentagem dentro de um periodo
            de dias maior que um valor de desconto informado
            Busca a quantidade de dias que o ativo foi melhor que a IBOV
            tendo um desconto como referência e retorna a porcentagem

        '''
        if dias is None:
            dias = self.dias_calculo
 
        if HistoricoAtivo.objects.filter(diferenca_variacao_com_ibov__isnull=False, ativo=self)[:dias].exists():
            #Busca o total de dias informado dentro do historico do ativo
            total_historico = HistoricoAtivo.objects.values("diferenca_variacao_com_ibov").filter(diferenca_variacao_com_ibov__isnull=False, ativo=self).order_by('-data')[:dias]
            #Calcula quantidade de vezes o spreed foi maior que o desconto informado.
            count = 0
            for line in total_historico:
                if line["diferenca_variacao_com_ibov"] > desconto:
                    count +=1
            return (count * 100) / total_historico.count()
        else:
            return 0


    def calcula_porcentagem_fechamento_com_minima(self, valor, dias=None):
        ''' 
            Argumentos
            valor  - inteiro - Informa o valor como -1, -2 -3...
            dias  - inteiro - Quantidade de dias para calcular amostragem

            Calcula a quantidade de vezes em que o papel variou entre o fechamento
            anterior e mínina maior que o valor informado.
            Retorna uma porcentagem em cima do valor total de dias informado.
            Exemplo: 80% das vezes o papel varia entre o fechamento e minina até -4%

        '''
        if dias is None:
            dias = self.dias_calculo
        if HistoricoAtivo.objects.filter(diff_minima_fechamento_dia_anterior__isnull=False, ativo=self)[:dias].exists():
            total_historico = HistoricoAtivo.objects.filter(diff_minima_fechamento_dia_anterior__isnull=False, ativo=self).order_by('-data')[:dias]
            count = 0
            for line in total_historico:
                if line.diff_minima_fechamento_dia_anterior > valor:
                    count +=1
            return float('%.2f' % ((count * 100) / total_historico.count()))
        else:
            return None

    def calcula_valor_fechamento_com_minima_dia_anterior(self, porcentagem_alvo=None, dias=None):
        ''' Calcula o valor de variação do ativo entre o fechamento do dia anterior
            com a mínima dentro de um determinado dias para um porcentagem alvo.
            Métrica de spreed do papel com relação a ele mesmo.
        '''

        if dias is None and porcentagem_alvo is None:
            dias = self.dias_calculo
            porcentagem_alvo = self.porcentagem_desconto

        limite = -10
        valor = 0
        while valor >= limite:
            porcentagem_calculada = self.calcula_porcentagem_fechamento_com_minima(valor, dias)
            if porcentagem_calculada is None:
                return 'N/A'
            if porcentagem_calculada >= porcentagem_alvo:
                break
            else:
                valor = valor - 0.5
        return valor

    def porcentagem_fechamento_bons_com_filtro(self, dias=None, filtro_fechamento=0):
        ''' Calcula a porcentagem em que o ativo variou
            entre a mínima e fechamento em relação ao valor do filtro
        '''

        if dias is None:
           dias = self.dias_calculo
        total_historico = HistoricoAtivo.objects.filter(diff_minima_fechamento__isnull=False, ativo=self).order_by("-data")[:dias]
        count = 0
        for dia in total_historico:
            if dia.diff_minima_fechamento > filtro_fechamento:
                count +=1
        return float('%.2f' % ((count * 100) / total_historico.count()))

    def porcentagem_fechamento_bom_relacao_IBOV(self, dias=None):
        ''' Calcula a quantidade em que o ativo variou melhor
            entre mínima e fechamento em relação ao IBOV
        '''

        if dias is None:
           dias = self.dias_calculo
        total_historico = HistoricoAtivo.objects.filter(diferenca_variacao_com_ibov__isnull=False, ativo=self).order_by("-data")[:dias]
        count = 0
        for dia in total_historico:
            if dia.comparacao_minina_fechamento_ibov() == 1:
                count +=1
        return  float('%.2f' % ((count * 100) / total_historico.count()))
    
    def menor_variacao_no_periodo(self, dias):
        ''' Método que retorna a menor variação
            do ativo em um determinado periodo.
        '''

        if dias is None:
            dias = self.dias_calculo
        total_historico = HistoricoAtivo.objects.values('id').filter(diferenca_variacao_com_ibov__isnull=False, ativo=self).order_by("-data")[:dias]
        lista_variacao = [historico.variacao_dia for historico in total_historico]
        return np.amin(lista_variacao)

    def variacao_ultima_semana(self):
        ''' Calcúla a variação do ativo na última semana
            5 dias
        '''
        dias = 5
        if HistoricoAtivo.objects.filter(ativo=self, valor_fechamento__isnull=False)[:dias].exists():
            fechamentos = HistoricoAtivo.objects.values("valor_fechamento").filter(ativo=self,
                                                        valor_fechamento__isnull=False).order_by('-data')[:dias]
            if len(fechamentos) > dias - 1:
                ultimo_fechamento = float(fechamentos[0]["valor_fechamento"])
                fechamento_ultima_semana = float(fechamentos[dias - 1]["valor_fechamento"])
                return float( '%.2f' % ((ultimo_fechamento * 100 / fechamento_ultima_semana) - 100))
            else:
                return 'N/A'
        else:
            return 'N/A'

    def variacao_ultimos_30_dias(self):
        ''' Calcúla a variação do ativo na última mês
            30 dias
        '''
        dias = 21
        if HistoricoAtivo.objects.filter(ativo=self, valor_fechamento__isnull=False)[:30].exists():
            fechamentos = HistoricoAtivo.objects.values("valor_fechamento").filter(ativo=self, valor_fechamento__isnull=False).order_by('-data')[:dias]
            if len(fechamentos) > dias-1:
                ultimo_fechamento = float(fechamentos[0]["valor_fechamento"])
                fechamento_ultimo_mes = float(fechamentos[dias-1]["valor_fechamento"])
                return float( '%.2f' % ((ultimo_fechamento * 100 / fechamento_ultimo_mes) - 100))
            else:
                print(self.codigo, "Quantidade de pregões necessários são 30 pregões", len(fechamentos))
                return 'N/A'
        else:
            return 'N/A'

    def variacao_ultimos_60_dias(self):
        ''' Calcúla a variação do ativo na última mês
            60 dias
        '''
        dias = 42
        if HistoricoAtivo.objects.filter(ativo=self, valor_fechamento__isnull=False)[:dias].exists():
            fechamentos = HistoricoAtivo.objects.values("valor_fechamento").filter(ativo=self, valor_fechamento__isnull=False).order_by('-data')[:dias]
            if len(fechamentos) > dias-1:
                ultimo_fechamento = float(fechamentos[0]["valor_fechamento"])
                fechamento_ultimo_2meses = float(fechamentos[dias-1]["valor_fechamento"])
                return float( '%.2f' % ((ultimo_fechamento * 100 / fechamento_ultimo_2meses) - 100))
            else:
                print(self.codigo, "Quantidade de pregões necessários são 60 pregões", len(fechamentos))
                return 'N/A'
        else:
            return 'N/A'

    def variacao_ultimos_90_dias(self):
        ''' Calcúla a variação do ativo na última mês
            90 dias
        '''
        dias = 64
        if HistoricoAtivo.objects.filter(ativo=self, valor_fechamento__isnull=False)[:dias].exists():
            fechamentos = HistoricoAtivo.objects.values("valor_fechamento").filter(ativo=self, valor_fechamento__isnull=False).order_by('-data')[:dias]
            if len(fechamentos) > dias-1:
                ultimo_fechamento = float(fechamentos[0]["valor_fechamento"])
                fechamento_ultimo_3meses = float(fechamentos[dias-1]["valor_fechamento"])
                return float( '%.2f' % ((ultimo_fechamento * 100 / fechamento_ultimo_3meses) - 100))
            else:
                print(self.codigo, "Quantidade de pregões necessários são 90 pregões", len(fechamentos))
                return 'N/A'
        else:
            return 'N/A'

    def variacao_ultimos_180_dias(self):
        ''' Calcúla a variação do ativo na última mês
            90 dias
        '''
        dias = 128
        if HistoricoAtivo.objects.filter(ativo=self, valor_fechamento__isnull=False)[:dias].exists():
            fechamentos = HistoricoAtivo.objects.values("valor_fechamento").filter(ativo=self, valor_fechamento__isnull=False).order_by('-data')[:dias]
            if len(fechamentos) > dias-1:
                ultimo_fechamento = float(fechamentos[0]["valor_fechamento"])
                fechamento_ultimo_3meses = float(fechamentos[dias-1]["valor_fechamento"])
                return float( '%.2f' % ((ultimo_fechamento * 100 / fechamento_ultimo_3meses) - 100))
            else:
                print(self.codigo, "Quantidade de pregões necessários são 180 pregões", len(fechamentos))
                return 'N/A'
        else:
            return 'N/A'

    def ultima_variacao(self):
        ''' Busca a última variação do ativo
        '''
        if HistoricoAtivo.objects.filter(ativo=self, variacao_dia__isnull=False).exists():
            return float(HistoricoAtivo.objects.filter(ativo=self, variacao_dia__isnull=False).last().variacao_dia)
        else:
            return 'N/A'


    def ultimo_fechamento(self):
        ''' Busca a ultimo fechamento do ativo
        '''
        if HistoricoAtivo.objects.filter(ativo=self, valor_fechamento__isnull=False).exists():
            return float(HistoricoAtivo.objects.filter(ativo=self, valor_fechamento__isnull=False).last().valor_fechamento)
        else:
            return 'N/A'

    def calcula_metricas_desconto(self, dias=None, porcentagem_alvo=None):
        ''' Calcula métricas do ativo como
            - Fechamentos bons
            - Fechamento ruins
            - Variação ultima semana
        '''
        if dias is None and porcentagem_alvo is None:
            dias = self.dias_calculo
            porcentagem_alvo = self.porcentagem_desconto
        limite = -10
        desconto = 0
        while desconto >= limite:
            porcentagem_calculada = float(self.calcula_porcentagem_em_dias_maior_que_valor(desconto, dias))
            if porcentagem_calculada >= porcentagem_alvo:
                fechamentos_bons_ibov = self.porcentagem_fechamento_bom_relacao_IBOV(dias)
                # porcentagem de fechamentos bons da minina
                pfbm1 = self.porcentagem_fechamento_bons_com_filtro(dias, 1)
                pfbm2 = self.porcentagem_fechamento_bons_com_filtro(dias, 2)
                # valor de variação padrão dentro de um confirança de porcetagem alvo
                vfm = self.calcula_valor_fechamento_com_minima_dia_anterior(porcentagem_alvo, dias)
                ultima_variacao = self.ultima_variacao()
                ultimo_fechamento = self.ultimo_fechamento()
                variacao_30 = self.variacao_ultimos_30_dias()
                variacao_60 = self.variacao_ultimos_60_dias()
                variacao_90 = self.variacao_ultimos_90_dias()
                variacao_180 = self.variacao_ultimos_180_dias()
                variacao_semana = self.variacao_ultima_semana()
                return [self, desconto, fechamentos_bons_ibov, pfbm1, pfbm2, vfm,
                        ultima_variacao, variacao_semana, variacao_30, variacao_60, variacao_90, variacao_180, ultimo_fechamento] 
            else:
                desconto = desconto - 0.5
            
            
    
    
    def calcula_desconto_ativo(self):
        ''' Calcula o desconto para o ativo
            considerando os valores nos campos
            dias_calculo e porcentagem_desconto
        '''
  
        dias = self.dias_calculo
        porcentagem_alvo = self.porcentagem_desconto
        limite = -15
        desconto = 0
        while desconto >= limite:
            porcentagem_calculada = float(self.calcula_porcentagem_em_dias_maior_que_valor(desconto, dias))
            if porcentagem_calculada >= porcentagem_alvo:
                return desconto
            else:
                desconto = desconto - 0.5

    # def historico_variacao_array(self, dias):
    #     if dias is None:
    #         data = date.today() - timedelta(days=self.dias_calculo)
    #     else:
    #         data = date.today() - timedelta(dias)
    #     return 10
    #     #total_historico =  HistoricoAtivo.objects.values('variacao_dia').filter(ativo=self,variacao_dia__isnull=False,data__gte=data)
    #     #lista_vaiacao =  [historico.variacao_dia for historico in total_historico]

    def get_absolute_url(self):
        return reverse("core:ativo-detail", args=[str(self.codigo)])

    def __str__(self):
        return self.codigo

    def save(self, *args, **kwargs):
        desconto = self.calcula_desconto_ativo()
        if desconto is not None:
            self.desconto_calculado = desconto
        else:
            self.desconto_calculado = 0

        super(Ativos, self).save(*args, **kwargs)

class HistoricoAtivo(models.Model):
    ''' Dados histórico de cada ativo.
    '''
    # Data do dia
    data = models.DateTimeField(verbose_name='Data')
    # Ativo
    ativo = models.ForeignKey(Ativos, on_delete=models.CASCADE)
    # Valor de abertura do dia, pode ser nulo pois existem hostórico incompleto
    valor_abertura = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Valor abertura',
                                        blank=True, null=True)
    # Valor de fechamento do ativo, é utilizado para calcular a variação do ativo no próximo dia.
    valor_fechamento = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Valor fechamento',
                                        blank=True, null=True)

    valor_maxima = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Valor máxima',
                                        blank=True, null=True)
    valor_minima = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Valor mínima',
                                        blank=True, null=True)

    # Diferença entre a mínima e o valor de fechamento
    diff_minima_fechamento = models.DecimalField(max_digits=10, decimal_places=2,
                            verbose_name='Diferença entre a mínina e fechamento', blank=True, null=True)
    # Para calculo de DFM
    diff_minima_fechamento_dia_anterior = models.DecimalField(max_digits=10, decimal_places=2,
                            verbose_name='Diferença entre a mínina do dia e fechamento do dia anterior',
                            blank=True, null=True)

    # Variação em porcentagem do dia em relação ao fechamento do dia anterior.
    variacao_dia = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Variação do dia',
                                        blank=True, null=True)

    # Spreed (Subtração) entre a VARIAÇÃO da mínina e o fechamento do ativo 
    # com essa mesma variaçaõ da ibov no mesmo dia.
    # É utilizado contando quanto as vezes o ativo fechou abaixo ou acima do fechamento da IBOV.
    # e para medir a propabilidade que o ativo pode fechar em referência ao fechamento da IBOV.
    diferenca_variacao_com_ibov = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Diferença de variação com IBOV',
                                        blank=True, null=True)


    def diferenca_minina_fechamento_ibov(self):
        ''' Retorna a diferença da minina e fechamento da IBOV para mostrar na lista do ativo
        '''
        if Ativos.objects.filter(codigo='IBOV').exists():
            ibov = Ativos.objects.get(codigo='IBOV')
            try:
                return HistoricoAtivo.objects.values("diff_minima_fechamento").get(ativo=ibov.id, data=self.data)["diff_minima_fechamento"]
            except Exception as e:
                return 'N/A'

    def diferenca_fechamento_minina_ibov(self):
        ''' Retorna a diferença do fechamento da IBOV do dia anterior
            com a mínima do dia
        '''

        if Ativos.objects.filter(codigo='IBOV').exists():
            ibov = Ativos.objects.get(codigo='IBOV')
            try:
                return HistoricoAtivo.objects.values("diff_minima_fechamento_dia_anterior").get(ativo=ibov.id, data=self.data)["diff_minima_fechamento_dia_anterior"]
            except Exception as e:
                return 'N/A'

    def comparacao_minina_fechamento_ibov(self):
        ''' Compara e retorna a subtração da
            diferença da minina e fechamento entre ação e a IBOV.
            Se o ativo variar entre a mínina e o fechamento mais
            que o a mínina e o fechmamento da IBOV.
            significa que o ativo se recupera ao longo do pregão.
        '''

        if Ativos.objects.filter(codigo='IBOV').exists():
            ibov = Ativos.objects.get(codigo='IBOV')
            try:
                ibov_hist_data = HistoricoAtivo.objects.values("diff_minima_fechamento").get(ativo=ibov.id, data=self.data)
                if self.diff_minima_fechamento > ibov_hist_data["diff_minima_fechamento"]:
                    return 1
                else:
                    return 0
            except Exception as e:
                return 'N/A'


    def comparacao_diferenca_ibov_com_desconto(self):
        ''' Calcula o valor com desconto aplicado
            em cima do valor de fechamento do ativo
            tendo como referência a soma da variação
            do ativo e da IBOV no memso dia
        '''
        if self.diferenca_variacao_com_ibov is not None:
            if self.ativo.desconto_calculado < self.diferenca_variacao_com_ibov:
                return 1
            else:
                return 0

    def variacao_IBOV(self):
        ''' Mostra a variação do dia da IBOV
            no mesmo dia do ativo
        '''
        ibov = Ativos.objects.get(codigo='IBOV')
        if HistoricoAtivo.objects.filter(ativo=ibov, data=self.data).exists():
            dia_ibov = HistoricoAtivo.objects.filter(ativo=ibov, data=self.data)
            return dia_ibov[0].variacao_dia
        else:
            return 'N/A'

    def get_absolute_url(self):
        return reverse("core:ativo-detail", args=[str(self.id)])

    def __str__(self):
        return self.ativo.codigo + str(self.data)
        
    class Meta:
        verbose_name = 'Histórico do ativo'
        constraints = [
            models.UniqueConstraint(fields=['ativo', 'data'], name='unique_data_por_ativo')
        ]

class SwingTrade(models.Model):
    codigo = models.ForeignKey(Ativos, on_delete=models.SET_NULL, blank=True, null=True)
    quantidade = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Quantidade', blank=True, null=True)
    valor = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Valor', blank=True, null=True)
    data_acao = models.DateTimeField(verbose_name='Data da Swing Trade')
    parentID = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True, parent_link=True)
    vendido = models.BooleanField(default=False, blank=True, null=True)

    tipo_movimentacao = models.CharField(max_length=10, choices=LISTA_TIPO_MOV)

    def valor_total_operacao(self):
        return '%.2f' % (self.quantidade * self.valor)

    def resultado_operacao(self):
        if self.parentID:
            return '%.2f' % ((self.valor - self.parentID.valor) * self.quantidade)
        else:
            return 0
    
    def diferencao_valor_venda(self):
        if self.tipo_movimentacao == 'venda':
            return '%.2f' % ((self.quantidade * self.valor) - (self.quantidade * self.parentID.valor))
        else:
            return 0

    def valida_venda_operacao(self):
        ''' Metedo para tornar o campo parentID obrigatorio ser for uma compra.
        '''
        if self.tipo_movimentacao == 'venda':
            # Para toda venda, tem quem que ter a ação comprada
            if self.parentID is None:
                raise ValidationError('Para venda, o campo Movimentação pai é obrigatório', code='invalid')
            # Para toda venda, verifica se já foi vendida todas as ações
            if self.parentID is not None:
                swing_filhas = SwingTrade.objects.filter(parentID=self.parentID.id)
                swing_pai = SwingTrade.objects.get(id=self.parentID.id)
                soma_quantidadade = 0
                # Se ja tem algum swing trade de venda de uma compra, soma a quantidade
                for swing in swing_filhas:
                    soma_quantidadade += swing.quantidade
                # Por fim, soma a quantidade da venda atual
                soma_quantidadade += self.quantidade
                if soma_quantidadade == swing_pai.quantidade:
                    swing_pai.vendido = 1
                    swing_pai.save()


    #//TODO Criar função queryse que mostra soma e venda no mes para Swing trade
    # meses_dict = {}
    # soma = 0
    # meses = Movimentacao.objects.dates('data_acao', 'month', order='DESC')
    # for m in meses:
    #     meses_dict[m.month] = Movimentacao.objects.filter(data_acao__month=m.month, tipo_movimentacao='venda')

    # for mes, rm in meses_dict.items():
    #     soma = 0
    #     for m in rm:
    #         soma = soma + (m.valor * m.quantidade)
    #     meses_dict[mes] = soma


    def save(self, *args, **kwargs):
        self.valida_venda_operacao()
        super(SwingTrade, self).save(*args, **kwargs)
    
    def __str__(self):
        return format("%s - %s - %s" % (self.codigo, str(self.quantidade), str(self.tipo_movimentacao)))

    def get_absolute_url(self):
        return reverse("core:swing-detail", args=[str(self.id)])

    class Meta:
        verbose_name = 'Compra e Venda'

class DayTrade(models.Model):
    data_acao = models.DateTimeField(verbose_name='Data da movimentação')

    descricao = models.CharField(max_length=2000, verbose_name='Descrição', blank=True, null=True)

    corretora = models.CharField(max_length=200, choices=LISTA_CORRETORA, verbose_name='Corretora')

    tipo_bolsa = models.CharField(max_length=20, choices=LISTA_BOLSA)

    #valor_liquido = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Valor líquido')

    valor_bruto = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Valor bruto',
                                        blank=True, null=True)

    taxas = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Taxas',
                                    blank=True, null=True)

    emulentos = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Emulentos',
                                    blank=True, null=True)
    
    corretagem = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Emulentos', default=0)

    irrf = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='IR retido na fonte',
                                blank=True, null=True)
   
    
    def valor_liquido(self):
        return self.valor_bruto - self.taxas - self.emulentos - self.corretagem - self.irrf

    def ir_day_trade(self):
        ''' Método para calcular resultado do day trade
        '''
       
        if self.valor_bruto is not None:
            valor_liquido = self.valor_bruto - self.taxas - self.emulentos
            if self.valor_bruto <= 0:
                return self.valor_bruto
            else:
                return '%.2f' % ((valor_liquido * 20) / 100 )


    def get_absolute_url(self):
        return reverse("core:day-detail", args=[str(self.id)])

    def __str__(self):
        return format("%s / %s / %s - %s - %s" % (self.data_acao.day, self.data_acao.month, self.data_acao.year,
                                                 str(self.tipo_bolsa), str(self.corretora)))

    class Meta:
        verbose_name = 'Day Trade'
        constraints = [
            models.UniqueConstraint(fields=['data_acao', 'tipo_bolsa', 'corretora'], name='unique_day_trade_dia')
        ]

class Conta(models.Model):
    conta = models.CharField(max_length=200, blank=False, verbose_name='Conta')
    empresa = models.CharField(max_length=200, blank=False, verbose_name='Empresa')
    dia_vencimento = models.IntegerField(verbose_name='Dia do vencimento')

    def get_absolute_url(self):
        return reverse("core:conta-detail", args=[str(self.id)])

    def __str__(self):
        return self.conta

    class Meta:
        verbose_name = 'Conta'

class Pagamento(models.Model):
    conta = models.ForeignKey(Conta, on_delete=models.PROTECT)
    user_own = models.ForeignKey(User, on_delete=models.PROTECT)
    valor = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Valor')
    data_pagamento = models.DateTimeField(verbose_name='Data do pagamento')
    mes_vigente = models.IntegerField(verbose_name='Mês vigente do pagamento')
    ano_vigente = models.IntegerField(verbose_name='Ano vigente do pagamento')

    def save(self, *args, **kwargs):
        super(Pagamento, self).save(*args, **kwargs)
    
    def __str__(self):
        return self.conta.conta + "-" + str(self.data_pagamento.month)

    def get_absolute_url(self):
        return reverse("core:pagamento-detail", args=[str(self.id)])

    class Meta:
        verbose_name = 'Pagamentos'

class Receita(models.Model):

    tipo_receita = models.CharField(max_length=20, choices=LISTA_RECEITA)
    valor = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Valor')
    data_receita = models.DateField(auto_now=False, auto_now_add=False, verbose_name='Data da receita')

    def __str__(self):
        return self.tipo_receita + "-" + self.data_receita

    def get_absolute_url(self):
        return reverse("core:receita-detail", args=[str(self.id)])