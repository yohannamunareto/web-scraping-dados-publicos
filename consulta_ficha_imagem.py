"""Consulta o contato profissional público em um cadastro on-line.

Alguns cadastros exibem os dados da ficha como imagem, então o script captura
a ficha, aplica OCR e extrai telefone e endereço com expressões regulares.

Configure o endereço do site e os seletores da página nas variáveis de
ambiente abaixo, de acordo com o site consultado.
"""
import os
import re
import time

import pytesseract
import requests
from bs4 import BeautifulSoup
from PIL import Image
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

if os.getenv("TESSERACT_CMD"):
    pytesseract.pytesseract.tesseract_cmd = os.getenv("TESSERACT_CMD")

URL_CADASTRO = os.getenv("URL_CADASTRO", "")
CAMPO_BUSCA = os.getenv("CAMPO_BUSCA_ID", "txtName")
BOTAO_BUSCA = os.getenv("BOTAO_BUSCA_ID", "btnFind")
AREA_RESULTADOS = os.getenv("AREA_RESULTADOS_ID", "resultContent")
LINHA_RESULTADO = os.getenv("LINHA_RESULTADO_CSS", ".rowName")
AREA_FICHA = os.getenv("AREA_FICHA_ID", "divResult")

PADRAO_TELEFONE = r"\(?\d{2,3}\)?[\s.-]?\d{4,5}[\s.-]?\d{4}"


def extrair_dados_da_imagem(caminho_imagem):
    """Lê a imagem com OCR e extrai telefone e endereço."""
    texto = pytesseract.image_to_string(Image.open(caminho_imagem), config="--psm 6")
    padrao_endereco = re.compile(
        r"(endereço.*?:?\s*[\w\s,º.-]+\s*-\s*[\w\s.-]*\d+)", re.IGNORECASE | re.DOTALL
    )
    telefones = re.findall(PADRAO_TELEFONE, texto)
    endereco = padrao_endereco.search(texto)
    return (telefones[0] if telefones else None,
            endereco.group(1).strip() if endereco else None)


def buscar_telefones_do_endereco(endereco):
    """Procura outros telefones associados ao endereço do escritório."""
    consulta = f"{endereco} escritório"
    headers = {"User-Agent": "Mozilla/5.0"}
    resposta = requests.get("https://www.google.com/search", params={"q": consulta}, headers=headers, timeout=30)
    if resposta.status_code != 200:
        print("Erro ao fazer a requisição de busca.")
        return []
    soup = BeautifulSoup(resposta.text, "html.parser")
    numeros = []
    for span in soup.find_all("span"):
        numeros.extend(re.findall(PADRAO_TELEFONE, span.get_text()))
    return list(set(numeros))


def buscar_profissional(nome):
    if not URL_CADASTRO:
        print("Defina a variável de ambiente URL_CADASTRO com o endereço do site.")
        return
    driver = webdriver.Chrome()
    try:
        driver.get(URL_CADASTRO)
        campo = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, CAMPO_BUSCA)))
        campo.send_keys(nome)
        driver.find_element(By.ID, BOTAO_BUSCA).click()

        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, AREA_RESULTADOS)))
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, LINHA_RESULTADO))).click()
        time.sleep(2)

        ficha = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, AREA_FICHA)))
        ficha.screenshot("resultado_ficha.png")

        telefone, endereco = extrair_dados_da_imagem("resultado_ficha.png")
        print(f"Telefone: {telefone or 'não encontrado'}")
        print(f"Endereço: {endereco or 'não encontrado'}")

        if endereco:
            for numero in buscar_telefones_do_endereco(endereco):
                print(f"Outro telefone do escritório: {numero}")

    except TimeoutException as e:
        print(f"Tempo de espera esgotado: {e}")
    except NoSuchElementException as e:
        print(f"Elemento não encontrado: {e}")
    finally:
        driver.quit()


if __name__ == "__main__":
    buscar_profissional(input("Digite o nome do profissional: ").strip().lower())
