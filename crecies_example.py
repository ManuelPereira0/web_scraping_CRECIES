from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import pyautogui, re, pymysql.cursors
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def iniciar_driver():
    driver = webdriver.Firefox()
    driver.get("https://area-restrita.crecies.gov.br/pesquisa-de-corretor-imobiliaria")
    return driver

def criar_conexao():
    return pymysql.connect(
        host='seu host',
        user='seu user',
        database='seu database',
        password='sua password',
        cursorclass=pymysql.cursors.DictCursor
    )

contador_registro = 1

conexao = criar_conexao()
cursor = conexao.cursor()

values = ["AFONSO CLAUDIO", "AGUA DOCE DO NORTE", "AGUIA BRANCA", "ALEGRE", "ALFREDO CHAVES",
"ALTO RIO NOVO", "ANCHIETA", "APIACA", "ARACRUZ", "ATILIO VIVACQUA", "BAIXO GUANDU",
"BARRA DE SAO FRANCISCO", "BOA ESPERANCA", "BOM JESUS DO NORTE", "BREJETUBA",
"CACHOEIRO DE ITAPEMIRIM", "CARIACICA", "CASTELO", "COLATINA", "CONCEICAO DA BARRA",
"CONCEICAO DO CASTELO", "DIVINO DE SAO LOURENCO", "DOMINGOS MARTINS", "DORES DO RIO PRETO",
"ECOPORANGA", "FUNDAO", "GOVERNADOR LINDENBERG", "GUACUI", "GUARAPARI", "IBATIBA",
"IBIRACU", "IBITIRAMA", "ICONHA", "IRUPI", "ITAGUACU", "ITAPEMIRIM", "ITARANA",
"IUNA", "JAGUARE", "JERONIMO MONTEIRO", "JOAO NEIVA", "LARANJA DA TERRA", "LINHARES",
"MANTENOPOLIS", "MARATAIZES", "MARECHAL FLORIANO", "MARILANDIA", "MIMOSO DO SUL", 
"MONTANHA", "MUCURICI", "MUNIZ FREIRE", "MUQUI", "NOVA VENECIA", "PANCAS", "PEDRO CANARIO",
"PINHEIROS", "PIUMA", "PONTO BELO", "PRESIDENTE KENNEDY", "RIO BANANAL", "RIO NOVO DO SUL",
"SANTA LEOPOLDINA", "SANTA MARIA DE JETIBA", "SANTA TERESA", "SAO DOMINGOS DO NORTE",
"SAO GABRIEL DA PALHA", "SAO JOSE DO CALCADO", "SAO MATEUS", "SAO ROQUE DO CANAA",
"SERRA", "SOORETAMA", "VARGEM ALTA", "VENDA NOVA DO IMIGRANTE", "VIANA", "VILA PAVAO", 
"VILA VALERIO", "VILA VELHA", "VITORIA"]



driver = iniciar_driver()

sleep(6)

botao_municipio = driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div[2]/div[1]/div/div[1]/div/ul/li[5]")
botao_municipio.click()

for value in values:
        
    sleep(2)

    pyautogui.moveTo(99, 485)
    sleep(0.5)

    pyautogui.click()
    sleep(0.5)

    pyautogui.write(value)
    sleep(0.5)

    pyautogui.press("enter")
    
    try:
        WebDriverWait(driver, 180).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.table > tbody:nth-child(1) > tr:nth-child(1) > td:nth-child(2) > dl:nth-child(1) > dd:nth-child(2)'))
        )
    except TimeoutException:
        print("Tempo de espera excedido. Elemento não encontrado.")
    

    pagina_html = driver.page_source
    soup = BeautifulSoup(pagina_html, 'html.parser')
    
    table = soup.find('table', class_="table table-sm table-hover table-striped")
    
    if not table:
        print("Tabela não encontrada")
    
    else:
        trs = table.find_all('tr')
        for tr in trs:
            sleep(0.5)
            text_nome = tr.find('a', class_='image-popup-no-margins')
            nome = text_nome.get('title') if text_nome else "Nome não encontrado"
            
            foto = tr.find('img', class_='rounded-circle img-thumbnail img-fluid')
            link_foto = foto.get('src')
            if link_foto and link_foto.startswith("http") and link_foto.endswith("FOTO.jpg"):
                foto_link = link_foto
            else:
                foto_link = "Não tem foto"
            
            print(foto_link)
                
            segundo_td = tr.select_one('td:nth-of-type(2)')
            if segundo_td:
                text_tr = segundo_td.get_text(strip=True, separator=' ').replace('\t', '').replace('\n', '')
            else:
                text_tr = ''
            
            padrao_creci = re.compile(r'([\d.]+-[A-Z]+)')
            padrao_ativo = re.compile(r'(Ativo)')
            padrao_cnai = re.compile(r'Nº CNAI\s*([0-9]+)')
            padrao_endereco_residencial = re.compile(r'Endereço Residencial (.+?Cep: \d{8})')
            padrao_endereco_comercial = re.compile(r'Endereço Comercial (.+?Cep: \d{8})')
            padrao_data = re.compile(r'\d{2}/\d{2}/\d{4}')
            
            crecis = padrao_creci.findall(text_tr)
            ativos = padrao_ativo.findall(text_tr)
            cnais = padrao_cnai.findall(text_tr)
            enderecos_residenciais = padrao_endereco_residencial.findall(text_tr)
            enderecos_comerciais = padrao_endereco_comercial.findall(text_tr)
            datas = padrao_data.findall(text_tr)
            
            creci = "Não tem CRECI"
            ativo = "Inativo"
            cnai = "Não tem CNAI"
            endereco_residencial = "Não tem endereco residencial"
            endereco_comercial = "Não tem endereco comercial" 
            data = "Não tem data de atualização"
            
            if crecis:
                creci = ', '.join(crecis)
                
            if ativos:
                ativo = ', '.join(ativos)
                
            if cnais:
                cnai = ', '.join(cnais)

            if enderecos_residenciais:
                endereco_residencial = ' '.join(enderecos_residenciais[0].split())
                print(endereco_residencial)
         
            if enderecos_comerciais:
                endereco_comercial = ' '.join(enderecos_comerciais[0].split())
                print(endereco_comercial)
            
            if datas:
                data = ', '.join(datas)
                
            
            query = f"""INSERT INTO (seu DB)
            (numero_registro, nome, tipo_pessoa, uf, linkFoto, situacao, numero_cnai,
            endereco_Residencial, endereco_comercial, data_atualizacao)
            VALUES ("{creci}", "{nome}", "fisica", "ES", "{foto_link}", "{ativo}", "{cnai}",
            "{endereco_residencial}", "{endereco_comercial}", "{data}")"""
            
            try:
                cursor.execute(query)
                conexao.commit()
            except:
                pass
            
            print(f"Dados inseridos no DB, registro {contador_registro}")
            contador_registro += 1 
        
        cursor.close()
        conexao.close()

        conexao = criar_conexao()
        cursor = conexao.cursor() 

driver.quit()