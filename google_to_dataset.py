from logging import StreamHandler
from re import search
import bs4
from selenium import webdriver
import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import requests
import multiprocessing
from PIL import Image
import os
import re
import subprocess
import os.path


search_queries = []
user_input = ""


def download_image(url, folder_name, num):
    # write image to file
    response = requests.get(url)
    print(response.status_code)
    if response.status_code == 200:
        with open(os.path.join(folder_name, str(num) + ".jpg"), "wb") as file:
            file.write(response.content)


if __name__ == "__main__":
    while user_input != "End":
        user_input = input("Enter a search query (Type End to exit): ")
        if user_input != "End":
            search_queries.append(user_input)
        print(search_queries)

    for x in search_queries:
        # creating a directory to save images
        folder_name = x
        if not os.path.isdir(folder_name):
            os.makedirs(folder_name)

        s = Service("C:/bin/chromedriver")
        driver = webdriver.Chrome(service=s)
        driver.maximize_window()

        # put search words into a list
        searchWordsList = x.split()

        # turn list into word+word+word format
        searchWordsString = ""
        for word in searchWordsList:
            searchWordsString += word
            searchWordsString += "+"

        searchWordsString = searchWordsString[:-1]
        print(searchWordsString)
        search_URL = (
            "https://www.google.com/search?q="
            + searchWordsString
            + "&rlz=1C5CHFA_enCA952CA952&source=lnms&tbm=isch&sa=X&ved=2ahUKEwjk1rGU-4z0AhWuQzABHVApBSMQ_AUoAnoECAEQBA&biw=1200&bih=899&dpr=2"
        )
        driver.get(search_URL)

        page_scroll_sleep = 2
    
        # Get scroll height
        last_height = driver.execute_script("return document.body.scrollHeight")

        while True:
            # Scroll down to bottom
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait to load page
            time.sleep(page_scroll_sleep)

            # Calculate new scroll height and compare with last scroll height
            new_height = driver.execute_script("return document.body.scrollHeight")

            if new_height == last_height:
                # break #insert press load more
                try:
                    element = driver.find_elements(
                        By.CLASS_NAME, "mye4qd"
                    )  # returns list
                    element[0].click()
                except:
                    break
            last_height = new_height

        # scroll to the top
        driver.execute_script("window.scrollTo(0,0)")

        page_html = driver.page_source
        pageSoup = bs4.BeautifulSoup(page_html, "html.parser")
        containers = pageSoup.findAll("div", {"class": "isv-r PNCib MSM1fd BUooTd"})

        len_containers = len(containers)

        print("Found", len_containers, "containers")

        for i in range(1, len_containers + 1):
            try:
                print("Loaded image", i)

                xPath = """//*[@id="islrg"]/div[1]/div[%s]""" % (i)
                element = driver.find_element(By.XPATH, xPath)
                if element.get_attribute("class") == "isv-r PNCib MSM1fd BUooTd":
                    previewImageXPath = (
                        """//*[@id="islrg"]/div[1]/div[%s]/a[1]/div[1]/img""" % (i)
                    )
                    previewImageElement = driver.find_element(
                        By.XPATH, previewImageXPath
                    )
                    previewImageURL = previewImageElement.get_attribute("src")

                    driver.find_element(By.XPATH, xPath).click()

                # It's all about the wait
                timeStarted = time.time()
                while True:
                    imageElement = driver.find_element(
                        By.XPATH,
                        """//*[@id="Sva75c"]/div/div/div[3]/div[2]/c-wiz/div/div[1]/div[1]/div[2]/div[1]/a/img""",
                    )
                    imageURL = imageElement.get_attribute("src")

                    if imageURL != previewImageURL:
                        # print("actual URL", imageURL)
                        break

                    else:
                        # making a timeout if the full res image can't be loaded
                        currentTime = time.time()

                        if currentTime - timeStarted > 10:
                            print(
                                "Timeout! Will download a lower resolution image and move onto the next one"
                            )
                            break

                # Downloading image
                try:
                    if __name__ == "__main__":
                        # Start download_image as a process
                        p = multiprocessing.Process(
                            target=download_image,
                            args=(
                                imageURL,
                                folder_name,
                                i,
                            ),
                        )
                        p.start()

                        # Wait 10 seconds
                        initial_time = time.time()
                        while p.is_alive():
                            if time.time() - initial_time > 10:
                                p.terminate()
                                print("killed process")
                                break
                        p.join()

                    print(
                        "Downloaded element %s out of %s total. URL: %s"
                        % (i, len_containers + 1, imageURL)
                    )
                except:
                    print(
                        "Couldn't download an image %s, continuing downloading the next one"
                        % (i)
                    )
            except:
                print("image", i, "not processed")

for x in search_queries:
    dataset_path = f"D:/Programming/TensorFlow/{x}"
    jpg_list = os.listdir(dataset_path)
    if not os.path.isdir(f"P {x}"):
        os.makedirs(f"P {x}")
    num_list = []
    for l in jpg_list:
        num_list.append(re.compile(r"(\d+)").search(l).group(1))
        print(num_list)

    for i in num_list:
        try:
            im1 = Image.open(f"D:/Programming/TensorFlow/{x}/{i}.jpg")
            im1.save(f"D:/Programming/TensorFlow/P {x}/{i}.png")
            print("image", i, "saved")
        except:
            print("image", i, "failed")

for x in search_queries:
    print("HOLA")
    broken_imgs = []
    # step into the images folder
    os.chdir(f"P {x}")

    dataset_path = f"D:/Programming/TensorFlow/P {x}"
    png_list = os.listdir(dataset_path)
    for i in png_list:
        try:
            # give printout of incorrect sRGB profile
            process = subprocess.Popen(
                f"pngcrush_1_8_11_w64.exe pngcrush -n -q {i}",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
            )
            stdout, stderr = process.communicate()
            stderr = stderr.decode("utf-8")
            # print(stderr)
            if re.compile(r"iCCP: known incorrect sRGB profile").search(stderr):
                broken_imgs.append(i)
                print("image", i, "added to broken imgs")

        except:
            print("failed:", i)

    print(broken_imgs)

    for j in broken_imgs:
        try:
            os.remove(f"{j}")
            print(f"REMOVED: {j}")
        except:
            print("could not remove image", j)
    os.chdir("..")
