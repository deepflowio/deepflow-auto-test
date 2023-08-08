# coding: utf-8

import json
import time
import os
import requests

from aliyunsdkcore import client
from aliyunsdkecs.request.v20140526.CreateInstanceRequest import CreateInstanceRequest
from aliyunsdkecs.request.v20140526.DescribeInstancesRequest import DescribeInstancesRequest
from aliyunsdkecs.request.v20140526.StartInstanceRequest import StartInstanceRequest
from aliyunsdkecs.request.v20140526.DeleteInstanceRequest import DeleteInstanceRequest
from aliyunsdkecs.request.v20140526.StopInstanceRequest import StopInstanceRequest
from aliyunsdkecs.request.v20140526.ModifyInstanceAttributeRequest import ModifyInstanceAttributeRequest
from aliyunsdkcore.acs_exception.exceptions import ServerException, ClientException
from aliyunsdkvpc.request.v20160428 import CreateVpcRequest
from aliyunsdkvpc.request.v20160428 import CreateVSwitchRequest
from aliyunsdkvpc.request.v20160428 import DeleteVSwitchRequest
from aliyunsdkvpc.request.v20160428 import DeleteVpcRequest
from aliyunsdkvpc.request.v20160428 import DescribeVSwitchAttributesRequest
from aliyunsdkvpc.request.v20160428 import DescribeVpcAttributeRequest
from aliyunsdkcore.client import AcsClient
from aliyunsdkvpc.request.v20160428 import ModifyVpcAttributeRequest

from common import common_config
from common.ssh import ssh_pool
from common import logger
from common.cmd import run_cmd

log = logger.getLogger()

# generate access key by aliyun ID and SECRET
clt = None
ali_vm_password_default = "Yunshan3302!"


def get_acsclient():
    global clt
    if not clt:
        clt = client.AcsClient(os.environ.get('ALICLOUD_ACCESS_KEY'),
                               os.environ.get('ALICLOUD_SECRET_KEY'),
                               os.environ.get('ALICLOUD_REGION'))
    return clt


def create_instances_by_deploy(
        uuid,
        instance_names,
        image_id=common_config.ali_image_centos7_419_id,
        instance_type=common_config.ali_instance_type_n1_medium,
        vsw_vswitch_id="",
        zone_id="",
        env_type=2):
    data = {"env_uuid": uuid, "action": 1, "envs": []}
    for instance_name in instance_names:
        env = {
            "instance_name": instance_name,
            "image_id": image_id,
            "instance_type": instance_type,
            "type": env_type,
        }
        if vsw_vswitch_id:
            env["vsw_vswitch_id"] = vsw_vswitch_id
        if zone_id:
            env["zone_id"] = zone_id
        data["envs"].append(env)
    url = "http://automation-deploy:20080/env/deploy"
    headers = {"Content-Type": "application/json"}
    log.info(f"create_instances_by_deploy: url: {url}, envs: {data}")
    res = requests.post(url=url, data=json.dumps(data), headers=headers)
    if res.status_code != 200:
        log.error(f"create instances by deploy error: {res.json()}")
        assert False
    time.sleep(60)
    instances_info = {}
    loop_num = 10
    while loop_num:
        url = f"http://automation-deploy:20080/env/detail?env_uuid={uuid}"
        res = requests.get(url=url)
        res_json = res.json()
        if res.status_code != 200 or not res_json.get('DATA'):
            log.error(f"get instances by deploy error: {res_json}")
            assert False
        for instance_name in instance_names:
            if "complate" not in res_json["DATA"][instance_name][
                    "deploy_status"]:
                continue
            ip = res_json["DATA"][instance_name]["mgt_ip"]
            if not ip:
                log.error(
                    f"get instance {instance_name} ip error {res_json['DATA']}"
                )
                assert False
            instances_info[instance_name] = ip
        if len(instances_info) != len(instance_names):
            time.sleep(10)
            loop_num -= 1
        else:
            break
    if len(instances_info) != len(instance_names):
        assert False
    return instances_info


def release_instance_by_delpoy(uuid, instance_names=None, env_type=2):
    if common_config.debug == 1:
        return
    data = {"env_uuid": uuid, "action": 11, "envs": []}
    for instance_name in instance_names:
        data["envs"].append({
            "instance_name": instance_name,
            "type": env_type,
        })
    url = "http://automation-deploy:20080/env/deploy"
    headers = {"Content-Type": "application/json"}
    log.info(f"release_instance_by_delpoy: url: {url}, envs: {data}")
    res = requests.post(url=url, data=json.dumps(data), headers=headers)
    log.info(f"release_instance_by_delpoy: {res.json()}")


def _send_request(request):
    """send ID and SECRET by json"""
    request.set_accept_format('json')
    try:
        # log.info(f"send aliyun request:{request}")
        response_str = get_acsclient().do_action(request)
        # log.info(f"send aliyun request finished, {response_str[50:]}")
        response_detail = json.loads(response_str)
        return response_detail
    except Exception as err:
        log.error(err)


def create_after_pay_instance(instance_name, image_id, instance_type,
                              security_group_id, vsw_vswitch_id,
                              resource_group_id, password, zone_id,
                              key_pair_name):
    """create aliyun instance by API, parameter:
    need instance_name, as a string. e.g: instance_name = 'auto-vm1'
    use default values for other parameters
    """
    request = CreateInstanceRequest()
    request.set_ImageId(image_id)
    request.set_SecurityGroupId(security_group_id)
    request.set_InstanceType(instance_type)
    request.set_IoOptimized('optimized')
    request.set_VSwitchId(vsw_vswitch_id)
    request.set_ResourceGroupId(resource_group_id)
    request.set_InstanceName(instance_name)
    request.set_Password(password)
    request.set_ZoneId(zone_id)
    request.set_KeyPairName(key_pair_name)
    request.add_query_param('Tag.1.value', "自动化测试")
    request.add_query_param('Tag.1.key', "财务单元")
    request.set_DataDisks([{"Category": "cloud_ssd"}])
    response = _send_request(request)
    instance_id = response.get('InstanceId')
    log.info(response)
    log.info('aliyun instance creation task was submitted,id:{}'.format(
        instance_id))
    return instance_id


def start_instance(instance_id):
    """start aliyun instance, parameter;
    instance_id, required, type is string
    """
    request = StartInstanceRequest()
    request.set_InstanceId(instance_id)
    _send_request(request)
    log.info('aliyun instance status is started,id:{}'.format(instance_id))


def stop_instance(instance_id, force_stop=False):
    """stop aliyun instance id, parameter;
    instance_id, required, type is string
    force_stop, default, False and True
    """
    request = StopInstanceRequest()
    request.set_InstanceId(instance_id)
    request.set_ForceStop(force_stop)
    _send_request(request)
    log.info('aliyun instance status is stopped,id:{}'.format(instance_id))


def release_instance(instance_id, force=False):
    """release aliyun instance, parameter;
    instance_id, required, type is string
    force_stop, default, False and True
    """
    request = DeleteInstanceRequest()
    request.set_InstanceId(instance_id)
    request.set_Force(force)
    _send_request(request)
    log.info('aliyun instance status is released, instance id is {}'.format(
        instance_id))
    return True


def get_instance_detail_by_id(instance_id, status='Stopped'):
    """check aliyun instance status is stopped by id, parameter;
    instance_id; required, type is string
    status; default, Stopped"""
    log.info(
        'check aliyun instance status is {}, aliyun instance id is {}'.format(
            status, instance_id))
    request = DescribeInstancesRequest()
    request.set_InstanceIds(json.dumps([instance_id]))
    response = _send_request(request)
    instance_detail = None
    if response is not None:
        instance_list = response.get('Instances').get('Instance')
        for item in instance_list:
            if item.get('Status') == status:
                instance_detail = item
                break
        return instance_detail


def check_instance_running(instance_id, instance_running='Running'):
    """check aliyun instance is running, parameter;
    instance_id; required, type is string
    instance_running; default, Running
    """
    detail = get_instance_detail_by_id(instance_id, instance_running)
    index = 0
    private_ip = None
    while detail is None and index < 60:
        detail = get_instance_detail_by_id(instance_id)
        time.sleep(10)
    if detail and detail.get('Status') == 'Stopped':
        log.info(f"aliyun instance {instance_id} is stopped now.")
        start_instance(instance_id)
        log.info(f"start aliyun instance {instance_id} job submit.")
    detail = get_instance_detail_by_id(instance_id, instance_running)
    while detail is None and index < 60:
        time.sleep(10)
        detail = get_instance_detail_by_id(instance_id, instance_running)
    private_ip = get_instance_info([detail.get('InstanceName')],
                                   get_type="private_ip")
    log.info(f"aliyun instance {instance_id} is running now.")
    return private_ip[detail.get('InstanceName')]


def get_instance_by_name_prefix(prefix, pagesize=100):
    """get instance info by name prefix;
    prefix string
    pagesize default value is 20
    return instance id, dict
    """
    instance_info = dict()
    request = DescribeInstancesRequest()
    request.set_accept_format('json')
    request.set_PageNumber(1)
    request.set_PageSize(pagesize)
    response = _send_request(request)
    for n in range(pagesize):
        if len(response.get('Instances').get('Instance')) <= n:
            break
        instance_name = response.get('Instances').get('Instance')[n].get(
            'InstanceName')
        if instance_name.startswith(prefix):
            for i in range(10):
                if instance_name in instance_info:
                    instance_name = f"{instance_name}-{i}"
                else:
                    break
            instance_info[instance_name] = response.get('Instances').get(
                'Instance')[n].get('InstanceId')
    return instance_info


def get_instance_info(instance_name, get_type='instance_id', pagesize=20):
    """get instance info, instance name type is dict, parameter;
    get_type='status', type is string
    get_type='private_ip', type is tring
    get_type='instance_name', type is string
    get_type='mac_address', type is string
    pagesize default value is 20
    """
    instance_info = dict()
    for i in range(len(instance_name)):
        request = DescribeInstancesRequest()
        request.set_accept_format('json')
        request.set_PageNumber(1)
        request.set_PageSize(pagesize)
        response = _send_request(request)
        for n in range(pagesize):
            if get_type == 'instance_id' and response.get('Instances').get('Instance')[n].get('InstanceName') == \
                    instance_name[i]:
                instance_id = response.get('Instances').get('Instance')[n].get(
                    'InstanceId')
                instance_info[instance_name[i]] = instance_id
                break
            elif get_type == 'status' and response.get('Instances').get('Instance')[n].get('InstanceName') == \
                    instance_name[i]:
                instance_status = response.get('Instances').get(
                    'Instance')[n].get('Status')
                instance_info[instance_name[i]] = instance_status
                break
            elif get_type == 'private_ip' and response.get('Instances').get('Instance')[n].get('InstanceName') == \
                    instance_name[i]:
                instance_private_ip = \
                    response.get('Instances').get('Instance')[n].get('VpcAttributes').get('PrivateIpAddress').get(
                        'IpAddress')[0]
                instance_info[instance_name[i]] = instance_private_ip
                break
            elif get_type == 'mac_address' and response.get('Instances').get('Instance')[n].get('InstanceName') == \
                    instance_name[i]:
                instance_mac_address = \
                    response.get('Instances').get('Instance')[n].get('NetworkInterfaces').get('NetworkInterface')[
                        0].get(
                        'MacAddress')
                instance_info[instance_name[i]] = instance_mac_address
                break
            elif get_type == 'instance_name' and response.get('Instances').get('Instance')[n].get('InstanceName') == \
                    instance_name[i]:
                instance_names = response.get('Instances').get(
                    'Instance')[n].get('InstanceName')
                instance_info[instance_name[i]] = instance_names
                break
            else:
                pass
    return instance_info


def create_instance_action(instance_name, image_id=common_config.ali_image_centos7_419_id,
                           instance_type=common_config.ali_instance_type_n1_medium, \
                           security_group_id=common_config.ali_security_group_default,
                           vsw_vswitch_id=common_config.ali_switch_id_default, \
                           resource_group_id=common_config.ali_resource_group_ie_ee,
                           password=ali_vm_password_default,
                           zone_id=common_config.ali_zone_id_default,
                           key_pair_name=common_config.ali_key_pair_name):
    """create aliyun instance action, parameter;
    instance_name, required, type is dict. e.g: instance_name = ['auto-vm1']
    """
    instance_id_info = dict()
    instance_ids = []
    private_ip_map = {}
    for i in range(len(instance_name)):
        vm_name = instance_name[i]
        instance_id = create_after_pay_instance(vm_name, image_id,
                                                instance_type,
                                                security_group_id,
                                                vsw_vswitch_id,
                                                resource_group_id, password,
                                                zone_id, key_pair_name)
        instance_id_info[vm_name] = instance_id
    for vm_name, instance_id in instance_id_info.items():
        if instance_id is not None:
            private_ip = check_instance_running(instance_id)
            log.info('aliyun instance status is normal,id:{},name:{}'.format(
                instance_id, vm_name))
            private_ip_map[instance_id] = private_ip
    time.sleep(40)
    for _, private_ip in private_ip_map.items():
        insert_ali_id_rsa(private_ip)
    return instance_id_info


def insert_ali_id_rsa(private_ip):
    ssh = ssh_pool.get(private_ip, common_config.ssh_port_default,
                       common_config.ssh_username_default,
                       common_config.ssh_password_default)
    ali_id_rsa = common_config.ali_id_rsa
    if not ali_id_rsa:
        p = run_cmd("cat aliyun_id_rsa")
        ali_id_rsa = p.stdout.decode("utf-8")
        if not ali_id_rsa:
            log.warning("ali_id_rsa is None")
            return
    stdin, stdout, stderr = ssh.exec_command(
        f'''echo {ali_id_rsa}|base64 -d > ~/.ssh/id_rsa && chmod 600 ~/.ssh/id_rsa'''
    )
    logs = stderr.readlines()
    if logs:
        log.error(logs)


def modify_instance_name_action(instance_name_info, instance_new_name):
    """modify aliyun instance name action, parameter;
    instance_name_info; required, type is dict. e.g: instance_name_info = {instance_name:instance_id}
    instance_new_name; required, instance new name
    """
    instance_new_name_info = dict()
    for instance_name, instance_id in instance_name_info.items():
        request = ModifyInstanceAttributeRequest()
        request.set_InstanceId(instance_id)
        request.set_InstanceName(instance_new_name)
        response = _send_request(request)
        instance_names = response.get('InstanceName')
        if instance_names == None:
            log.info('aliyun instance name is modified now,id:{},new name:{}'.
                     format(instance_id, instance_new_name))
            instance_new_name_info[instance_id] = instance_new_name
        return instance_new_name_info


def delete_instance_action(instance_id_info):
    """delete aliyun instance action. parameter
    instance_id_info; required, instance_id_info
    """
    for instance_name, instance_id in instance_id_info.items():
        stop_instance(instance_id, force_stop=True)
        log.info('wait 30s,aliyun instance is stopping. id:{},name:{}'.format(
            instance_id, instance_name))
        time.sleep(3)
    time.sleep(10)
    for instance_name, instance_id in instance_id_info.items():
        release_instance(instance_id, force=True)
        log.info('aliyun instance has been deleted.id:{},name:{}'.format(
            instance_id, instance_name))

        # instance_status = get_instance_info([instance_name],
        #                                     get_type='status')
        # if instance_status[instance_name] == 'Stopped':
        #     release_instance(instance_id, force=True)
        #     log.info(
        #         'aliyun instance has been deleted.id:{},name:{}'.format(
        #             instance_id, instance_name
        #         )
        #     )
        #     instance_id_info.pop(instance_name)
        #     break
        # else:
        #     log.info('wait 10s')
        #     log.info(
        #         '等待实例停止，实例ID是: {} 实例名称是: {} status: {}'.format(
        #             instance_id, instance_name,
        #             instance_status[instance_name]
        #         )
        #     )
        time.sleep(3)


##########VPC##########
def create_vpc_without_subnet(
        vpc_name,
        vpc_cidr,
        resource_group_id=common_config.ali_resource_group_ie_ee):
    """
    create aliyun vpc without subnet. parameter;
    vpc_name; required, type is string
    vpc_cidr; required, type is string
    resource_group_id; default, type is string
    return vcp id
    """
    try:
        request = CreateVpcRequest.CreateVpcRequest()
        request.set_VpcName('%s' % (vpc_name))
        request.set_ResourceGroupId(resource_group_id)
        request.set_CidrBlock('%s' % (vpc_cidr))
        request.set_accept_format('JSON')
        response = get_acsclient().do_action(request)
        response_json = json.loads(response)
        vpc_id = response_json.get('VpcId')
        return vpc_id
    except Exception as err:
        log.error(
            'create aliyun vpc without subnet failed, log info:\n{}'.format(
                err))


def get_vpc_info_by_id(vpc_id, vpc_type='name'):
    """
    get aliyun vpc info by vpc id. parameter;
    vpc_id; required, type is string
    vpc_type; default, default value is name, type is string
    vpc_type=status, get vpc status, type is string
    vpc_type=cidr, get cidr value, type is string
    """
    request = DescribeVpcAttributeRequest.DescribeVpcAttributeRequest()
    request.set_VpcId(vpc_id)
    request.set_accept_format('JSON')
    response = get_acsclient().do_action(request)
    response_json = json.loads(response)
    if vpc_type == 'name':
        return response_json.get('VpcName')
    elif vpc_type == 'status':
        return response_json.get('Status')
    elif vpc_type == 'cidr':
        return response_json.get('CidrBlock')
    else:
        return response_json


def create_vpc_without_subnet_action(
        vpc_name,
        vpc_cidr,
        resource_group_id=common_config.ali_resource_group_ie_ee):
    """create vpc without subnet. parameter;
    vpc_name; required, vpc name, type is list
    vpc_cidr; required, vpc cidr, type is list
    resource_group_id; default，resource group id. type is string
    """
    index = 0
    vpc_id_info = dict()
    for i in range(len(vpc_name)):
        try:
            vpc_id = create_vpc_without_subnet(vpc_name[i], vpc_cidr[i],
                                               resource_group_id)
            while index <= 60:
                if get_vpc_info_by_id(vpc_id,
                                      vpc_type='status') == 'Available':
                    log.info(
                        'aliyun vpc has been created,vpc id:{},cidr:{}'.format(
                            vpc_id, vpc_name[i], vpc_cidr[i]))
                    vpc_id_info[vpc_name[i]] = vpc_id
                    break
                else:
                    log.info('aliyun vpc is creating now, wait 10s')
                    time.sleep(10)
                    index += 10
        except Exception as err:
            log.error('aliyun vpc creation failed, log info;\n{}'.format(err))
    return vpc_id_info


def modify_vpc_name_without_subnet(vpc_id_info, vpc_new_name):
    """modify vpc name, parameter;
    vpc_id_info; required, vpc name and vpc id. type is list, e.g: {vpc_name:vpc_id}
    vpc_new_name; required，vpc new name, type is string
    """
    vpc_new_id_info = dict()
    for vpc_name, vpc_id in vpc_id_info.items():
        try:
            request = ModifyVpcAttributeRequest.ModifyVpcAttributeRequest()
            request.set_VpcId('%s' % (vpc_id))
            request.set_VpcName('%s' % (vpc_new_name))
            request.set_accept_format('JSON')
            response = get_acsclient().do_action(request)
            log.info('aliyun vpc has been modified, vpc id; {}, vpc name: {}'.
                     format(vpc_id, vpc_new_name))
            vpc_new_id_info[vpc_new_name] = vpc_id
            return vpc_new_id_info
        except Exception as err:
            log.error(
                'aliyun vpc has not been modified, log info; \n{}'.format(err))


def delete_vpc_without_subnet_action(vpc_id_info):
    """delete vpc by API, parameter;
    vpc_id_info; required,vpc name and vpc id, type is dict, e.g: {vpc_name:vpc_id}
    """
    for vpc_name, vpc_id in vpc_id_info.items():
        try:
            request = DeleteVpcRequest.DeleteVpcRequest()
            request.set_VpcId('%s' % (vpc_id))
            request.set_accept_format('JSON')
            response = get_acsclient().do_action(request)
            log.info(
                'aliyun vpc has been deleted, vpc id; {}. vpc name: {}'.format(
                    vpc_id, vpc_name))
        except Exception as err:
            log.error(
                'aliyun vpv has not been deleted, log info; \n{}'.format(err))


def create_linux_vm_x86(vm_name, type="k8s"):
    if type == "k8s":
        image_id = common_config.ali_image_centos7_deepflow_id
    elif type == "workloadv":
        image_id = common_config.ali_image_centos7_performance_id
    else:
        pass

    vm_id_info = create_instance_action([vm_name], image_id=image_id)
    log.info("VirtualMachine::create_linux_vm_x86::vm_id_info ==> {}".format(
        vm_id_info))

    vm_name_ip_dict = get_instance_info([vm_name], get_type='private_ip')
    vm_ip = vm_name_ip_dict[vm_name]
    log.info("VirtualMachine::create_linux_vm_x86::vm_ip ==> {}".format(vm_ip))
    return vm_id_info, vm_ip


def create_linux_vm_arm(arm_vm_name):
    vm_id_info = create_instance_action(
        [arm_vm_name],
        image_id=common_config.ali_image_anolis_performance_id,
        instance_type=common_config.ali_instance_type_g6r_large,
        vsw_vswitch_id=common_config.ali_switch_id_arm,
        zone_id=common_config.ali_zone_id_beijing_k)
    vm_name_ip_dict = get_instance_info([arm_vm_name], get_type='private_ip')
    vm_ip = vm_name_ip_dict[arm_vm_name]
    log.info("create_linux_vm_arm::vm_id_info ==> {}".format(vm_id_info))
    log.info("create_linux_vm_arm::vm_ip ==> {}".format(vm_ip))
    return vm_id_info, vm_ip
