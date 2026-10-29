# Web scraping de informações públicas

Scripts que extraem conteúdo de sites de forma automática e organizada, inclusive quando a informação aparece em imagem.


## Problema

O conteúdo de treinamento do sistema usado nas empresas estava espalhado em vários artigos online, sem uma versão consolidada para consulta.

Depois, surgiu a necessidade de consultar dados profissionais públicos que alguns sites exibem como imagem, o que impede a cópia direta.

## Como funciona

- `central_de_ajuda.py`: percorre cada seção de uma central de ajuda, coleta os links de todos os artigos e extrai título, texto e imagens de cada um. O conteúdo virou um manual em PDF.
- Registra cada etapa em log e trata erros artigo por artigo, para uma falha não interromper a extração.
- `consulta_ficha_imagem.py`: pesquisa um profissional pelo nome em um cadastro on-line e abre a ficha.
- Como o cadastro mostra os dados em imagem, o script captura a ficha, lê o texto com OCR e separa telefone e endereço com expressões regulares.

## Uso responsável

Use apenas em sites que permitem a coleta, respeitando os termos de uso de cada site e a LGPD. Os scripts consultam somente dados profissionais públicos.

## Como rodar

1. `pip install -r requirements.txt`
2. Para o `consulta_ficha_imagem.py`, instale o [Tesseract](https://github.com/tesseract-ocr/tesseract) e defina a variável `URL_CADASTRO` com o endereço do site.
3. Rode `python central_de_ajuda.py <url-da-secao>` ou `python consulta_ficha_imagem.py`.

## Ferramentas

Python, Selenium, undetected-chromedriver, Tesseract, BeautifulSoup e expressões regulares.

## Resultados

- Manual de treinamento consolidado em PDF.
- Ferramenta segue em uso para extrair informações públicas de sites que permitem esse uso.
