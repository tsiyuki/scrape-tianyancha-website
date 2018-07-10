#coding: gbk
import re, json
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import time, os
import uuid,re
import selenium
from bs4 import BeautifulSoup
from fontTools.ttLib import TTFont
from urllib import request
import tinycss2
# import conn_mysql

class Scrape(object):

    def __init__(self, word):
        self.url = 'https://www.tianyancha.com/login'
        self.username = '15757474731'
        self.password = 'tekinfo0517'
        self.word = word
        # self.driver = self.login()
        # self.scrapy(self.driver)


    def login(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')

        driver = webdriver.Chrome(chrome_options=chrome_options)
        driver.get(self.url)

        # 模拟登陆
        driver.find_element_by_xpath(
            ".//*[@id='web-content']/div/div/div/div[2]/div/div[2]/div[2]/div[2]/div[2]/input"). \
            send_keys(self.username)
        driver.find_element_by_xpath(
            ".//*[@id='web-content']/div/div/div/div[2]/div/div[2]/div[2]/div[2]/div[3]/input"). \
            send_keys(self.password)
        driver.find_element_by_xpath(
            ".//*[@id='web-content']/div/div/div/div[2]/div/div[2]/div[2]/div[2]/div[5]").click()
        time.sleep(1)
        driver.refresh()
        # driver.get('https://www.tianyancha.com/company/28723141')

        # 模拟登陆完成，输入搜索内容
        driver.find_element_by_xpath(".//*[@id='home-main-search']").send_keys(self.word)  # 输入搜索内容
        driver.find_element_by_xpath(".//*[@id='home-main-search']").send_keys(Keys.ENTER)
        driver.implicitly_wait(5)

        # 选择相关度最高的搜索结果 第一条搜索框，然后再
        try:
            driver.find_element_by_xpath(".//img[@id='bannerClose']").click()
        except selenium.common.exceptions.NoSuchElementException:
            pass
        number = driver.find_elements_by_xpath("//div[@id='search']//span[@class='num']")[0].text
        return number, driver

    def get_company_list(self, driver):
        names = {}
        tags = driver.find_elements_by_xpath("//div[@class='search-result-single ']")
        for tag in tags:
            names[tag.find_element_by_xpath(".//a[@class='name ']").text] = tag.find_element_by_tag_name('a')
        while True:
            try:
                next = driver.find_element_by_xpath("//a[@class='num -next']")
            except selenium.common.exceptions.NoSuchElementException:
                break
            else:
                next.send_keys(Keys.ENTER)
                # ActionChains(driver).move_to_element(next_link).perform()
                # next_link.click()
                driver.implicitly_wait(10)
                tags = driver.find_elements_by_xpath("//div[@class='search-result-single ']")
                for tag in tags:
                    names[tag.find_element_by_xpath(".//a[@class='name ']").text] = tag.find_element_by_tag_name('a')
        return tags, names

    def select_company(self, driver, company):
        tags = driver.find_elements_by_xpath("//div[@class='search-result-single ']")
        link = None
        for tag in tags:
            if tag.find_element_by_xpath(".//a/em").text == company:
                link = tag.find_element_by_tag_name('a')
                ActionChains(driver).move_to_element(link).perform()
                link.click()
                driver.implicitly_wait(5)
                break
        while not link:
            try:
                next = driver.find_element_by_xpath("//li[@class='pagination-next ng-scope ']")
            except selenium.common.exceptions.NoSuchElementException:
                break
            else:
                next_link = next.find_element_by_tag_name('a')
                ActionChains(driver).move_to_element(next_link).perform()
                next_link.click()
                driver.implicitly_wait(5)
                tags = driver.find_elements_by_xpath("//div[@class='search_right_item ml10']")
                for tag in tags:
                    if tag.find_element_by_xpath(".//a/span").text == company:
                        link = tag.find_element_by_tag_name('a')
                        ActionChains(driver).move_to_element(link).perform()
                        link.click()
                        driver.implicitly_wait(5)
                        break

        # 转化句柄
        now_handle = driver.current_window_handle
        all_handles = driver.window_handles
        for handle in all_handles:
            if handle != now_handle:
                # 输出待选择的窗口句柄
                # print(handle)
                driver.switch_to.window(handle)
        return driver

    def read_config(self):
        with open("config.json", "r", encoding="utf-8") as load_f:
            config = json.load(load_f)
        return config


    #  获取所有表格和表单
    def scrapy(self, driver):
        driver.implicitly_wait(5)
        table = driver.find_elements_by_xpath("//div[@class='block-data']")
        # print(f"length of tables: {len(table)}")

        represnt = driver.find_elements_by_xpath("//div[@id='_container_baseInfo']//a[@target='_blank']")
        cap = table[0].find_elements_by_xpath("//table[@class='table']//tbody//tr//td")
        left_cap = []
        right_cap = []
        count = 0
        for i in range(1, 5):
            for j, div in enumerate(cap[i].find_elements_by_tag_name('div')):
                try:
                    div.text
                except AttributeError:
                    continue
                else:
                    if div.text != "股权结构图" and div.text != "查看详情" and div.text !="":
                        if count % 2 == 0:
                            left_cap.append(div)
                        else:
                            right_cap.append(div)
                        count += 1
        # right_cap = table[0].find_elements_by_xpath("//div[contains(@class, 'baseinfo-module-content-value')]")
        html = driver.page_source
        font_file_url = self.get_font_file(html)

        right_base = []
        left_base = []
        base = table[0].find_elements_by_xpath("//*[@class='table -striped-col -border-top-none']//tr//td")
        base_count = 0
        for element in base:
            # print(element.text, i)
            if element.text == "":
                continue
            if base_count % 2 == 0:
                left_base.append(element)
            if base_count % 2 == 1:
                right_base.append(element)
            base_count += 1

        list = {}
        list["法定代表人"] = represnt[0].text
        for i in range(len(left_cap)):
            replaced = self.font_match(font_file_url, right_cap[i].text)
            list[left_cap[i].text] = replaced

        for i in range(len(left_base)):
            if left_base[i].text == "核准日期":
                replaced = self.font_match(font_file_url, right_base[i].text)
                list[left_base[i].text] = replaced
            else:
                list[left_base[i].text] = right_base[i].text

        # print(f"items: {list}")

        return list

    def get_font_file(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        urls = soup.findAll('link', rel='stylesheet')
        for u in urls:
            url = u['href']
            if url.endswith("font.css"):
                response = request.urlopen(url)
                rules, encoding = tinycss2.parse_stylesheet_bytes(
                    css_bytes=response.read(),
                )
                for rule in rules:
                    if rule.type == "at-rule":
                        for list in rule.content:
                            if list.type == "url":
                                if list.value.endswith("woff"):
                                    return list.value

    def font_match(self, font_file_url, data):
        base_font = TTFont('./fonts/base_font.woff')
        base_names = ['5', '4', '0', '8', '1', '3', '2', '9', '6', '7', '_#266', '_#317', '_#48', '_#21', 'x']
        base_appears = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '人', '元', '万', '民', '.']

        dir = os.path.abspath('.')
        path = dir + '/fonts/font.woff'
        request.urlretrieve(font_file_url, path)
        font = TTFont('./fonts/font.woff')  # 打开文件
        cmap = font['cmap']
        names = []
        for c in data:
            uni = json.dumps(c)[1:-1]
            if len(uni) > 1:
                base_10 = int(uni[2:], 16)
                flag = 0  # does not find a match
                for item in cmap.tables[0].cmap.items():
                    if item[0] == base_10:
                        names.append(item[1])
                        flag = 1
                if flag == 0:
                    names.append("occupied")
            else:
                names.append(c)

        fonts = []
        for j, name in enumerate(names):
            if name == "occupied":
                fonts.append(data[j])
            else:
                try:
                    contour = font['glyf'][name]
                except KeyError:
                    fonts.append(data[j])
                else:
                    flag = 0  # 判断已知基础字典中是否有匹配字段
                    for i, base_name in enumerate(base_names):
                        base_contour = base_font['glyf'][base_name]
                        if base_contour == contour:
                            fonts.append(base_appears[i])
                            flag = 1  # 已知基础字典中含有匹配字段
                    if flag == 0:
                        fonts.append(data[j])  # 没有匹配项，使用原始数据
        return "".join(fonts)

    def font_match2(self, font_file_url, data):
        dir = os.path.abspath('.')
        path = dir + '/fonts/base_font.woff'
        request.urlretrieve(font_file_url, path)
        font = TTFont('./fonts/base_font.woff')  # 打开文件
        gly_list = font.getGlyphOrder()[2:12]
        dict = {}
        list = []

        if gly_list[-1] == "_":
            for num, gly in enumerate(gly_list):
                dict[gly] = str(num + 1)
        else:
            for num, gly in enumerate(gly_list):
                dict[gly] = str(num)

        for c in data:
            list.append(c)
        for i in range(len(list)):
            if list[i] in dict.keys():
                list[i] = dict[list[i]]
        return "".join(list)

    def trytable(self, x):
        # 是否需要去掉get_attribute ,得到的是table的名字 ,若没得表格到flag则为0
        try:
            x.find_element_by_tag_name('table').get_attribute('class')
            flag = 1
        except Exception:
            flag = 0
            print("这不是表格")
        return flag

    def tryonclick(self, x):
        # 测试是否有翻页
        try:
            # 找到有翻页标记
            x.find_element_by_tag_name('ul')
            onclickflag = 1
        except Exception:
            print("没有翻页")
            onclickflag = 0
        return onclickflag

    def jiexionclick(self, x, result):
        PageCount = x.find_element_by_xpath("//div[@class='total']").text
        PageCount = re.sub("\D", "", PageCount)  # 使用正则表达式取字符串中的数字 ；\D表示非数字的意思
        for i in range(PageCount - 1):
            button = x.find_element_by_xpath(".//li[@class='pagination-next  ']/a")
            button.click()
            table = x.find_element_by_tag_name('tbody')
            turnpagetable = self.jiexitable(table)
            result.append(turnpagetable)
        return result

    def jiexitable(self, x, id):
        rows = x.find_elements_by_tag_name('tr')
        # 第二个表格是th 有没有什么方法可以同时查找td或者th！！！！！ and 和 or
        cols = rows[0].find_elements_by_tag_name('td' or 'th')
        result = [[0 for col in range(len(cols)+2)] for row in range(len(rows))]
        # 创建一个二维列表
        for i in range(len(rows)):
            result[i][0] = id
            idd = str(uuid.uuid1())
            idd = idd.replace('-', '')
            result[i][1] = idd
            for j in range(len(cols)):
                result[i][j+2] = rows[i].find_elements_by_tag_name('td')[j].text
        data = list(map(tuple, result)) # 将列表变成元组格式才能被插入数据库中
        return data

    def baseInfo(self, idd):
        base = self.driver.find_element_by_xpath("//div[@class='company_header_width ie9Style']/div")
        # base '淘宝（中国）软件有限公司浏览40770\n高新企业\n电话：18768440137邮箱：暂无\n网址：http://www.atpanel.com
        # 地址：杭州市余杭区五常街道荆丰村'
        name = base.text.split('浏览')[0]
        tel = base.text.split('电话：')[1].split('邮箱：')[0]
        email = base.text.split('邮箱：')[1].split('\n')[0]
        web = base.text.split('网址：')[1].split('地址')[0]
        address = base.text.split('地址：')[1]
        abstract = self.driver.find_element_by_xpath("//div[@class='sec-c2 over-hide']//script")
        # 获取隐藏内容
        abstract = self.driver.execute_script("return arguments[0].textContent", abstract).strip()
        tabs = self.driver.find_elements_by_tag_name('table')
        rows = tabs[1].find_elements_by_tag_name('tr')
        cols = rows[0].find_elements_by_tag_name('td' and 'th')
        # 工商注册号
        reg_code = rows[0].find_elements_by_tag_name('td')[1].text
        # 注册地址
        reg_address = rows[5].find_elements_by_tag_name('td')[1].text
        # 英文名称
        english_name = rows[5].find_elements_by_tag_name('td')[1].text
        # 经营范围
        ent_range = rows[6].find_elements_by_tag_name('td')[1].text
        # 统一信用代码
        creditcode = rows[1].find_elements_by_tag_name('td')[1].text
        # 纳税人识别号
        tax_code = rows[2].find_elements_by_tag_name('td')[1].text
        # 营业期限
        deadline = rows[3].find_elements_by_tag_name('td')[1].text
        # 企业类型
        ent_type = rows[1].find_elements_by_tag_name('td')[3].text

        baseInfo = (idd, name, tel, email, web, address, abstract, reg_code, reg_address, english_name, ent_range,
                    creditcode, tax_code, deadline, ent_type)

        return baseInfo

    # def inser_sql(self, title, table):
    #
    #     if title == 'baseInfo':
    #         conn_mysql.baseInfo(table)
    #     elif title == 'staff':
    #         conn_mysql.staff(table)
    #     elif title == 'holder':
    #         conn_mysql.holder(table)
    #     elif title == 'invest':
    #         conn_mysql.invest(table)"
    #     elif title == 'jingpin':
    #         conn_mysql.jingpin(table)

if __name__ == "__main__":
    scrape = Scrape("面料图书馆")
    number, driver = scrape.login()
    #driver = scrape.select_company(driver, "面料图书馆") #上海金姿纺织装饰织造有限公司
    tags, names = scrape.get_company_list(driver)
    # list = scrape.scrapy(driver)
    print(number, names)

