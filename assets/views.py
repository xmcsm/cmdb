from django.shortcuts import render,get_object_or_404,HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
import json
from assets.models import Asset,Server,NetworkDevice,StorageDevice,SecurityDevice,Software,EventLog,NewAssetApprovalZone,SoftwareType,AssetType
from assets import asset_handler
from login.models import LoginLog,User
from utils.tools import login_required, post_required
from assets.asset_handler import ApproveAsset
from .forms import SoftwareForm,AssetTypeForm

# Create your views here.

@csrf_exempt
def report(request):
    """
        通过csrf_exempt装饰器，跳过Django的csrf安全机制，让post的数据能被接收，但这又会带来新的安全问题。
        可以在客户端，使用自定义的认证token，进行身份验证。这部分工作，请根据实际情况，自己进行。
        :param request:
        :return:
        """
    print('report')
    print(request)
    if request.method == "POST":
        asset_data = request.POST.get('asset_data')
        data = json.loads(asset_data)
        # 各种数据检查，请自行添加和完善！
        if not data:
            return HttpResponse("没有数据！")
        if not issubclass(dict, type(data)):
            return HttpResponse("数据必须为字典格式！")
        # 是否携带了关键的sn号
        sn = data.get('sn', None)
        if sn:
            # 进入审批流程
            # 首先判断是否在上线资产中存在该sn
            asset_obj = Asset.objects.filter(sn=sn)
            if asset_obj:
                # 进入已上线资产的数据更新流程
                update_asset = asset_handler.UpdateAsset(request, asset_obj[0], data)
                return HttpResponse("资产数据已经更新！")
            else:  # 如果已上线资产中没有，那么说明是未批准资产，进入新资产待审批区，更新或者创建资产。
                obj = asset_handler.NewAsset(request, data)
                response = obj.add_to_new_assets_zone()
                return HttpResponse(response)
        else:
            return HttpResponse("没有资产sn序列号，请检查数据！")
    return HttpResponse('200 ok')

def event_log(name, event_type, asset, new_asset, component, detail, user, address, useragent, memo=None):
    event = EventLog()
    event.name = name
    event.event_type = event_type
    event.asset = asset
    event.new_asset = new_asset
    event.component = component
    event.detail = detail
    event.user = user
    event.address = address
    event.useragent = useragent
    event.memo = memo
    event.save()

@login_required
def index(request):
    # assets = get_list_or_404(Asset)
    total = Asset.objects.count()
    if total == 0:  # 访问系统无数据时, 0 做除数报错
        total = 1
    upline = Asset.objects.filter(status=0).count()
    offline = Asset.objects.filter(status=1).count()
    unknown = Asset.objects.filter(status=2).count()
    breakdown = Asset.objects.filter(status=3).count()
    backup = Asset.objects.filter(status=4).count()
    up_rate = round(upline / total * 100)
    o_rate = round(offline / total * 100)
    un_rate = round(unknown / total * 100)
    bd_rate = round(breakdown / total * 100)
    bu_rate = round(backup / total * 100)
    server_number = Server.objects.count()
    networkdevice_number = NetworkDevice.objects.count()
    storagedevice_number = StorageDevice.objects.count()
    securitydevice_number = SecurityDevice.objects.count()
    software_number = Software.objects.count()
    return render(request, 'assets/index.html', locals())

@login_required
def NewAsset_assets(request):
    newassets = NewAssetApprovalZone.objects.all()
    return render(request,'assets/newasset.html',locals())

def NewAsset_detail(request):
    assets_id = request.GET.get('assets_id')
    newasset = NewAssetApprovalZone.objects.get(pk=assets_id)
    newasset.__dict__.pop('_state')
    newasset.__dict__['asset_type_display'] = newasset.get_asset_type_name()
    data = {}
    data['status'] = 'SUCCESS'
    data['newasset'] = newasset.__dict__
    print(data)
    return JsonResponse(data)

@login_required
@post_required
def delete_newasset_assets(request):
    pk = request.POST.get('id')
    asset = get_object_or_404(NewAssetApprovalZone, pk=pk)
    asset_name = asset.get_asset_type_name()
    asset_sn = asset.sn
    asset.delete()
    name = "删除待审批资产"
    event_type = 7
    asset = None
    new_asset = None
    component = None
    detail = "删除待审批资产：{0}_{1}".format(asset_name, asset_sn)
    username = request.session.get('username')
    user = User.objects.get(username=username)
    address = request.META.get('REMOTE_ADDR', None)
    useragent = request.META.get('HTTP_USER_AGENT', None)
    event_log(name, event_type, asset, new_asset, component, detail, user, address, useragent)
    return JsonResponse({"code": 200, "err": ""})

@login_required
@post_required
def approval_newasset_assets(request):
    pks = request.POST.get('id').split(',')
    username = request.session.get('username')
    user = User.objects.get(username=username)
    success_upline_number = 0
    for pk in pks:
        obj = asset_handler.ApproveAsset(user, pk)
        ret = obj.asset_upline()
        if ret:
            success_upline_number += 1
    return JsonResponse({"code": 200, "err": ""})

@login_required
def hardware_assets(request):
    # assets = get_list_or_404(Asset)
    assets = Asset.objects.all()
    return render(request, 'assets/hardware.html', locals())

@login_required
@post_required
def delete_hardware_assets(request):
    pk = request.POST.get('id')
    asset = get_object_or_404(Asset, pk=pk)
    asset_name = asset.name
    asset_sn = asset.sn
    asset.delete()
    name = "删除硬件资产"
    event_type = 3
    asset = None
    new_asset = None
    component = None
    detail = "删除硬件资产：{0}_{1}".format(asset_name, asset_sn)
    username = request.session.get('username')
    user = User.objects.get(username=username)
    address = request.META.get('REMOTE_ADDR', None)
    useragent = request.META.get('HTTP_USER_AGENT', None)
    event_log(name, event_type, asset, new_asset, component, detail, user, address, useragent)
    return JsonResponse({"code": 200, "err": ""})

@login_required
@post_required
def add_hardware_assets(request):
    pass
    return JsonResponse({"code": 200, "err": ""})

@login_required
def software_assets(request):
    # assets = get_list_or_404(Asset)
    assets = Software.objects.all()
    softwaretype = SoftwareType.objects.all()
    return render(request, 'assets/software.html', locals())

# @csrf_exempt
@login_required
@post_required
def delete_software_assets(request):
    pk = request.POST.get('id')
    asset = get_object_or_404(Software, pk=pk)
    asset_id = asset.id
    asset_version = asset.version
    asset.delete()
    name = "删除软件资产"
    event_type = 8
    asset = None
    new_asset = None
    component = None
    detail = "删除软件资产：{0}_{1}".format(asset_id, asset_version)
    username = request.session.get('username')
    user = User.objects.get(username=username)
    address = request.META.get('REMOTE_ADDR', None)
    useragent = request.META.get('HTTP_USER_AGENT', None)
    event_log(name, event_type, asset, new_asset, component, detail, user, address, useragent)
    return JsonResponse({"code": 200, "err": ""})

@login_required
@post_required
def add_software_assets(request):
    softwareform = SoftwareForm(request.POST)
    if softwareform.is_valid():
        if Software.objects.filter(version=softwareform.cleaned_data.get('version')).count() > 0:
            error_message = '{} 已存在!'.format(softwareform.cleaned_data.get('version'))
            return JsonResponse({"code": 400, "err": error_message})
        software = Software()
        software.software_type_id = int(softwareform.cleaned_data.get('subassettype'))
        software.license_num = int(softwareform.cleaned_data.get('licensenum'))
        software.version = softwareform.cleaned_data.get('version')
        software.save()
        name = "新增软件资产"
        event_type = 8
        asset = None
        new_asset = None
        component = None
        detail = "新增软件资产：{0}".format(software.version)
        username = request.session.get('username')
        user = User.objects.get(username=username)
        address = request.META.get('REMOTE_ADDR', None)
        useragent = request.META.get('HTTP_USER_AGENT', None)
        event_log(name, event_type, asset, new_asset, component, detail, user, address, useragent)
        return JsonResponse({"code": 200, "pk":software.pk, "err": ""})
    else:
        error_message = '请检查填写的内容!'
        return JsonResponse({"code": 401,"err": error_message})


@login_required
def detail(request, asset_id):
    # assets = get_list_or_404(Asset)
    asset = get_object_or_404(Asset, id=asset_id)
    return render(request, 'assets/detail.html', locals())


@login_required
def operation(request):
    events = EventLog.objects.all()
    return render(request, 'assets/audit_operation.html', locals())


@login_required
def audit_login(request):
    # assets = get_list_or_404(Asset)
    events = LoginLog.objects.all()
    return render(request, 'assets/audit_login.html', locals())

@login_required
def AssetType_list(request):
    # assets = get_list_or_404(Asset)
    assettypes = AssetType.objects.all()
    return render(request, 'assets/asset_type.html', locals())

@login_required
def AssetType_delete(request):
    pk = request.POST.get('id')
    assettype = get_object_or_404(AssetType, pk=pk)
    assettype_id = assettype.id
    type_id = assettype.type_id
    type_name = assettype.type_name
    assettype.delete()
    name = "删除资产类型"
    event_type = 9
    asset = None
    new_asset = None
    component = None
    detail = "删除资产类型：{0}_{1}_{2}".format(assettype_id,type_id, type_name)
    username = request.session.get('username')
    user = User.objects.get(username=username)
    address = request.META.get('REMOTE_ADDR', None)
    useragent = request.META.get('HTTP_USER_AGENT', None)
    event_log(name, event_type, asset, new_asset, component, detail, user, address, useragent)
    return JsonResponse({"code": 200, "err": ""})

@post_required
@login_required
def AssetType_add(request):
    assettypeform = AssetTypeForm(request.POST)
    print(assettypeform)
    if assettypeform.is_valid():
        type_id = assettypeform.cleaned_data.get('type_id')
        if AssetType.objects.filter(type_id=type_id).count() > 0:
            error_message = '{} 已存在!'.format(assettypeform.cleaned_data.get('type_id'))
            return JsonResponse({"code": 400, "err": error_message})
        assettype = AssetType()
        assettype.type_name = assettypeform.cleaned_data.get('type_name')
        assettype.type_id = assettypeform.cleaned_data.get('type_id')
        assettype.save()
        name = "新增资产类型"
        event_type = 9
        asset = None
        new_asset = None
        component = None
        detail = "新增资产类型：{0}-{1}".format(assettype.type_id,assettype.type_name)
        username = request.session.get('username')
        user = User.objects.get(username=username)
        address = request.META.get('REMOTE_ADDR', None)
        useragent = request.META.get('HTTP_USER_AGENT', None)
        event_log(name, event_type, asset, new_asset, component, detail, user, address, useragent)
        return JsonResponse({"code": 200, "pk": assettype.pk, "err": ""})
    else:
        error_message = '请检查填写的内容!'
        return JsonResponse({"code": 401, "err": error_message})
