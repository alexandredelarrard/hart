from glob import glob
import time
import numpy as np
import cv2
import matplotlib.pyplot as plt
from PIL import Image
from io import BytesIO
import random 
from selenium import webdriver

def crop(image):
    y_nonzero, x_nonzero, _ = np.nonzero(image)
    return image[np.min(y_nonzero):np.max(y_nonzero), np.min(x_nonzero):np.max(x_nonzero)]


def deduce_slider_x(driver): #captcha_0_4.PNG
      
    time.sleep(2)
    captcha = driver.find_element_by_class_name("geetest_window")

    # base_path = r"C:\Users\de larrard alexandre\Documents\repos_github\PAP\data\captcha_solve"
    # len_files = len(glob(base_path +"/*"))
    # captcha.screenshot(base_path + f'/captcha.png')

    image = np.array(Image.open(BytesIO(captcha.screenshot_as_png)))[:,:,0]

    # find where more shadow
    # image = cv2.imread(str(base_path) + f'/{driver}')
    # image = crop(image)[:,:,0]

    # image shape 
    shape = image.shape
    if shape[1] > 300:
        largeur_puzzle = 80
    else:
        largeur_puzzle = 40

    x_first_part = int(shape[1]*0.20)
    first_part = image[:,0:x_first_part]
    second_part = image[:,x_first_part:]

    (thresh, sub) = cv2.threshold(first_part, np.median(first_part.squeeze())*0.9, 255, cv2.THRESH_BINARY_INV)

    # sub image 
    sub_a = sub.sum(axis=1) / x_first_part
    sub_b = np.diff(sub_a)
    sub_b = np.where(abs(sub_b) < min(np.max(sub_b)*0.5, 3*np.mean(abs(sub_b))), 0, sub_b)

    f_y_index_min = 10 + np.argmin(sub_b[10:-10]) # to have middle of piece
    f_y_index_max = 10 + np.argmax(sub_b[10:-10])

    if f_y_index_max < f_y_index_min:
        tampon  = f_y_index_min
        f_y_index_min = f_y_index_max
        f_y_index_max = tampon

    if abs(f_y_index_max - f_y_index_min) < largeur_puzzle:
            middle= int((f_y_index_min + f_y_index_max)/2)
            f_y_index_min = max(10, middle - largeur_puzzle)
            f_y_index_max = min(middle + largeur_puzzle, shape[0] - 10)

    # plt.plot(range(len(sub_b[10:-10])), sub_b[10:-10])

    # analyse the rest
    s = second_part[f_y_index_min:f_y_index_max,:]
    # (thresh, s) = cv2.threshold(second_part[f_y_index_min:f_y_index_max,:], np.median(first_part.squeeze()), 255, cv2.THRESH_BINARY_INV)

    sub_a = s.sum(axis=0) / (f_y_index_max - f_y_index_min)
    sub_b = np.diff(sub_a)
    sub_b = np.where(abs(sub_b) < min(np.max(sub_b)*0.5, 3*np.mean(abs(sub_b))), 0, sub_b)

    y_index_min = 10 + np.argmin(sub_b[10:-10]) # to have middle of piece
    y_index_max = 10 + np.argmax(sub_b[10:-10])

    if y_index_max < y_index_min:
        tampon  = y_index_min
        y_index_min = y_index_max
        y_index_max = tampon

    # rule based 
    if abs(sub_b[y_index_min]) > abs(sub_b[y_index_max]) and abs(y_index_max - y_index_min) < largeur_puzzle/1.5:
        y_index_max = y_index_min + largeur_puzzle
    elif abs(sub_b[y_index_min]) < abs(sub_b[y_index_max]) and abs(y_index_max - y_index_min) < largeur_puzzle/1.5:
        y_index_min = y_index_max - largeur_puzzle

    if abs(sub_b[y_index_min]) > abs(sub_b[y_index_max]) and abs(y_index_max - y_index_min) > 1.5*largeur_puzzle:
        y_index_max = y_index_min + largeur_puzzle
    elif abs(sub_b[y_index_min]) < abs(sub_b[y_index_max]) and abs(y_index_max - y_index_min) > 1.5*largeur_puzzle:
        y_index_min = y_index_max - largeur_puzzle

    solution = x_first_part + (y_index_min + y_index_max)/2

    plt.imshow(image)
    plt.vlines(x =x_first_part+ y_index_max, ymin=0, ymax=shape[0], colors="red")
    plt.vlines(x =x_first_part+ y_index_min, ymin=0, ymax=shape[0], colors="red")
    plt.hlines(y = f_y_index_max, xmin=0, xmax=shape[1], colors="red")
    plt.hlines(y = f_y_index_min, xmin=0, xmax=shape[1], colors="red")
    plt.show()

    print(solution*200/shape[1])
    return solution*200/shape[1] 


def main_captcha(driver, restart_driver):

    time.sleep(4)
    i = 0

    # get zone of button to open captcha
    driver.switch_to.frame(driver.find_element(By.XPATH, "//iframe[@style='height:100vh;']")) 
    
    text = driver.find_element_by_tag_name("body").text
    if "bloqué" in text: 
        print("A ete bloqué")
        driver = restart_driver(driver)
        return driver

    btn = driver.find_element_by_class_name("geetest_holder")
    btn_click = driver.find_element_by_class_name("geetest_holder")

    actions = webdriver.ActionChains(driver)
    actions.move_to_element(btn).click(btn_click).perform()

    time.sleep(4)

    while len(driver.find_elements_by_class_name("geetest_slider_button"))>0 and i < 5:

        print(f"INTO WHILE")
        time.sleep(3)

        # solve captcha
        driver = solve_captcha(driver)

        i +=1

    return driver


def solve_captcha(driver):

    refresh = driver.find_element_by_class_name("geetest_refresh_1") 
    slider = driver.find_element_by_class_name("geetest_slider_button")

    x = deduce_slider_x(driver)

    actions = webdriver.ActionChains(driver)
    actions.move_to_element(slider).perform()

    if x >= 120:
        actions.click_and_hold(slider)
        actions.move_by_offset(x/32, random.uniform(-0.3, 0.3))
        actions.move_by_offset(x/4, random.uniform(-0.3, 0.3))
        actions.move_by_offset(x/4, random.uniform(-0.3, 0.3))
        actions.move_by_offset(x/8, random.uniform(-0.3, 0.3))
        actions.move_by_offset(x/8, random.uniform(-0.3, 0.3))
        actions.move_by_offset(x/8, random.uniform(-0.3, 0.3))
        actions.move_by_offset(x/16, random.uniform(-0.3, 0.3))
        actions.move_by_offset(x/32, random.uniform(-0.3, 0.3)).release().perform()
        time.sleep(4)

    else:
        actions.click_and_hold(slider)
        actions.move_by_offset(x/16, random.uniform(-0.3, 0.3))
        actions.move_by_offset(x/2, random.uniform(-0.3, 0.3))
        actions.move_by_offset(x/4, random.uniform(-0.3, 0.3))
        actions.move_by_offset(x/8, random.uniform(-0.3, 0.3))
        actions.move_by_offset(x/16, random.uniform(-0.3, 0.3)).release().perform()
        time.sleep(4)

    if len(driver.find_elements_by_class_name("geetest_refresh_1"))>0:
        actions = webdriver.ActionChains(driver)
        actions.move_to_element(refresh).click(refresh).perform()

    return driver