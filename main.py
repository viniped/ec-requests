import requests
import json
import os
import re
import random
import time
import pyfiglet
from colorama import Fore
from getpass4 import getpass
from concurrent.futures import ThreadPoolExecutor, as_completed
from config import *

start_time = time.time()

def convert_seconds_to_hms(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{int(hours)}:{int(minutes):02d}:{int(seconds):02d}"

class Banner:
    def __init__(self, Banner):
        self.banner = Banner
        self.lg = Fore.LIGHTGREEN_EX
        self.w = Fore.WHITE
        self.cy = Fore.CYAN
        self.ye = Fore.YELLOW
        self.r = Fore.RED
        self.n = Fore.RESET

    def print_banner(self):
        colors = [self.lg, self.w, self.cy, self.ye, self.r]
        f = pyfiglet.Figlet(font='slant')
        banner = f.renderText(self.banner)
        print(f'{random.choice(colors)}{banner}{self.n}')
        print(f'{self.r}  Version: 0.0.1 Author : @vinitemaceta \n{self.n}')

def banner():
    banner = Banner('EstrategiaConc')
    banner.print_banner()

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def sanitize_filename(filename):
    """Sanitiza o nome do arquivo removendo caracteres problemáticos."""
    sanitized = re.sub(r'[<>:"/\\|?*]', '', filename).strip()
    if len(sanitized) > 80:
        sanitized = sanitized[:80]  # Trunca nomes de arquivos longos
    return sanitized

def download_file(url, dest_folder, filename):
    """Baixa um arquivo de uma URL e salva na pasta especificada."""
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)
    
    file_path = os.path.join(dest_folder, filename)
    
    if os.path.exists(file_path):
        print(f"                {filename} [Already been Downloaded]")
        return False

    try:
        response = ss.get(url)
        with open(file_path, 'wb') as file:
            file.write(response.content)
        print(f"                {filename} [Downloaded]")
    except requests.exceptions.ConnectionError:
        time.sleep(random.randint(1, 8))
        response = ss.get(url)
        with open(file_path, 'wb') as file:
            file.write(response.content)
        print(f"                {filename} [Downloaded]")
    return True

def download_audio(url, dest_folder, filename):
    """Baixa um arquivo de áudio de uma URL e salva na pasta especificada."""
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)
    
    file_path = os.path.join(dest_folder, filename)
    
    if os.path.exists(file_path):
        print(f"                {filename} [Already been Downloaded]")
        return False

    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(file_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f"                {filename} [Downloaded]")
    except requests.exceptions.RequestException as e:
        print(f"Erro ao baixar o arquivo: {e}")
        return False
    return True

def download_content(url, folder, filename, index, content_type):
    """Função genérica para baixar conteúdos específicos."""
    if url:
        filename = sanitize_filename(f"{index:02d} - {filename}_{content_type}.pdf")
        download_file(url, folder, filename)
        return index + 1
    return index

def baixar_aula(aula, curso_folder, executor, tasks):
    index_video = 1
    index_pdf = 1
    index_audio = 1
    index_outros = 1

    aula_nome = sanitize_filename(aula['nome'])
    aula_folder = os.path.join(curso_folder, aula_nome)
    
    if not os.path.exists(aula_folder):
        os.makedirs(aula_folder)
    
    print(f"        {aula_nome}")
    
    # Baixar PDFs
    pdfs = {'pdf': aula.get('pdf'), 'pdf_grifado': aula.get('pdf_grifado'), 'pdf_simplificado': aula.get('pdf_simplificado')}
    pdf_folder = os.path.join(aula_folder, 'pdf')
    if not os.path.exists(pdf_folder):
        os.makedirs(pdf_folder)
    
    for pdf_type, pdf_url in pdfs.items():
        if pdf_url:
            pdf_filename = sanitize_filename(f"{index_pdf:02d} - {aula['nome']}.pdf")
            tasks.append(executor.submit(download_file, pdf_url, pdf_folder, pdf_filename))
            index_pdf += 1
    
    videos = aula.get('videos', [])
    resumo_list = []
    for v, video in enumerate(videos, start=0):
        if v + 1 < 10:
            nome_video = sanitize_filename(f"0{v + 1}")
        else:
            nome_video = sanitize_filename(f"{v + 1}")

        with open(os.path.join(curso_folder, 'mapa.txt'), 'a', encoding='utf-8') as mapa:
            mapa.write(f'       {nome_video}   >   {video["titulo"]}\n')
        print(f'        {nome_video}')
        
        if 'slide' in baixar:
            try:
                slide = video['slide']
                if slide:
                    print("         Baixando o slide")
                    os.makedirs(os.path.join(aula_folder, 'PDF'), exist_ok=True)
                    caminho = os.path.join(aula_folder, 'PDF', f'{nome_video}_Slide.pdf')
                    tasks.append(executor.submit(download_file, slide, aula_folder, caminho))
                else:
                    print("         Sem Slide")
            except KeyError:
                print("         Sem Slide")

        if 'mapa_mental' in baixar:
            try:
                mapa_mental = video['mapa_mental']
                if mapa_mental:
                    print("         Baixando o Mapa Mental")
                    os.makedirs(os.path.join(aula_folder, 'PDF'), exist_ok=True)
                    caminho = os.path.join(aula_folder, 'PDF', f'{nome_video}_Mapa Mental.pdf')
                    tasks.append(executor.submit(download_file, mapa_mental, aula_folder, caminho))
                else:
                    print("         Sem Mapa Mental")
            except KeyError:
                print("         Sem Mapa Mental")

        if 'resumo' in baixar:
            try:
                resumo = video['resumo']
                if resumo:
                    if resumo not in resumo_list:
                        resumo_list.append(resumo)
                        print("         Baixando o Resumo")
                        os.makedirs(os.path.join(aula_folder, 'PDF'), exist_ok=True)
                        caminho = os.path.join(aula_folder, 'PDF', f'{nome_video}_Resumo.pdf')
                        tasks.append(executor.submit(download_file, resumo, aula_folder, caminho))
                else:
                    print("         Sem Resumo")
            except KeyError:
                print("         Sem Resumo")

        if 'video' in baixar:
            try:
                video_user_resolucao = video['resolucoes'][user_resolucao]
                if video_user_resolucao:
                    print("         Baixando o vídeo")
                    os.makedirs(os.path.join(aula_folder, 'Vídeo'), exist_ok=True)
                    caminho = os.path.join(aula_folder, 'Vídeo', f'{nome_video}_Vídeo_aula.mp4')
                    tasks.append(executor.submit(download_file, video_user_resolucao, aula_folder, caminho))
            except KeyError:
                try:
                    for res in video['resolucoes']:
                        video_link = video['resolucoes'][res]
                        if video_link:
                            print("         Baixando o vídeo")
                            os.makedirs(os.path.join(aula_folder, 'Vídeo'), exist_ok=True)
                            caminho = os.path.join(aula_folder, 'Vídeo', f'{nome_video}_Vídeo_aula.mp4')
                            tasks.append(executor.submit(download_file, video_link, aula_folder, caminho))
                            break
                except KeyError:
                    print("         Sem vídeo")

        if 'audio' in baixar:
            try:
                audio = video['audio']
                if audio:
                    print("         Baixando o áudio")
                    os.makedirs(os.path.join(aula_folder, 'Vídeo'), exist_ok=True)
                    caminho = os.path.join(aula_folder, 'Vídeo', f'{nome_video}_Audio.mp3')
                    tasks.append(executor.submit(download_audio, audio, aula_folder, caminho))
                else:
                    print("         Aula sem áudio")
            except KeyError:
                print("         Aula sem áudio")

def baixar_conteudos(curso_response, curso_folder, aulas_selecionadas):
    curso_data = curso_response['data']
    curso_nome = sanitize_filename(curso_data['nome'])
    curso_folder = os.path.join(curso_folder, curso_nome)
    
    if not os.path.exists(curso_folder):
        os.makedirs(curso_folder)
    
    print(f"{curso_nome}")

    tasks = []
        
    with ThreadPoolExecutor(max_workers=threads) as executor:
        for i, aula in enumerate(curso_data.get('aulas', []), start=1):
            if i in aulas_selecionadas or 0 in aulas_selecionadas:
                baixar_aula(aula, curso_folder, executor, tasks)
    
    # Espera todas as tarefas terminarem
    for task in as_completed(tasks):
        task.result()

banner()
email = input("Insira seu e-mail: ")
password = getpass("Insira sua senha: ")
clear_console()

ss = requests.Session()

cookies = {}

headers = {
    'authority': 'www.estrategiaconcursos.com.br',
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
    'dnt': '1',
    'referer': 'https://www.estrategiaconcursos.com.br/app/dashboard',
    'sec-ch-ua': '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    "connection": "keep-alive",
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
}

data = {"email": email, "password": password}

response = ss.post('https://api.accounts.estrategia.com/auth/login', cookies=cookies, headers=headers, json=data)
access_token = response.cookies.get_dict()['__Secure-SID']
response = ss.get('https://www.estrategiaconcursos.com.br/oauth/token/', headers=headers)
cookies.update(response.cookies.get_dict())
headers['accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7'
headers['content-type'] = 'application/x-www-form-urlencoded'
data = {
    'access_token': access_token
}
response = ss.post('https://www.estrategiaconcursos.com.br/accounts/login/?goto=https://www.estrategiaconcursos.com.br/app/dashboard', cookies=cookies, headers=headers, data=data, allow_redirects=False)
cookies.update(response.cookies.get_dict())
response = ss.get('https://www.estrategiaconcursos.com.br/oauth/token/', cookies=cookies, headers=headers)
dados = json.loads(response.content)
headers['authorization'] = f"Bearer {dados['access_token']}"

response = ss.get('https://api.estrategiaconcursos.com.br/api/aluno/assinaturaInscricao', cookies=cookies, headers=headers).json()

produtos = response.get('data', [])

clear_console()
banner()

print("Cursos disponíveis para Download:")
for i, item in enumerate(produtos, 1):
    produto = item['produto']
    print(f"{i}. {produto['nome']} (ID: {produto['id']})")

ids_selecionados = []

while True:
    escolha = input("\nDigite o número do curso para baixar ou '0' para baixar todos: ")
    if escolha == '0':
        ids_selecionados = [produto['produto']['id'] for produto in produtos]
        clear_console()
        print("Todos os cursos foram selecionados.")
        break

    try:
        escolha = int(escolha) - 1
        if 0 <= escolha < len(produtos):
            produto_selecionado = produtos[escolha]['produto']
            produto_id = produto_selecionado['id']
            print(f"\nVocê escolheu o produto: {produto_selecionado['nome']} com ID: {produto_id}")
            ids_selecionados.append(produto_id)
            break  # Remova este break se quiser permitir múltiplas escolhas
        else:
            print("\nEscolha inválida. Tente novamente.")
    except ValueError:
        print("\nEntrada inválida. Por favor, insira um número válido.")

# Inicia o download dos cursos selecionados
for id_curso in ids_selecionados:
    curso_response = requests.get(f'https://api.estrategiaconcursos.com.br/api/aluno/pacote/{id_curso}', headers=headers).json()

    produto_nome = sanitize_filename(curso_response.get('data', {}).get('nome', 'produto'))

    produto_folder = os.path.join(os.getcwd(), produto_nome)
    if not os.path.exists(produto_folder):
        os.makedirs(produto_folder)

    clear_console()
    banner()

    cursos = curso_response.get('data', {}).get('cursos', [])
    print("Cursos disponíveis para Download dentro do produto:")
    for i, curso in enumerate(cursos, 1):
        print(f"{i}. {curso['nome']}")

    while True:
        escolha_cursos = input("\nDigite o número dos cursos para baixar separadas por vírgula (ex: 1,2,3) ou '0' para baixar todos: ")
        try:
            if escolha_cursos == '0':
                cursos_selecionados = [0]
                clear_console()
                print("Todos os cursos foram selecionados.")
                break
            else:
                cursos_selecionados = [int(x.strip()) for x in escolha_cursos.split(',')]
                if all(1 <= x <= len(cursos) for x in cursos_selecionados):
                    clear_console()
                    print(f"Cursos selecionados: {cursos_selecionados}")
                    break
                else:
                    print("Uma ou mais escolhas estão fora do intervalo. Tente novamente.")
        except ValueError:
            print("Entrada inválida. Por favor, insira números válidos separados por vírgula.")

    for i, curso in enumerate(cursos, 1):
        if i in cursos_selecionados or 0 in cursos_selecionados:
            curso_id = curso['id']
            detalhes_curso_response = requests.get(f'https://api.estrategiaconcursos.com.br/api/aluno/curso/{curso_id}', headers=headers).json()
            baixar_conteudos(detalhes_curso_response, produto_folder, [0])
        
end_time = time.time()
execution_time = end_time - start_time
formatted_time = convert_seconds_to_hms(execution_time)
atencao_txt_path = os.path.join(produto_folder, 'atenção.txt')
mensagem = f"O download do produto '{produto_nome}' levou {formatted_time}.\n mantenha tudo atualizado sempre !!! Faça uma doação ao desenvolvedor \n Compre um café : https://buymeacoffee.com/vinitemaceta"
with open(atencao_txt_path, 'w', encoding='utf-8') as file:
    file.write(mensagem)