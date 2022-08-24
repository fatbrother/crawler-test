import json
import os
import string
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
import urllib.request

options = webdriver.ChromeOptions()
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_experimental_option("prefs", {
                                "profile.password_manager_enabled": False, "credentials_enable_service": False, 'profile.default_content_settings.popups': 0})


def initCheckPoint() -> None:
    with open('checkPoint.json', 'r') as f:
        checkPoint = json.load(f)
    for key in checkPoint:
        checkPoint[key] = False
    with open('checkPoint.json', 'w') as f:
        json.dump(checkPoint, f)
    return None


def loadCheckPoint() -> dict:
    with open('checkPoint.json', 'r') as f:
        checkPoint = json.load(f)
    return checkPoint


def saveCheckPoint(checkPoint: dict) -> None:
    with open('checkPoint.json', 'w') as f:
        json.dump(checkPoint, f)
    return None


def main():
    # initCheckPoint()

    url = 'https://judgegirl.csie.org/problems/domain/0'

    # load dict of checkPoint in json file
    checkPoint = loadCheckPoint()

    # put r in a text file
    if not checkPoint['get problemSet']:
        with open('text.txt', 'w', encoding='UTF-8') as f:
            r = requests.get(url)
            # encode r into string
            f.write(r.text)

        # read text file
        # save all text between <li class="pure-menu-item" and </li> into a another text file
        with open('text.txt', 'r', encoding='UTF-8') as f:
            with open('problemSet.txt', 'w', encoding='UTF-8') as f2:
                for line in f:
                    if '<li class="pure-menu-item" data=' in line:
                        while '</li>' not in line:
                            f2.write(line)
                            line = f.readline()
                        f2.write(line)

        # delete text file
        os.remove('text.txt')

        # read problemSet.txt and save all problemSet id into a another text file
        with open('problemSet.txt', 'r', encoding='UTF-8') as f:
            with open('problemSetId.txt', 'w', encoding='UTF-8') as f2:
                for line in f:
                    if 'data="' in line:
                        f2.write(line[line.find('#'):-3])
                        f2.write('  ')
                        continue
                    if '</a></li>' in line:
                        # fine the first alpha index
                        start = 0
                        for i in range(len(line)):
                            if line[i].isalpha():
                                start = i
                                break
                        # replace all '/' with ''
                        target = line[start:-10]
                        target = target.replace('/', '')

                        if target.find('  ') > 4:
                            continue

                        f2.write(target)
                        f2.write('\n')

        # delete problemSet.txt
        os.remove('problemSet.txt')
        checkPoint['get problemSet'] = True
        saveCheckPoint(checkPoint)

    # read problemSetId.txt
    if not checkPoint['get problemId']:
        with open('problemSetId.txt', 'r', encoding='UTF-8') as f:
            # create a folder named the text after '  ' of each line
            for line in f:
                # test if the folder already exists

                folderName = line[line.find('  ')+2:-1]

                if not os.path.exists(folderName):
                    os.mkdir(folderName)

                driver = webdriver.Chrome(
                    'chromedriver.exe', chrome_options=options)
                driver.minimize_window()
                # create a file named Description.txt in each folder
                with open(folderName+'/Description.txt', 'w', encoding='UTF-8') as f2:
                    # goto the problemSet page
                    url = 'https://judgegirl.csie.org/problems/domain/0' + \
                        line[0:line.find('  ')]
                    driver.get(url)
                    # wait for the page to load
                    # driver.implicitly_wait(3)
                    elements = driver.find_elements(
                        By.CLASS_NAME, 'problem-item')
                    # write element into Description.txt
                    for element in elements:
                        print(element.text)
                        f2.write(element.text)
                        f2.write('\n')

                driver.close()
                driver.quit()
        checkPoint['get problemId'] = True
        saveCheckPoint(checkPoint)

    url = 'https://judgegirl.csie.org/problem/0'

    if not checkPoint['get problems']:
        # go to each problemSet folder in problemSetId.txt
        folderNames = list()
        with open('problemSetId.txt', 'r', encoding='UTF-8') as f:
            for line in f:
                folderNames.append(line[line.find('  ')+2:-1])

        problemSets = dict()
        for folderName in folderNames:
            with open(folderName + '/Description.txt', 'r', encoding='UTF-8') as f:
                problemSets[folderName] = list()
                for line in f:
                    problemSets[folderName].append(line[0:-1])

        for key in problemSets:
            for problem in problemSets[key]:
                title = problem
                id = problem[0:problem.find(' ') - 1]
                # if the last character of title is a punctuation, delete it
                if title[-1] in string.punctuation:
                    title = title[:-1]
                # replace all '/' with ' '
                title = title.replace('/', ' ')
                if title in checkPoint and checkPoint[title]:
                    continue

                print('Now downloading ' + title)

                driver = webdriver.Chrome(
                    'chromedriver.exe', chrome_options=options)
                driver.minimize_window()
                # goto the problem page
                url = 'https://judgegirl.csie.org/problem/0/' + id
                driver.get(url)
                # wait for the page to load
                # driver.implicitly_wait(3)
                
                if not os.path.exists(key+'/'+title):
                    os.mkdir(key+'/'+title)
                with open(key+'/'+title+'/Description.txt', 'w', encoding='UTF-8') as f:
                    f.write(driver.find_element(By.CLASS_NAME, 'content').text)

                # open the file with read and write permission
                with open(key+'/'+title+'/Description.txt', 'r', encoding='UTF-8') as f:
                    start = end = 0
                    for index, line in enumerate(f):
                        if 'Task Description' in line:
                            start = index
                        if 'Submit' in line:
                            end = index
                            break

                    # goto th top of the file
                    f.seek(0)
                    # save the line between start and end into newFile
                    newFile = f.readlines()[start:end]

                with open(key+'/'+title+'/Description.txt', 'w', encoding='UTF-8') as f2:
                    # clear the file
                    f2.truncate()
                    # write the new file
                    for line in newFile:
                        f2.write(line)

                # find the photo and save it
                photos = driver.find_elements(
                    By.CLASS_NAME, 'pure-img-responsive')
                if len(photos) != 0:
                    for index, photo in enumerate(photos):
                        link = photo.get_attribute('src')
                        # save the phot
                        if 'https://judgegirl.csie.org/images/problems/' in link:
                            urllib.request.urlretrieve(link, key+'/'+title+'/'+link[44:])
                            
                if not os.path.exists(key+'/'+title+'/testCases'):
                    os.mkdir(key+'/'+title+'/testCases')
                # find the elements that inside text is 'Download Testdata' by XPATH
                link = 'https://judgegirl.csie.org/testdata/download/' + id
                print(title)
                print(url)
                print(link)
                # goto the testCase page
                driver.get(link)
                # wait for the page to load
                # driver.implicitly_wait(3)

                content = driver.find_element(By.CLASS_NAME, 'content')
                menu = content.find_element(By.CLASS_NAME, 'pure-g')
                cases = menu.find_elements(By.CLASS_NAME, 'pure-menu-link')

                # download each testCase
                for case in cases:
                    url = case.get_attribute('href')
                    file = requests.get(url)
                    with open(key+'/'+title+'/testCases/'+case.text, 'wb') as f:
                        f.write(file.content)

                driver.close()
                driver.quit()

                checkPoint[title] = True
                saveCheckPoint(checkPoint)
        checkPoint['get problems'] = True
        saveCheckPoint(checkPoint)

    # check if all checkPoint is True
    for key in checkPoint:
        if not checkPoint[key]:
            print(key+' is not finished')
            return None
    print('all checkPoint is finished')
    return None


if __name__ == '__main__':
    main()