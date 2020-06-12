from django import forms


class SoftwareForm(forms.Form):
    subassettype = forms.IntegerField(label="软件类型")
    licensenum = forms.IntegerField(label="授权数量")
    version = forms.CharField(label="软件/系统版本", min_length=1, max_length=64)

class AssetTypeForm(forms.Form):
    type_id = forms.CharField(label="资产类型编码", min_length=1, max_length=64)
    type_name = forms.CharField(label="资产类型", min_length=1, max_length=64)
