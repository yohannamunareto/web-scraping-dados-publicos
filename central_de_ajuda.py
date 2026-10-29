"""Extrai título, texto e imagens dos artigos de uma central de ajuda.

Uso: python central_de_ajuda.py <url-da-secao> [<url-da-secao> ...]
"""
import logging
import os
import sys

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def criar_driver():
    options = uc.ChromeOptions()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # Caminho opcional do ChromeDriver via variável de ambiente
    caminho = os.getenv("CHROMEDRIVER_PATH")
    return uc.Chrome(options=options, driver_executable_path=caminho) if caminho else uc.Chrome(options=options)


def processar_links(links):
    driver = criar_driver()
    wait = WebDriverWait(driver, 10)
    try:
        for section_url in links:
            driver.get(section_url)
            logging.info(f"Seção {section_url} carregada, extraindo links dos artigos...")

            elementos = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/articles/"]')
            links_artigos = [e.get_attribute("href") for e in elementos]
            logging.info(f"Encontrados {len(links_artigos)} artigos na seção.")

            for artigo_url in links_artigos:
                logging.info(f"Acessando o artigo: {artigo_url}")
                try:
                    driver.get(artigo_url)
                    titulo = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1"))).text.strip()
                    conteudo = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.article-body"))).text.strip()
                    imagens = driver.find_elements(By.CSS_SELECTOR, "div.article-body img")
                    urls_imagens = [img.get_attribute("src") for img in imagens]
                    logging.info(f"Título: {titulo}")
                    logging.info(f"Conteúdo: {conteudo}")
                    logging.info(f"Imagens: {', '.join(urls_imagens)}")
                    logging.info("=" * 80)
                except Exception as erro:
                    logging.error(f"Erro ao extrair o artigo {artigo_url}: {erro}")
    except Exception as e:
        logging.error(f"Erro durante a extração: {e}")
    finally:
        driver.quit()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python central_de_ajuda.py <url-da-secao>")
        sys.exit(1)
    processar_links(sys.argv[1:])
