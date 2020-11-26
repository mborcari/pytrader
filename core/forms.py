from django.forms import ModelForm
from django import forms
from .models import Ativos, SwingTrade, DayTrade, Conta, Pagamento, Receita
from django.contrib.auth.models import User
from .choices import LISTA_BOLSA, LISTA_CORRETORA, LISTA_TIPO_MOV

# class BaseForm(ModelForm):
#     def __init__(self, *args, **kwargs):
#         super(BaseForm, self).__init__(*args, **kwargs)
#         # Superclasse adiconada, caso os campos não sejam declarados, aplica um stilo de CSS básico.
#         # for field_name, field in self.fields.items():
#         #     if type(field) == forms.CharField:
#         #         field.widget.attrs['class'] = 'form-control'


class UserForm(ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

class AtivoForm(ModelForm):
    class Meta:
        model = Ativos
        fields = '__all__'

class SwingForm(ModelForm):
    codigo = forms.ModelChoiceField(queryset=Ativos.objects.all(), label='Código')                     
    data_acao = forms.DateField(label='Data da movimentação')
    valor = forms.DecimalField(decimal_places=2, max_digits=10)
    quantidade = forms.DecimalField(decimal_places=2, max_digits=10)
    parentID = forms.ModelChoiceField(queryset=SwingTrade.objects.filter(tipo_movimentacao='compra', vendido=False),
        label='Movimentação Pai', required=False)
    vendido = forms.BooleanField(required=False)

    tipo_movimentacao = forms.ChoiceField(choices=LISTA_TIPO_MOV, label='Tipo do movimentação', initial='')

    # def clean_parentID(self):
    #     if self.data['tipo_movimentacao'] == 'venda':
    #         parentID = self.cleaned_data.get('parentID')
    #         if parentID is None:
    #             raise forms.ValidationError(_('Para venda, o campo Movimentação pai é obrigatório',
    #         code='invalid'))
    #         else:
    #             return parentID

    class Meta:
        model = SwingTrade
        fields = ['codigo', 'quantidade', 'tipo_movimentacao', 'valor', 'data_acao', 'parentID', 'vendido']
        error_messages = {
            'quantidade': {
                'required': ("Esse campo é obrigatório."),
            },
        }

class DayForm(ModelForm):             
    data_acao = forms.DateField(label='Data da movimentação')
    corretora = forms.ChoiceField(choices=LISTA_CORRETORA, label='Corretora', initial='terra')
    tipo_bolsa = forms.ChoiceField(choices=LISTA_BOLSA, label='Bolsa', initial='')
    valor_bruto = forms.DecimalField(decimal_places=2, max_digits=10)
    taxas = forms.DecimalField(decimal_places=2, max_digits=10, label='Taxa de liquidação')
    emulentos = forms.DecimalField(decimal_places=2, max_digits=10)
    irrf = forms.DecimalField(decimal_places=2, max_digits=10, label='Imposto')
    corretagem = forms.DecimalField(decimal_places=2, max_digits=10)
    descricao = forms.CharField(max_length=2000, required=False, widget=forms.Textarea)
    #valor_liquido = forms.DecimalField(decimal_places=2, max_digits=10)

    class Meta:
        model = DayTrade
        fields = ['data_acao', 'corretora', 'tipo_bolsa','valor_bruto', 'taxas', 'emulentos', 'irrf', 'corretagem','descricao']

class ContaForm(ModelForm):
    class Meta:
        model = Conta
        fields = '__all__'

class PagamentoForm(ModelForm):
    class Meta:
        model = Pagamento
        fields = '__all__'

class ReceitaForm(ModelForm):
    class Meta:
        model = Receita
        fields = '__all__'