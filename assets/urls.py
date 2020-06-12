from django.urls import path
from assets import views

app_name = 'assets'

urlpatterns = [
    path('', views.index, name='index'),
    path('assets/report/', views.report, name='report'),
    path('newassets/', views.NewAsset_assets, name='newassets'),
    path('newassets/detail', views.NewAsset_detail, name='newassets_detail'),
    path('newassets/del', views.delete_newasset_assets, name='newassets_delete'),
    path('newassets/approval', views.approval_newasset_assets, name='newassets_approval'),
    path('hardware/', views.hardware_assets, name='hardware'),
    path('hardware/del/', views.delete_hardware_assets, name='hardware_delete'),
    path('hardware/add/', views.add_hardware_assets, name='hardware_add'),
    path('software/', views.software_assets, name='software'),
    path('software/del/', views.delete_software_assets, name='software_delete'),
    path('software/add/', views.add_software_assets, name='software_add'),
    path('detail/<int:asset_id>/', views.detail, name='detail'),
    path('audit/operation/', views.operation, name='operation'),
    path('audit/login/', views.audit_login, name='audit_login'),
    path('assettype/', views.AssetType_list, name='assettype_list'),
    path('assettype/del', views.AssetType_delete, name='assettype_delete'),
    path('assettype/add', views.AssetType_add, name='assettype_add'),

]