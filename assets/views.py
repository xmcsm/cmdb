from django.shortcuts import render,get_object_or_404,HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.apps import apps
from django.core import serializers
import json
from assets.models import Asset,Server,NetworkDevice,StorageDevice,SecurityDevice,Software,EventLog,NewAssetApprovalZone,SoftwareType,AssetType,SubordinateUnits
from assets import asset_handler
from login.models import LoginLog,User
from utils.tools import login_required, post_required
from assets.asset_handler import ApproveAsset
from .forms import SoftwareForm,AssetTypeForm,SoftwareTypeForm,SubordinateUnitsForm,SoftwareUpdateForm

# Create your views here.

@csrf_exempt
def report(request):
    """
        通过csrf_exempt装饰器，跳过Django的csrf安全机制，让post的数据能被接收，但这又会带来新的安全问题。
        可以在客户端，使用自定义的认证token，进行身份验证。这部分工作，请根据实际情况，自己进行。
        :param request:
        :return:
        """
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
    '''
    日志保存
    :param name:
    :param event_type:
    :param asset:
    :param new_asset:
    :param component:
    :param detail:
    :param user:
    :param address:
    :param useragent:
    :param memo:
    :return:
    '''
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

    types = AssetType.objects.all()
    type_name_list = []
    type_count_list = []
    for type in types:
        type_data = {}
        type_name_list.append(type.type_name)
        type_data['name'] = type.type_name
        model_obj = apps.get_model('assets',type.type_id)
        type_data['value'] = model_obj.objects.count()
        type_count_list.append(type_data)
    print(type_name_list)
    print(type_count_list)
    server_number = Server.objects.count()
    networkdevice_number = NetworkDevice.objects.count()
    storagedevice_number = StorageDevice.objects.count()
    securitydevice_number = SecurityDevice.objects.count()
    software_number = Software.objects.count()
    return render(request, 'assets/index.html', locals())

# 待审批资产列表
@login_required
def NewAsset_assets(request):
    newassets = NewAssetApprovalZone.objects.all()
    return render(request,'assets/newasset.html',locals())

# 待审批资产详细信息
def NewAsset_detail(request):
    assets_id = request.GET.get('assets_id')
    newasset = NewAssetApprovalZone.objects.get(pk=assets_id)
    newasset.__dict__.pop('_state')
    newasset.__dict__['asset_type_display'] = newasset.get_asset_type_name()
    data = {}
    data['status'] = 'SUCCESS'
    data['newasset'] = newasset.__dict__
    return JsonResponse(data)

# 删除待审批资产
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

# 审批待审批资产
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

# 硬件资产列表
@login_required
def hardware_assets(request):
    # assets = get_list_or_404(Asset)
    assets = Asset.objects.all()
    return render(request, 'assets/hardware.html', locals())

# 删除硬件资产
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

# 新增硬件资产
@login_required
@post_required
def add_hardware_assets(request):
    pass
    return JsonResponse({"code": 200, "err": ""})

# 详细硬件资产
@login_required
def detail(request, asset_id):
    # assets = get_list_or_404(Asset)
    asset = get_object_or_404(Asset, id=asset_id)
    return render(request, 'assets/detail.html', locals())

# 业务系统列表
@login_required
def software_assets(request):
    # assets = get_list_or_404(Asset)
    assets = Software.objects.all()
    softwaretype = SoftwareType.objects.all()
    return render(request, 'assets/software.html', locals())

@login_required
def software_detail(request):
    if request.method == 'POST':
        softwareform = SoftwareUpdateForm(request.POST)
        if softwareform.is_valid():
            if Software.objects.filter(soft_name=softwareform.cleaned_data.get('soft_name')).count() > 0:
                status_code = '400'
                message = '系统名称[{0}]已存在!'.format(softwareform.cleaned_data.get('soft_name'))
                return render(request, 'assets/software_add.html', locals())
            status_code = '200'
            message = '新增成功！'
            new_software = softwareform.save(commit=False)
            new_software.save()

            assets_list = softwareform.cleaned_data.get('assets')
            for asset in assets_list:
                new_software.assets.add(asset)
            new_software.save()

            name = "新增业务系统"
            event_type = 8
            asset = None
            new_asset = None
            component = None
            detail = "新增业务系统：{0}".format(new_software.soft_name)
            username = request.session.get('username')
            user = User.objects.get(username=username)
            address = request.META.get('REMOTE_ADDR', None)
            useragent = request.META.get('HTTP_USER_AGENT', None)
            event_log(name, event_type, asset, new_asset, component, detail, user, address, useragent)
        else:
            status_code = '400'
            message = '请检查填写的内容!'
    else:
        softwareform = SoftwareForm()
    return render(request, 'assets/software_add.html', locals())

def save_software(request,form_data):
    software = Software()
    software.soft_name = form_data.cleaned_data.get('soft_name')
    software.software_type = form_data.cleaned_data.get('software_type')
    software.units = form_data.cleaned_data.get('units')

    software.balanc_url = form_data.cleaned_data.get('balanc_url')
    software.all_url = form_data.cleaned_data.get('all_url')
    software.program_path = form_data.cleaned_data.get('program_path')
    software.domain_path = form_data.cleaned_data.get('domain_path')
    software.account_info = form_data.cleaned_data.get('account_info')
    software.save()
    assets_list = form_data.cleaned_data.get('assets')
    for asset in assets_list:
        software.assets.add(asset)
    software.save()
    name = "新增业务系统"
    event_type = 8
    asset = None
    new_asset = None
    component = None
    detail = "新增业务系统：{0}".format(software.soft_name)
    username = request.session.get('username')
    user = User.objects.get(username=username)
    address = request.META.get('REMOTE_ADDR', None)
    useragent = request.META.get('HTTP_USER_AGENT', None)
    event_log(name, event_type, asset, new_asset, component, detail, user, address, useragent)
    return software

@login_required
def software_update(request,soft_id):
    software = get_object_or_404(Software,pk=soft_id)
    if request.method == 'POST':
        softwareform = SoftwareUpdateForm(instance=software,data=request.POST)
        if softwareform.is_valid():
            if Software.objects.filter(soft_name=softwareform.cleaned_data.get('soft_name')).count() > 0:
                softwares = Software.objects.filter(soft_name=softwareform.cleaned_data.get('soft_name'))
                for sw in softwares:
                    if sw.pk != soft_id:
                        status_code = '400'
                        message = '系统名称[{0}]已存在!'.format(softwareform.cleaned_data.get('soft_name'))
                        return render(request, 'assets/software_detail.html', locals())
            status_code = '200'
            message = '修改成功！'
            softwareform.save()
            software = get_object_or_404(Software, pk=soft_id)
            name = "修改业务系统"
            event_type = 8
            asset = None
            new_asset = None
            component = None
            detail = "修改业务系统：{0}".format(software.soft_name)
            username = request.session.get('username')
            user = User.objects.get(username=username)
            address = request.META.get('REMOTE_ADDR', None)
            useragent = request.META.get('HTTP_USER_AGENT', None)
            event_log(name, event_type, asset, new_asset, component, detail, user, address, useragent)
        else:
            status_code = '400'
            message = '请检查填写的内容!'
    else:
        status_code = '201'
        message = '开始修改！'
        softwareform = SoftwareUpdateForm(instance=software)
    return render(request, 'assets/software_detail.html', locals())

# 删除业务系统
# @csrf_exempt
@login_required
@post_required
def delete_software_assets(request):
    pk = request.POST.get('id')
    asset = get_object_or_404(Software, pk=pk)
    soft_id = asset.id
    soft_name = asset.soft_name
    asset.delete()
    name = "删除业务系统"
    event_type = 8
    asset = None
    new_asset = None
    component = None
    detail = "删除业务系统：{0}_{1}".format(soft_id, soft_name)
    username = request.session.get('username')
    user = User.objects.get(username=username)
    address = request.META.get('REMOTE_ADDR', None)
    useragent = request.META.get('HTTP_USER_AGENT', None)
    event_log(name, event_type, asset, new_asset, component, detail, user, address, useragent)
    return JsonResponse({"code": 200, "err": ""})

# 添加业务系统
@login_required
@post_required
def add_software_assets(request):
    softwareform = SoftwareForm(request.POST)
    if softwareform.is_valid():
        if Software.objects.filter(soft_name=softwareform.cleaned_data.get('soft_name')).count() > 0:
            error_message = '{} 已存在!'.format(softwareform.cleaned_data.get('soft_name'))
            return JsonResponse({"code": 400, "err": error_message})

        software = save_software(request,softwareform)

        return JsonResponse({"code": 200, "pk":software.pk, "err": ""})
    else:
        error_message = '请检查填写的内容!'
        return JsonResponse({"code": 401,"err": error_message})



@login_required
def operation(request):
    events = EventLog.objects.all().order_by('-date')
    return render(request, 'assets/audit_operation.html', locals())


@login_required
def audit_login(request):
    # assets = get_list_or_404(Asset)
    events = LoginLog.objects.all()
    return render(request, 'assets/audit_login.html', locals())

@login_required
def AssetType_list(request):
    # assets = get_list_or_404(Asset)
    assettypes = AssetType.objects.all().order_by('pk')
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

@post_required
@login_required
def AssetType_update(request):
    assettypeform = AssetTypeForm(request.POST)

    if assettypeform.is_valid():
        obj_id = request.POST.get('obj_id')
        if AssetType.objects.filter(pk=obj_id).exists():
            assettype = AssetType.objects.get(pk=obj_id)
            assettype.type_name = assettypeform.cleaned_data.get('type_name')
            assettype.type_id = assettypeform.cleaned_data.get('type_id')
            assettype.save()
            name = "修改资产类型"
            event_type = 9
            asset = None
            new_asset = None
            component = None
            detail = "修改资产类型：{0}-{1}".format(assettype.type_id,assettype.type_name)
            username = request.session.get('username')
            user = User.objects.get(username=username)
            address = request.META.get('REMOTE_ADDR', None)
            useragent = request.META.get('HTTP_USER_AGENT', None)
            event_log(name, event_type, asset, new_asset, component, detail, user, address, useragent)
            return JsonResponse({"code": 200, "pk": obj_id, "err": ""})
        else:
            error_message = '{} 已存在!'.format(assettypeform.cleaned_data.get('type_id'))
            return JsonResponse({"code": 400, "err": error_message})
    else:
        error_message = '请检查填写的内容!'
        return JsonResponse({"code": 401, "err": error_message})


@login_required
def SoftwareType_list(request):
    # assets = get_list_or_404(Asset)
    softwaretypes = SoftwareType.objects.all().order_by('pk')
    return render(request, 'assets/software_type.html', locals())

@login_required
def SoftwareType_delete(request):
    pk = request.POST.get('id')
    softwaretype = get_object_or_404(SoftwareType, pk=pk)
    softwaretype_id = softwaretype.id
    type_name = softwaretype.type_name
    softwaretype.delete()
    name = "删除软件类型"
    event_type = 10
    asset = None
    new_asset = None
    component = None
    detail = "删除软件类型：{0}_{1}".format(softwaretype_id, type_name)
    username = request.session.get('username')
    user = User.objects.get(username=username)
    address = request.META.get('REMOTE_ADDR', None)
    useragent = request.META.get('HTTP_USER_AGENT', None)
    event_log(name, event_type, asset, new_asset, component, detail, user, address, useragent)
    return JsonResponse({"code": 200, "err": ""})

@post_required
@login_required
def SoftwareType_add(request):
    softwaretypeform = SoftwareTypeForm(request.POST)
    if softwaretypeform.is_valid():
        type_name = softwaretypeform.cleaned_data.get('type_name')
        if SoftwareType.objects.filter(type_name=type_name).count() > 0:
            error_message = '{} 已存在!'.format(softwaretypeform.cleaned_data.get('type_name'))
            return JsonResponse({"code": 400, "err": error_message})
        softwaretype = SoftwareType()
        softwaretype.type_name = softwaretypeform.cleaned_data.get('type_name')
        softwaretype.save()
        name = "新增软件类型"
        event_type = 10
        asset = None
        new_asset = None
        component = None
        detail = "新增软件类型：{0}".format(softwaretype.type_name)
        username = request.session.get('username')
        user = User.objects.get(username=username)
        address = request.META.get('REMOTE_ADDR', None)
        useragent = request.META.get('HTTP_USER_AGENT', None)
        event_log(name, event_type, asset, new_asset, component, detail, user, address, useragent)
        return JsonResponse({"code": 200, "pk": softwaretype.pk, "err": ""})
    else:
        error_message = '请检查填写的内容!'
        return JsonResponse({"code": 401, "err": error_message})

@post_required
@login_required
def SoftwareType_update(request):
    softwaretypeform = SoftwareTypeForm(request.POST)
    if softwaretypeform.is_valid():
        obj_id = request.POST.get('obj_id')
        if SoftwareType.objects.filter(pk=obj_id).exists():
            softwaretype = SoftwareType.objects.get(pk=obj_id)
            softwaretype.type_name = softwaretypeform.cleaned_data.get('type_name')
            softwaretype.save()
            name = "修改软件类型"
            event_type = 10
            asset = None
            new_asset = None
            component = None
            detail = "修改软件类型：{0}".format(softwaretype.type_name)
            username = request.session.get('username')
            user = User.objects.get(username=username)
            address = request.META.get('REMOTE_ADDR', None)
            useragent = request.META.get('HTTP_USER_AGENT', None)
            event_log(name, event_type, asset, new_asset, component, detail, user, address, useragent)
            return JsonResponse({"code": 200, "pk": obj_id, "err": ""})
        else:
            error_message = '{} 已存在!'.format(softwaretypeform.cleaned_data.get('type_name'))
            return JsonResponse({"code": 400, "err": error_message})
    else:
        error_message = '请检查填写的内容!'
        return JsonResponse({"code": 401, "err": error_message})

@login_required
def SubordinateUnits_list(request):
    # assets = get_list_or_404(Asset)
    subordinateunits = SubordinateUnits.objects.all().order_by('pk')
    return render(request, 'assets/subordinate_units.html', locals())

@login_required
def SubordinateUnits_delete(request):
    pk = request.POST.get('id')
    subordinateunits = get_object_or_404(SubordinateUnits, pk=pk)
    subordinateunits_id = subordinateunits.id
    subordinateunits_name = subordinateunits.name
    subordinateunits.delete()
    name = "删除所属单位"
    event_type = 11
    asset = None
    new_asset = None
    component = None
    detail = "删除所属单位：{0}_{1}".format(subordinateunits_id, subordinateunits_name)
    username = request.session.get('username')
    user = User.objects.get(username=username)
    address = request.META.get('REMOTE_ADDR', None)
    useragent = request.META.get('HTTP_USER_AGENT', None)
    event_log(name, event_type, asset, new_asset, component, detail, user, address, useragent)
    return JsonResponse({"code": 200, "err": ""})

@post_required
@login_required
def SubordinateUnits_add(request):
    subordinateunitsform = SubordinateUnitsForm(request.POST)
    if subordinateunitsform.is_valid():
        type_name = subordinateunitsform.cleaned_data.get('name')
        if SubordinateUnits.objects.filter(name=type_name).count() > 0:
            error_message = '{} 已存在!'.format(subordinateunitsform.cleaned_data.get('name'))
            return JsonResponse({"code": 400, "err": error_message})
        subordinateunits = SubordinateUnits()
        subordinateunits.name = subordinateunitsform.cleaned_data.get('name')
        subordinateunits.save()
        name = "新增所属单位"
        event_type = 11
        asset = None
        new_asset = None
        component = None
        detail = "新增所属单位：{0}".format(subordinateunits.name)
        username = request.session.get('username')
        user = User.objects.get(username=username)
        address = request.META.get('REMOTE_ADDR', None)
        useragent = request.META.get('HTTP_USER_AGENT', None)
        event_log(name, event_type, asset, new_asset, component, detail, user, address, useragent)
        return JsonResponse({"code": 200, "pk": subordinateunits.pk, "err": ""})
    else:
        error_message = '请检查填写的内容!'
        return JsonResponse({"code": 401, "err": error_message})

@post_required
@login_required
def SubordinateUnits_update(request):
    subordinateunitsform = SubordinateUnitsForm(request.POST)
    if subordinateunitsform.is_valid():
        obj_id = request.POST.get('obj_id')
        if SubordinateUnits.objects.filter(pk=obj_id).exists():
            subordinateunits = SubordinateUnits.objects.get(pk=obj_id)
            old_name = subordinateunits.name
            subordinateunits.name = subordinateunitsform.cleaned_data.get('name')
            subordinateunits.save()
            name = "修改所属单位"
            event_type = 10
            asset = None
            new_asset = None
            component = None
            detail = "修改所属单位：{0}-->{1}".format(old_name,subordinateunits.name)
            username = request.session.get('username')
            user = User.objects.get(username=username)
            address = request.META.get('REMOTE_ADDR', None)
            useragent = request.META.get('HTTP_USER_AGENT', None)
            event_log(name, event_type, asset, new_asset, component, detail, user, address, useragent)
            return JsonResponse({"code": 200, "pk": obj_id, "err": ""})
        else:
            error_message = '{} 已存在!'.format(subordinateunitsform.cleaned_data.get('name'))
            return JsonResponse({"code": 400, "err": error_message})
    else:
        error_message = '请检查填写的内容!'
        return JsonResponse({"code": 401, "err": error_message})