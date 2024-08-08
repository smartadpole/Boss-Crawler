# -*- coding: utf-8 -*-
"""
Created on 2022-10-20 04:36:10
@author: Zer-hex
"""
from time import sleep
import pandas as pd
from selenium.webdriver.common.by import By
from selenium import webdriver
from config import *

def main():
    login()
    search_lists = get_search_lists()
    for search_url in search_lists:
        get_jobs_lists(*search_url)


def login():
    browser.get('https://login.zhipin.com/')
    print("[+] 你有20秒的时间扫码登录boss直聘")
    sleep(20)
    browser.refresh()


def get_search_lists():
    urls = []
    for job in jobs:
        for city_code in citys:
            # url = f'https://www.zhipin.com/web/geek/job?query={job}&city={city_code}&experience={experience}&degree={degree}'
            url = f'https://www.zhipin.com/web/geek/job?query={job}&city={city_code}&experience={experience}&degree={degree}'
            urls.append((url, f"{job}.xlsx"))
    return urls


def get_jobs_lists(search_url, name):
    domain = name.split('.')[0].split('_')[-1]
    browser.get(search_url)
    print("Sleep")
    sleep(7)
    print("Wake Up")

    # browser.execute_script("window.scrollTo(0, document.body.scrollHeight)")   # 滚到底端，
    # sleep(1)
    page_num_tags = browser.find_elements(By.XPATH, '//*[@id="wrap"]/div[2]/div[2]/div/div[1]/div[2]/div/div/div/a')
    print(f"[+] 捕获页码标签,长度: {len(page_num_tags)}")
    if(len(page_num_tags) == 0): 
        sleep(20)
        page_num_tags = browser.find_elements(By.XPATH, '//*[@id="wrap"]/div[2]/div[2]/div/div[1]/div[2]/div/div/div/a')

    try :
        if len(page_num_tags) > 3:
            page_num = int(page_num_tags[-2].text)
        else:
            page_num = 1
        print(f"[+] 信息共{page_num}页, Url: {search_url}")
        for page in range(1, page_num):
            print(f"[+] 正在爬取第{page+1}页.")
            url = f"{search_url}&page={page+1}"
            # print(browser.get_cookie())
            browser.get(url)
            sleep(7)
            lis = browser.find_elements(By.XPATH, '//*[@id="wrap"]/div[2]/div[2]/div/div[1]/div[1]/ul/li')
            info = {
                '公司': [],
                '岗位': [],
                '薪资': [],
                '位置': [],
                '经验要求': [],
                '学历要求': [],
                '公司规模': [],
                '所属行业': [],
                '加分项目': [],
                '招聘人': [],
                '招聘人职位': [],
                '详情': [],
                '链接': [],
                '福利': [],
                '领域': []
            }
            for li in lis:
                recruiter_name = ""
                recruiter_position = ""
                job_link = ""
                job_detail = ""

                job_name = li.find_element(By.CLASS_NAME, 'job-name').text
                salary = li.find_element(By.CLASS_NAME, 'salary').text
                addr = li.find_element(By.CLASS_NAME, 'job-area').text
                tag_list = li.find_elements(By.CLASS_NAME, 'tag-list')
                tag_list1 = tag_list[0].find_elements(By.TAG_NAME, 'li')  
                tag_list1 = [i for i in tag_list1 if(i.text != '' and i.text != ' ')] # 要求
                tag_list2 = tag_list[1].find_elements(By.TAG_NAME, 'li')
                tag_list2 = [i for i in tag_list2 if(i.text != '' and i.text != ' ')] # 加分项
                experience = tag_list1[0].text
                degree = tag_list1[1].text
                excess = ', '.join([x.text for x in tag_list2])
                company_name = li.find_element(By.CLASS_NAME, 'company-name').text
                industry = li.find_element(By.CLASS_NAME, 'company-tag-list').find_elements(By.TAG_NAME, 'li')[0].text
                welfare = li.find_element(By.CLASS_NAME, 'info-desc').text
                company_tag_list = li.find_element(By.CLASS_NAME, 'company-tag-list') 
                company_people = "无"
                for x in company_tag_list.find_elements(By.TAG_NAME, 'li'): 
                    if("人" in x.text): company_people = x.text

                # 提取岗位详细链接
                try:
                    job_link = li.find_element(By.XPATH, ".//div[@class='job-card-body clearfix']/a[@class='job-card-left']").get_attribute('href')
                    # 提取招聘人名字
                    recruiter_name = li.find_element(By.XPATH, ".//div[@class='info-public']").text.split()[0]
                    # 提取招聘人职位
                    recruiter_position = li.find_element(By.XPATH, ".//div[@class='info-public']/em").text
                except:
                    pass

                # browser.get(job_link)
                # sleep(7)
                # try:
                #     job_detail =  browser.find_elements(By.CLASS_NAME, "job-sec-text")[0].get_attribute('innerHTML')
                #     job_detail.replace("<br>", "\n")
                # except:
                #     job_detail = ""

                print(f"[公司]: {company_name} [岗位]: {job_name} [薪资]: {salary} [经验要求]: {experience} [学历要求]: {degree} [加分项目]: {excess} [所属行业]: {industry} [位置]: {addr} [公司规模]:{company_people} [福利]: {welfare}")
                info['公司'].append(company_name)
                info['岗位'].append(job_name)
                info['薪资'].append(salary)
                info['经验要求'].append(experience)
                info['学历要求'].append(degree)
                info['加分项目'].append(excess)
                info['所属行业'].append(industry)
                info['位置'].append(addr)
                info['公司规模'].append(company_people)
                info['招聘人'].append(recruiter_name)
                info['招聘人职位'].append(recruiter_position)
                info['详情'].append(job_detail)
                info['链接'].append(job_link)
                info['福利'].append(welfare)
                info['领域'].append(domain)
            save_data(name, pd.DataFrame(info))
    except Exception as e:
        print(e)


def save_data(name: str, new_data: dict):
    try:
        data = pd.read_excel(name)
    except:
        data = pd.DataFrame({
            '公司': [],
            '岗位': [],
            '薪资': [],
            '位置': [],
            '经验要求': [],
            '学历要求': [],
            '公司规模': [],
            '所属行业': [],
            '加分项目': [],
            '招聘人': [],
            '招聘人职位': [],
            '详情': [],
            '链接': [],
            '福利': [],
            '领域': []
        })
    save = pd.concat([data, new_data], axis=0)
    save.to_excel(name, index=False)


if __name__ == '__main__':
    options = webdriver.ChromeOptions()  # 创建Chrome参数对象
    options.add_argument("--no-sandbox")  # 停用沙箱
    options.add_argument("--disable-dev-shm-usage")  # 利用本地临时文件夹作为chrome的运行空间
    # options.add_argument("--window-size=1920x1080")  # 设置分辨率
    # options.add_argument("--disable-gpu")  # 关闭Gpu
    # options.add_argument("--hide-scrollbars")  # 隐藏滚动条
    # options.binary_location = "/home/hao/Software/chromedriver"
    # options.add_argument("--blink-settings=imagesEnabled=false")  # 不加载图片
    # options.add_argument("--headless")  # 无界面模式
    browser = webdriver.Chrome(options=options)
    main()
    print("[+] Fuck boss success end ...")
    browser.quit()
