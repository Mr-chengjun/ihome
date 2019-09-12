from selenium import webdriver
from lxml import etree
import requests
import time
import re
import os

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
}


# 打开对应的TXT文件，转换成可以XPATH的文件并返还
def OpenFile(file_name):
    html = etree.HTML(open(file_name, 'r').read())

    return html


# 提取对应的城市名称，对应编号，以及链接地址，返还数据
def Arrangement(city):
    city_name = city.xpath('//div/a/text()')

    data_list = city.xpath('//div/a/@data')

    city_data = [i[2:-2] for i in data_list]

    temp_url = city.xpath('//div/a/@href')

    city_url = [i[2:-2] for i in temp_url]

    return city_name, city_data, city_url


# 抓取事项清单和办事指南
def detailedList(post_number, post_id):
    data = {
        'webId': post_number,
        'pageno': '',
        'deptCode': post_id,
        'type': '',
        'keyword': ''
    }
    print(requests.post('http://gy.gzegn.gov.cn/gzszwfww/bmbs/bmbslistshow.do', headers=headers, data=data).text)
    # open('temp.txt', 'w').write(requests.get('http://gy.gzegn.gov.cn/gzszwfww/bmbs/bmbslistshow.do', headers=headers).content.decode())


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
    content += '\n\n电话：'
    # 联系电话
    try:
        telephones = html.xpath('//div[@class="bs_wz_c"]/table/tbody/tr/td[@colspan="4"]/text()')
    except:

        pass
    find = r'[0-9-]'
    number = ''
    for i in telephones:
        try:
            print(i)
            number = re.findall(find, i.split('电话')[1])
        except Exception as e:
            number = re.findall(find, i)
            print('caocuol', e)
            pass
    if len(number) >= 8:
        for n in number:
            content += n
        content += '\n\n'
    else:
        content += '暂无\n\n'

    # 申请条件
    try:
        content += '申请条件：'
        content += html.xpath('//div[@id="con03"]/table/tbody/tr/td/text()')[0] + ''
        materials = '//div[@id="con04"]/iframe/@src'
    except:
        content += '暂无'
        materials = '//div[@id="con03"]/iframe/@src'

    content += '申请材料：'

    # 材料名称
    html = etree.HTML(
        requests.get('http://gy.gzegn.gov.cn' + html.xpath(materials)[0], headers=headers).content.decode())
    temp = html.xpath('//table/tr')
    for i in range(2, (len(temp) + 1)):
        # 序号，材料名称，材料要求，材料来源
        find = '//table/tr[{}]/td/text()'.format(str(i))
        Serial_number = html.xpath(find)
        content += '\n\n序号：' + Serial_number[0]
        try:
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
                    file_extension = ('.' + down_path.split('.')[-1].split('&')[0])
                    print(file_extension)
                    if down_name.find('示范') != -1:
                        '''
                        if down_path.find('.jpg') != -1 or down_path.find('.JPG') != -1:
                            file_extension = '示范.jpg'
                        elif down_path.find('.xls') != -1 or down_path.find('.XLS') != -1:
                            file_extension = '示范.xls'
                        elif down_path.find('.doc') != -1 or down_path.find('.DOC') != -1:
                            file_extension = '示范.doc'
                        else:
                            file_extension = '示范格式错误请查看.html'
                            '''
                        f = open((file + '\\' + Serial_number[1] + file_extension), 'wb')
                        f.write(requests.get(down_path, headers=headers).content)
                        f.close()
                    else:
                        '''
                        if down_path.find('.jpg') != -1:
                            file_extension = '示范.jpg'
                        elif down_path.find('.xls') != -1:
                            file_extension = '示范.xls'
                        elif down_path.find('.doc') != -1:
                            file_extension = '示范.doc'
                        else:
                            file_extension = '示范格式错误请查看.html'
                            '''
                        print("****************************************")
                        print(file)
                        print(Serial_number)
                        print(file_extension)
                        f = open((file + '\\' + Serial_number[1] + file_extension), 'wb')
                        f.write(requests.get(down_path, headers=headers).content)
                        f.close()

            else:
                pass
        except:
            pass

    f = open((file + '\\基础信息.txt'), 'w', encoding='utf-8')
    # print(content)
    f.write(content)
    f.close()

    time.sleep(3)


# 用webdriver 抓取模板等内容对应的链接
def Driver(url, file):
    print("1、参数URL：")
    driver = webdriver.Chrome(r'C:\Users\Administrator\Desktop\chromedriver.exe')
    driver.get(url)
    url_list = driver.find_elements_by_xpath('//li[@class="bs"]/a')

    for url in url_list:
        print("2、",url.get_attribute('href'))
        GraspData(url.get_attribute('href'), file)
    while True:
        bk = True
        next_page = driver.find_elements_by_xpath('//div[@class="fw_fy_b fl"]/ul[@class="cf"]/li/a')
        print("3、next_page:", next_page)
        number = 0
        for i in next_page:
            number += 1
            try:
                print("4、i：", i)
                if i.text == '下一页':
                    i.click()
                    number = 0
                    url_list1 = driver.find_elements_by_xpath('//li[@class="bs"]/a')
                    for url in url_list1:
                        print("5、URL:", url)
                        GraspData(url.get_attribute('href'), file)
                if number == 3:
                    print('number =============== 3')
                    bk = False
            except Exception as e:
                print('baocuole', e)
                pass
        if bk == False:
            break
    driver.quit()


# 循环整理各个城市的乡镇的url，并抓取保存
def main():
    # 文件保存地址
    file_path = "../ttt/"
    # os.mkdir(file_path)
    # 获取名字，城市id， 城市的url
    # 市级
    city_name, city_data, city_url = Arrangement(OpenFile('shi.txt'))
    # 县级
    county_content = open('xian.txt', 'r').read().split('<!--')
    # 乡级
    country_content = open('xiang.txt', 'r').read().split('<!--')
    for name in city_name:
        print(name)
        if os.path.exists(file_path + name):
            pass
        else:
            os.mkdir(file_path + name)
        for county in county_content:
            if county.find(name) != -1:
                county_name, county_data, county_url = Arrangement(etree.HTML(county))

                for county in county_name:
                    print(county)
                    if os.path.exists(file_path + name + '\\' + county):
                        pass
                    else:
                        os.mkdir(file_path + name + '\\' + county)
                    # os.mkdir(file_path+name+'\\'+county)
                    for country in country_content:
                        if country.find(county) != -1:
                            country_name, country_data, country_url = Arrangement(etree.HTML(country))
                            # print(country_name)
                            if len(country_name) != 0:
                                for url in country_url:
                                    print(country_name[country_url.index(url)])
                                    file = file_path + name + '\\' + county + '\\' + (
                                        country_name[country_url.index(url)])
                                    if os.path.exists(file):
                                        pass
                                    else:
                                        os.mkdir(file)
                                    # os.mkdir(file)
                                    suffix = etree.HTML(requests.get(url, headers=headers).content.decode()).xpath(
                                        '//iframe/@src')[0]

                                    driver_url = (url.split('.cn')[0]) + '.cn' + suffix
                                    print(driver_url)
                                    Driver(driver_url, file)

                                    # time.sleep(5)
                            else:
                                pass


if __name__ == '__main__':
    main()
