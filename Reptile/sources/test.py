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


# 从已经有的txt文件中提取对应的城市名称，对应编号，以及链接地址，返还数据
def Arrangement(city):
    """
    :param city: 城市的xpath对象
    :return:城市名称、城市data、城市的url
    """
    city_name = city.xpath('//div/a/text()')

    data_list = city.xpath('//div/a/@data')

    city_data = [i[2:-2] for i in data_list]

    temp_url = city.xpath('//div/a/@href')
    print("temp_url:", temp_url)

    city_url = [i[2:-2] for i in temp_url]
    return city_name, city_data, city_url


def Arrangement_shi(city_con):
    """
    :param city: 城市的xpath对象
    :return:城市名称、城市data、城市的url
    """
    city_con.pop(0)
    print(city_con)
    city_names = []
    city_urls = []
    for city in city_con:
        city = etree.HTML(city)
        base_url = city.xpath('//div[@class="city_name"]/a/@href')
        print("base_url:", base_url)
        city_names.append(city.xpath('//div/a/text()'))
        temp_url = city.xpath('//div/a/@href')[1:]
        city_urls.append([j + i for j in base_url for i in temp_url])
        print("temp_url:", temp_url)

    return city_names, city_urls


# 获取省级
def Arrangement_prov(prov):
    """
    :param prov: 省级的xpath对象
    :return:省名称、、省的url
    """
    base_url = prov.xpath('//div[@class="pro_name"]/a/@href')
    print("base_url:", base_url)
    prov_name = prov.xpath('//div/a/text()')
    temp_url = prov.xpath('//div/a/@href')[1:]
    print("temp_url:", temp_url)

    prov_url = [base_url[0] + i for i in temp_url]

    return prov_name, prov_url


# 抓取信息并下载信息及模板，
def GraspData(url, file):
    """
    :param url: 具体事件的url
    :param file: 文件的保存路径
    :return: None
    """
    content = ""
    telephones = ""

    html = etree.HTML(requests.get(url, headers=headers).content.decode())
    try:
        # print(url)
        title = html.xpath('//div[@class="bs_wz_a"]/a/span/text()')[1]
        file += ('\\' + title)
        if os.path.exists(file):
            pass
        else:
            os.mkdir(file)
        # 事项名称
        content += '事项名称：'
        content += html.xpath('//div[@class="bs_wz_c"]/table/tbody/tr/td[@colspan="6"]/text()')[0]
        content += '\n\n权力部门：'
        # 权力部门
        content += html.xpath('//div[@class="bs_wz_c"]/table/tbody/tr/td[@colspan="2"]/text()')[1]
        content += '\n\n电话：'
        # 联系电话
        telephones = html.xpath('//div[@class="bs_wz_c"]/table/tbody/tr/td[@colspan="4"]/text()')
    except:
        pass
    find = r'[0-9-]'
    number = ''
    try:
        for i in telephones:
            try:
                # print(i)
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
    except:
        pass

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
    try:
        html = etree.HTML(
            requests.get('http://gy.gzegn.gov.cn' + html.xpath(materials)[0], headers=headers).content.decode())
    except:
        pass
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
                    # print(down_name)
                    file_extension = ('.' + down_path.split('.')[-1].split('&')[0])
                    # print(file_extension)
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
                        try:
                            f = open((file + '\\' + Serial_number[1] + file_extension), 'wb')
                            f.write(requests.get(down_path, headers=headers).content)
                        except:
                            pass
                        finally:
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
                        try:
                            f = open((file + '\\' + Serial_number[1] + file_extension), 'wb')
                            f.write(requests.get(down_path, headers=headers).content)

                        except:
                            pass
                        finally:
                            f.close()
            else:
                pass
        except:
            pass
    try:
        f = open(os.path.join(file, "基础信息.txt"), 'w', encoding='utf-8')
        f.write(content)
        f.close()
    except:
        pass

    time.sleep(3)


# 用webdriver 抓取模板等内容对应的链接
def Driver(url, file):
    """
    :param url: 事件页面的url
    :param file: 文件的保存路径
    :return: None
    """
    driver = webdriver.Chrome(r'C:\Users\Administrator\Desktop\chromedriver.exe')
    driver.get(url)
    url_list = driver.find_elements_by_xpath('//li[@class="bs"]/a')
    for url in url_list:
        GraspData(url.get_attribute('href'), file)
    while True:
        bk = True
        next_page = driver.find_elements_by_xpath('//div[@class="fw_fy_b fl"]/ul[@class="cf"]/li/a')

        number = 0
        for i in next_page:
            number += 1
            try:

                if i.text == '下一页':
                    i.click()
                    number = 0
                    # 获取事件页面每一个事件的url
                    url_list1 = driver.find_elements_by_xpath('//li[@class="bs"]/a')
                    print("url_list:", url_list)
                    for url in url_list1:
                        # 针对每个事件url爬取详细信息，并保存
                        GraspData(url.get_attribute('href'), file)
                if number == 3:
                    print('number =============== 3')
                    print("没有下一页")
                    bk = False
            except Exception as e:
                print('baocuole', e)
                pass
        if bk == False:
            break
    driver.quit()


# 用webdriver 抓取模板等内容对应的链接
def Driver_shiji(url, file):
    """
    省、市级别
    :param url: 事件页面的url
    :param file: 文件的保存路径
    :return: None
    """
    driver = webdriver.Chrome(r'C:\Users\Administrator\Desktop\chromedriver.exe')
    driver.get(url)
    url_list = driver.find_elements_by_xpath('//li[@class="bs"]/a')
    try:
        url_list.pop(1)
    except:
        pass
    print(url_list)
    for url in url_list:
        print("url:", url.get_attribute('href'))
        GraspData(url.get_attribute('href'), file)
    while True:
        next_page = driver.find_elements_by_xpath('//*[@class="laypage_next"]')
        if next_page == []:
            break
        for i in next_page:
            print(i.text)
            try:
                if i.text == '下一页':
                    i.click()
                    # 获取事件页面每一个事件的url
                    url_list1 = driver.find_elements_by_xpath('//li[@class="bs"]/a')
                    print("url_list:", url_list)
                    for url in url_list1:
                        # 针对每个事件url爬取详细信息，并保存
                        print("url2:", url.get_attribute('href'))
                        GraspData(url.get_attribute('href'), file)

            except Exception as e:
                print('baocuole', e)
                pass
    driver.quit()


# 用webdriver 抓取模板等内容对应的链接
def Driver_prov(url, file):
    """
    省级别
    :param url: 事件页面的url
    :param file: 文件的保存路径
    :return: None
    """
    driver = webdriver.Chrome(r'C:\Users\Administrator\Desktop\chromedriver.exe')
    driver.get(url)
    url_list = driver.find_elements_by_xpath('//li[@class="bs"]/a')
    for url in url_list:
        try:
            GraspData(url.get_attribute('href'), file)
        except:
            pass
    while True:
        next_page = driver.find_elements_by_xpath('//*[@class="laypage_next"]')
        if next_page == []:
            break
        for i in next_page:
            print(i.text)
            try:
                if i.text == '下一页':
                    i.click()
                    # 获取事件页面每一个事件的url
                    url_list1 = driver.find_elements_by_xpath('//li[@class="bs"]/a')
                    print("url_list:", url_list)
                    for url in url_list1:
                        # 针对每个事件url爬取详细信息，并保存
                        print("url2:", url.get_attribute('href'))
                        GraspData(url.get_attribute('href'), file)

            except Exception as e:
                print('baocuole', e)
                pass
    driver.quit()


# 循环整理各个城市的乡镇的url，并抓取保存
def getCountry(file_path):
    # 获取名字，城市id， 城市的url
    # 市级
    city_name, city_data, city_url = Arrangement(OpenFile('shi.txt'))
    print("city_url", city_url)
    # 县级
    county_content = open('xian.txt', 'r').read().split('<!--')
    # 乡级
    country_content = open('xiang.txt', 'r').read().split('<!--')
    for name in city_name:
        # print(name)
        if os.path.exists(file_path + name):
            pass
        else:
            os.mkdir(file_path + name)
        for county in county_content:
            if county.find(name) != -1:
                county_name, county_data, county_url = Arrangement(etree.HTML(county))

                for county in county_name:
                    # print(county)
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
                                    # print(country_name[country_url.index(url)])
                                    file = file_path + name + '\\' + county + '\\' + (
                                        country_name[country_url.index(url)])
                                    if os.path.exists(file):
                                        pass
                                    else:
                                        os.mkdir(file)
                                    # os.mkdir(file)
                                    print("url:", url)
                                    suffix = etree.HTML(requests.get(url, headers=headers).content.decode()).xpath(
                                        '//iframe/@src')[0]

                                    print("suffix", suffix)
                                    # 构造事件页面的url
                                    driver_url = (url.split('.cn')[0]) + '.cn' + suffix
                                    print(driver_url)
                                    Driver(url, file)
                                    # time.sleep(5)
                            else:
                                pass


def getCity(file_path):
    """
    获取市级的资料
    :param file_path:
    :return: None
    """
    # 获取名字，城市id， 城市的url
    # 市级
    city_name, city_url = Arrangement_shi(open('shiji/shi.txt').read().split('<!---->'))
    print(city_name)
    print(city_url)
    for i in range(len(city_name)):
        base_file = file_path + city_name[i].pop(0)
        print("办事单位名称长度：",len(city_name[i]))
        print("对应url长度:", len(city_url[i]))
        print("----------------------------------")
        for j in range(len(city_name[i])):
            print("办事单位名称：",city_name[i][j])
            print("对应url:", city_url[i][j])
            file = os.path.join(base_file, city_name[i][j])
            print("保存路径：",file)
            print("**************************************************")
            if os.path.exists(file):
                pass
            else:
                os.makedirs(file)
            Driver_shiji(city_url[i][j], file)
            # time.sleep(5)



def getProvince(file_path):
    """
    获取省信息
    :param file_path:
    :return:
    """
    "http://www.gzegn.gov.cn/gzszwfww/bmbs/showDetail.do?webId=1&deptCode=11520000MB157"
    # 获取名字，城市id， 城市的url
    # 市级
    prov_name, prov_url = Arrangement_prov(OpenFile('province/province.txt'))
    pro = prov_name.pop(0)
    base_file = os.path.join(file_path, pro)
    print(len(prov_name))
    print(len(prov_url))
    for i in range(len(prov_name)):
        file = os.path.join(base_file, prov_name[i])  # 文件保存路劲 + 省 + 单位
        print("办事单位:", prov_name[i])
        print("保存路径：", file)
        if os.path.exists(file):
            pass
        else:
            os.makedirs(file)
        print("url:", prov_url[i])
        print("file:", file)
        print("*******************************************")
        # Driver_prov(url, file)
        # time.sleep(5)



def main():
    # 文件保存地址
    file_path = "D:/贵州政务服务数据/"
    # os.mkdir(file_path)
    getCity(file_path)
    # getProvince(file_path)


if __name__ == '__main__':
    main()
