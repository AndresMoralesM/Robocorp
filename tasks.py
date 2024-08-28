from robocorp.tasks import task
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


@task
def minimal_task():
    #path=requests.request("get", "https://cloud.robocorp.com/api/v1/workspaces/c9fdb73c-1e53-42f0-b2bd-f9f54eb0533b/assets/fbf28151-2972-4431-aa99-f5efb2868c46", headers={
    #    "Content-Type": "application/json",
    #    "Authorization": "RC-WSKEY kv38phq90FXtJ7QSDoMEDBUXyPD2qeDJIehXIIAiqQVLIWGGXOOHTyDF8XcQhrZKNUCPDBK1t1NdpvxFCTSZyiyvzVNpR4aJesN9EN6qhTJY0Zd3mPnUZdXAJd0NM"
    #    })
    #print(path.json())
    edge_service = Service(executable_path="C:\\Users\\bella\\Downloads\\msedgedriver.exe")


    edge_options = Options()
    edge_options.add_argument('--ignore-certificate-errors')
    edge_options.add_argument('--ignore-ssl-errors')
	# Set up Edge WebDriver
    driver = webdriver.Edge(service=edge_service)

    driver.get("https://www.aljazeera.com/")

    try:
        button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-testid="menu-trigger"]'))
        )
        button.click()

        input_field = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[placeholder="Search"]'))
        )

        # Enviar un texto al campo de entrada
        input_text = "dollars saving"
        input_field.send_keys(input_text)
        print("it was sent")

        button = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'button[type="submit"].css-sp7gd'))
        )
        button.click()
        
        select_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "search-sort-option"))
        )

        # Crear un objeto Select
        select = Select(select_element)

        # Seleccionar la opción por su valor
        select.select_by_value("date")

        

        elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.search-result__list article'))
        )

        
        if not os.path.exists('imagenes'):
            os.makedirs('imagenes')

        search_results = []
        print(len(elements))
        print("cuantos gg")
        index=0
        for element in elements:
            
            try:
                title = element.find_element(By.CSS_SELECTOR, "a.u-clickable-card__link").text
                img_element = element.find_element(By.CSS_SELECTOR, 'img.article-card__image.gc__image')
                description = element.find_element(By.CSS_SELECTOR, "p").text
                search_text=title.lower() + description.lower()

                phraseCounter=0
                for phrase in input_text.split():
                    phraseCounter=len(search_text.split(phrase.lower()))+phraseCounter

                patron_dinero = r"\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?|(?:\d{1,3}(?:,\d{3})*(?:\.\d{2})?\s*(?:usd|dollars))"

                if re.search(patron_dinero, search_text.lower()):
                    containsMoney=True
                else:
                    containsMoney=False
                
                # Obtén la URL de la imagen
                img_url = img_element.get_attribute('src')
                
                # Descarga la imagen
                img_data = requests.get(img_url).content
                img_name = f'{title.split(" ")[0]}_{index + 1}.jpg'
                index+=1
                # Guarda la imagen en el directorio
                with open(os.path.join('imagenes', img_name), 'wb') as handler:
                    handler.write(img_data)


                
                #url = element.find_element(By.CSS_SELECTOR, "a.u-clickable-card__link").get_attribute("href")
                date = driver.find_element(By.CSS_SELECTOR, 'div.date-simple.css-1yjq2zp span[aria-hidden="true"]').text
                
                print(date)
                search_results.append({
                    "title": title,
                    "date": date,
                    "description": description,
                    "Picture_Name": img_name,
                    "Phrases_Counter": phraseCounter,
                    "Contains_Money": containsMoney

                })
            except Exception as e:
                print(f"Error al extraer datos de un resultado: {e}")

        # Convertir los resultados en un DataFrame de Pandas
        df = pd.DataFrame(search_results)

        # Mostrar el DataFrame
        print(df)
      

        
    
    except Exception as e:
        print("El botón no se pudo encontrar o hacer clic:", e)

    driver.implicitly_wait(10) 
