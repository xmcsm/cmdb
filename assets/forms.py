from django import forms
from .models import SoftwareType,SubordinateUnits,Asset,Software


class SoftwareForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  # 初始化父类方法
        print(self.fields)
        for field in self.fields.values():
            field.widget.attrs = {'class': 'form-control','rows':'6'}

    soft_name = forms.CharField(label="系统名称", min_length=1, max_length=64)
    software_type = forms.ModelChoiceField(label='部署方式',queryset=SoftwareType.objects.all())
    units = forms.ModelChoiceField(label='所属单位',queryset=SubordinateUnits.objects.all())
    assets = forms.ModelMultipleChoiceField(label='部署服务器',queryset=Asset.objects.all())
    balanc_url = forms.CharField(label="访问地址", widget=forms.Textarea(attrs={'rows':'5'}))
    all_url = forms.CharField(label="各节点访问地址", widget=forms.Textarea(attrs={'rows':'5'}))
    program_path = forms.CharField(label="程序路径", widget=forms.Textarea(attrs={'rows':'5'}))
    domain_path = forms.CharField(label="域路径", widget=forms.Textarea(attrs={'rows':'5'}))
    account_info = forms.CharField(label="账号信息", widget=forms.Textarea(attrs={}))

class SoftwareUpdateForm(forms.ModelForm):
    class Meta:
        model = Software
        fields = ['soft_name','software_type','units','assets','balanc_url','all_url','program_path','domain_path','account_info']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  # 初始化父类方法
        print(self.fields)
        for field in self.fields.values():
            field.widget.attrs = {'class': 'form-control','rows':'6'}

class AssetTypeForm(forms.Form):
    type_id = forms.CharField(label="资产类型编码", min_length=1, max_length=64)
    type_name = forms.CharField(label="资产类型", min_length=1, max_length=64)

class SoftwareTypeForm(forms.Form):
    type_name = forms.CharField(label="软件类型", min_length=1, max_length=64)

class SubordinateUnitsForm(forms.Form):
    name = forms.CharField(label="单位名称", min_length=1, max_length=64)
