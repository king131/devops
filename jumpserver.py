#!/usr/bin/python

import requests
import json
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.acs_exception.exceptions import ClientException
from aliyunsdkcore.acs_exception.exceptions import ServerException
from aliyunsdkecs.request.v20140526.DescribeInstancesRequest import DescribeInstancesRequest

'''
1,需要修改下面的六个变量
2,需要修改 add_jumpserver_hosts 方法中：
    admin_user
    nodes
  的UUID。这个可以通过在页面创建后，通过api获取这俩值。

'''
JUMPSERVER_HOST= "xxxx"
JUMPSERVER_ADMIN_USER = "xxxx"
JUMPSERVER_ADMIN_PASSWD = "xxxx"

ECS_ACCESS_KEY_ID = "xxxx"
ECS_ACCESS_SECRET = "xxxx"
ECS_REGION_ID = "cn-hangzhou"

def get_token():

    url = 'http://%s/api/users/v1/auth/' %JUMPSERVER_HOST

    query_args = {
        "username": JUMPSERVER_ADMIN_USER,
        "password": JUMPSERVER_ADMIN_PASSWD
    }

    response = requests.post(url, data=query_args)


    return json.loads(response.text)['token']

#获取阿里云ecs实例
def get_ecs_instances():
    client = AcsClient(
       ECS_ACCESS_KEY_ID,
       ECS_ACCESS_SECRET,
       ECS_REGION_ID
    );

    #ecs实例空字典
    instances = {}
    page_size = 10
    page_number = 1
    total_count = None

    request = DescribeInstancesRequest()
    request.set_PageNumber(page_number)
    request.set_PageSize(page_size)

    #以{privateIP:InstanceName}的形式将实例的名字和私网ip添加到ecs实例字典里
    while total_count is None or page_number * page_size < (total_count + page_size)  :
        body = client.do_action_with_exception(request)
        data = json.loads(body)
        for instance in data['Instances']['Instance']:
            instances.update( {  instance['VpcAttributes']['PrivateIpAddress']['IpAddress'][0] : instance['InstanceName'] })
        total_count = data['TotalCount']
        page_number += 1
        request.set_PageNumber(page_number)
    print("获取阿里云ecs数据....共获取 %s 条数据。" %(len(instances)) )
    return instances

#获取jumpserver中已经存在的实例
def get_assets_instances():
    url = 'http://%s/api/assets/v1/assets/' %JUMPSERVER_HOST
    token = get_token()
    header_info = { "Authorization": 'Bearer ' + token }
    response = requests.get(url, headers=header_info)
    data = json.loads(response.text)
    jumpserver_instances = []

    for instance in data:
        jumpserver_instances.append(instance['ip'])
    print("获取jumpserver已录入数据....共获取 %s 条数据。" % (len(jumpserver_instances)))
    return jumpserver_instances

def add_jumpserver_hosts(list,ecs_dict):
    token = get_token()
    ecs_instances = ecs_dict
    url = 'http://%s/api/assets/v1/assets/' %JUMPSERVER_HOST
    header_info = {"Authorization": 'Bearer ' + token}
    for i in list:
        print("添加IP：%s，hostname: %s 至jumpserver中" %(i,ecs_instances[i]))
        post_data = {
            "ip": i,
            "is_active": "true",
            "hostname": ecs_instances[i],
            "admin_user": "dad9a385-e1b4-4aa5-9ffe-3ce292d173f7",
            "nodes": [
                "24c3613f-14a8-4423-b869-21ee795233c4"
            ]
        }
        response = requests.post(url,post_data,headers=header_info)

def delete_jumpserver_hosts(list):
    token = get_token()
    header_info = {"Authorization": 'Bearer ' + token}
    for i in list:
        url = "http://%s/api/assets/v1/assets/?ip=%s" %(JUMPSERVER_HOST,i)
        requests.delete(url,headers=header_info)



def add_or_delete_host():
    jumpserver_hosts_ip = get_assets_instances()
    ecs_instances = get_ecs_instances()
    ecs_hosts_ip = []
    for ip in ecs_instances.keys():
        ecs_hosts_ip.append(ip)


    exist_ip = list(set(jumpserver_hosts_ip).intersection(set(ecs_hosts_ip)))
    already_deleted_ip = list(set(jumpserver_hosts_ip).difference(set(exist_ip)))
    needed_add_ip = list(set(ecs_hosts_ip)-set(exist_ip))
    print("需添加 %s 条数据至jumpserver,需要删除 %s 条数据。" %(len(needed_add_ip),len(already_deleted_ip)))
    #添加机器
    add_jumpserver_hosts(needed_add_ip,ecs_instances)
    #删除机器
    delete_jumpserver_hosts(already_deleted_ip)

if __name__ == '__main__':
    add_or_delete_host()
