from robocorp.tasks import task
from RPA.Robocloud.Items import Items
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import Select
import pandas as pd
import os
import requests
import re
import time



def click(driver,selector,attempts=2,waitTime=10):
    
    for i in range(0,attempts):
        try:
            button = WebDriverWait(driver, waitTime).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
            )
            driver.execute_script("arguments[0].scrollIntoView();", button)
            button.click()
            return
        except Exception as e:
            if i == attempts-1:
                raise Exception(f"selector for buttom: {selector} could not be found after {attempts} attempts ")
            continue

def selectItem(driver,selector,option,attempts=2,waitTime=10):
    for i in range(0,attempts):
        try:
            select_element = WebDriverWait(driver, waitTime).until(
                    EC.presence_of_element_located((By.ID, selector))
                )
            select = Select(select_element)

            # Seleccionar la opción por su valor
            select.select_by_value(option)
            return
        except Exception as e:
            if i == attempts-1:
                raise Exception(f"selector for dropdown: {selector} could not be found after {attempts} attempts ")
            continue

def sendText(driver,selector,text,attempts=2,waitTime=10):
    for i in range(0,attempts):
        try:
            input_field = WebDriverWait(driver, waitTime).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
            input_field.send_keys(text) 
            return
        except Exception as e:
            if i == attempts-1:
                raise Exception(f"selector for Input Text: {selector} could not be found after {attempts} attempts ")
            continue


@task
def getNews():
    items = Items()
    data = items.get_input_work_item()
    path = data.payload.get("edgePath")
    input_text = data.payload.get("inputPhrase")
    section=data.payload.get("section")
    fileName=data.payload.get("fileName")
    print("Data from work item has been extracted sucessfully.")
   
  
    
    
    for i in range(0,3):
        try:
            edge_service = Service(executable_path=path)	
            driver = webdriver.Edge(service=edge_service)
            driver.get("https://www.aljazeera.com/")# Open website
            click(driver,'button[data-testid="menu-trigger"]')#Click on menu to unhide search bar
            
            sendText(driver,'input[placeholder="Search"]',input_text) # send search phrase 

            click(driver,'button[type="submit"].css-sp7gd')# Click on submit to search results
            
            selectItem(driver,"search-sort-option",section) # select date from dropdown options

            #Try to get all the results from the page.
            for i in range(0,9):
                try:
                    click(driver,'[data-testid="show-more-button"]')
                except Exception as e:
                    if i==0:
                        raise Exception("There is no any match")
                    else:
                        print("There are less than 99 results.")
            
            # a delay to wait for all results to load    
            time.sleep(8)           

            #Get all articles
            elements = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.search-result__list article'))
            )

            print(f"Articles for phrase: {input_text} have been founded ")
            #check for images folder
            if not os.path.exists('output\images'):
                os.makedirs('output\images')
                print(f"Images folder has been created {os.path.join('images')}")

            search_results = []
            
            index=0

            #For to get iterate in each article and extrac data
            for element in elements:
                
                try:
                    #Extract data
                    title = element.find_element(By.CSS_SELECTOR, "a.u-clickable-card__link").text
                    img_element = element.find_element(By.CSS_SELECTOR, 'img.article-card__image.gc__image')
                    description = element.find_element(By.CSS_SELECTOR, "p").text
                    search_text=title.lower() + description.lower()
                    date = element.find_element(By.CSS_SELECTOR, 'div.date-simple.css-1yjq2zp span[aria-hidden="true"]').text

                    #create counter phrase 
                    phraseCounter=0
                    for phrase in input_text.split():
                        phraseCounter=len(search_text.split(phrase.lower()))+phraseCounter
                    
                    #regex for Possible formats: $11.1 | $111,111.11 | 11 dollars | 11 USD
                    patron_dinero = r"\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?|(?:\d{1,3}(?:,\d{3})*(?:\.\d{2})?\s*(?:usd|dollars))" 

                    if re.search(patron_dinero, search_text.lower()):
                        containsMoney=True
                    else:
                        containsMoney=False
                    
                    # Get image url
                    img_url = img_element.get_attribute('src')
                    # Download image
                    img_data = requests.get(img_url).content
                    img_name = f'{title.split(" ")[0]}_{index + 1}.jpg'
                    index+=1
                    # save image in directory\images
                    with open(os.path.join('output\images', img_name), 'wb') as handler:
                        handler.write(img_data)

                    
                    #create table for results found
                    search_results.append({
                        "title": title,
                        "date": date,
                        "description": description,
                        "Picture_Name": img_name,
                        "Phrases_Counter": phraseCounter,
                        "Contains_Money": containsMoney
                    })
                except Exception as e:
                    print(f"Error could not extract data from an article: {e}")
                    continue
                
            print("Data from articles has been extracted")
            # Convert result into a pandas dataframe 
            df = pd.DataFrame(search_results)
            
            file_path = os.path.join('output', fileName)

            # Write the DataFrame to an Excel file
            df.to_excel(file_path, index=False, engine='openpyxl')
            print(f"Excel file has been created succesfully {str(file_path)}")

            print("Bot has run succesfully")
            break

    

            
        
        except Exception as e:
            if i == 2:
                raise Exception(f"{e} \n 3 attempts were performed from scratch")
            continue
            
    
