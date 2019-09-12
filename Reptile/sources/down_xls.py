from selenium import webdriver
from lxml import etree
import requests
import time
import re
import os

headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
    }
# 抓取信息并下载信息及模板
def GraspData(url, file):
    print(url)
    html = etree.HTML(requests.get(url, headers=headers).content.decode())
    title = html.xpath('//div[@class="bs_wz_a"]/a/span/text()')[1]
    file += ('\\' + title)
    if os.path.exists(file):
        pass
    else:
        os.mkdir(file)
    content = ''
    # 事项名称
    content += '事项名称：'
    content += html.xpath('//div[@class="bs_wz_c"]/table/tbody/tr/td[@colspan="6"]/text()')[0]
    content += '\n\n权力部门：'
    # 权力部门
    content += html.xpath('//div[@class="bs_wz_c"]/table/tbody/tr/td[@colspan="2"]/text()')[1]
    content +=  '\n\n电话：'
    # 联系电话
    try:
        print(html.xpath('//div[@class="bs_wz_c"]/table/tbody/tr/td[@colspan="4"]/text()'))
        telephones = html.xpath('//div[@class="bs_wz_c"]/table/tbody/tr/td[@colspan="4"]/text()')
        print(111111111111111111111)
    except:
        print(222222222222222222222)
        pass
    find = r'[0-9-]'
    number = ''
    for i in telephones:
        try:
            print(i)
            number = re.findall(find,i.split('电话')[1])
        except Exception as e:
            number = re.findall(find,i)
            print('caocuol',e)
            pass
    print(number)
    if len(number) >= 8:
        for n in number:
            content += n
        content += '\n\n'
    else:
        content += '暂无\n\n'

    # 申请条件
    try:
        content +=  '申请条件：'
        content += html.xpath('//div[@id="con03"]/table/tbody/tr/td/text()')[0] + ''
        materials = '//div[@id="con04"]/iframe/@src'
    except:
        content += '暂无'
        materials = '//div[@id="con03"]/iframe/@src'

    content += '申请材料：'

    # 材料名称
    html = etree.HTML(requests.get('http://gy.gzegn.gov.cn' + html.xpath(materials)[0], headers=headers).content.decode())
    temp = html.xpath('//table/tr')
    for i in range(2,(len(temp)+1)):
        # 序号，材料名称，材料要求，材料来源
        find = '//table/tr[{}]/td/text()'.format(str(i))
        Serial_number = html.xpath(find)
        content += '\n\n序号：' + Serial_number[0]
        content += '\n材料名称：' + Serial_number[1]
        content += '\n材料要求：' + Serial_number[2]
        content += '\n材料来源：' + Serial_number[3]
        # 法定依据及描述
        find1 = '//table/tr[{}]/td/div/text()'.format(str(i))
        content += '\n法定依据及描述：' + html.xpath(find1)[0]
        # 格式文本下载地址
        find2 = '//table/tr[{}]/td/a/@href'.format(str(i))
        find3 = '//table/tr[{}]/td/a/text()'.format(str(i))
        down_url = html.xpath(find2)
        down_file_name = html.xpath(find3)
        
        if len(down_url) != 0:
            for down_name, down_path in zip(down_file_name, down_url):
                print(down_name)
                if down_name.find('示范') != -1:
                    if down_path.find('.jpg') != -1:
                        file_extension = '示范.jpg'
                    elif down_path.find('.xls') != -1:
                        file_extension = '示范.xls'
                    elif down_path.find('.doc') != -1:
                        file_extension = '示范.doc'
                    else:
                        file_extension = '示范格式错误请查看.html'
                    f = open((file+'\\' + Serial_number[1] + file_extension),'wb')
                    f.write(requests.get(down_path, headers=headers).content)
                    f.close()
                else:
                    if down_path.find('.jpg') != -1:
                        file_extension = '示范.jpg'
                    elif down_path.find('.xls') != -1:
                        file_extension = '示范.xls'
                    elif down_path.find('.doc') != -1:
                        file_extension = '示范.doc'
                    else:
                        file_extension = '示范格式错误请查看.html'
                    f = open((file+'\\' + Serial_number[1] + file_extension),'wb')
                    f.write(requests.get(down_path, headers=headers).content)
                    f.close()

        else:
            pass

    f = open((file+'\\基础信息.txt'), 'w', encoding='utf-8')
    # print(content)
    f.write(content)
    f.close()

    time.sleep(3)



url = 'http://gynm.gzegn.gov.cn/art/2019/7/3/art_44999_303377.html'
file = "C:\\Users\\Administrator\\Desktop\\58"
GraspData(url, file)
