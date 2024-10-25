import yt_dlp
from moviepy.editor import AudioFileClip
import os

def baixar_video(url):
    try:
        # Baixa o video em .webm
        ydl_opts = {
            'format': 'bestvideo[ext=webm]+bestaudio[ext=webm]/best[ext=webm]',  # Prioriza download em webm
            'outtmpl': '%(title)s.%(ext)s',  # Nome do arquivo baseado no titulo
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            titulo = info['title']
            print(f"Titulo: {titulo}")
            print(f"Thumbnail: {info['thumbnail']}")

        print("Download concluído!")
        return f"{titulo}.webm"  # Retorna o nome do arquivo baixado

    except Exception as e:
        print(f"Ocorreu um erro durante o download: {e}")
        return None

def converter_webm_para_mp4(input_file):
    try:
        output_file = os.path.splitext(input_file)[0] + ".mp4"  # Define o nome do arquivo .mp4
        audio = AudioFileClip(input_file)

        # Converte para .mp4 e salva novo arquivo
        audio.write_audiofile(output_file, codec='aac')  
        print(f"Conversao concluida: {output_file}")

        # Deleta o arquivo .webm depois da conversao
        os.remove(input_file)
        print(f"Arquivo removido: {input_file}")

    except Exception as e:
        print(f"Erro durante a conversao: {e}")

    finally:
        if 'audio' in locals():
            audio.close()

if __name__ == "__main__":
    url = input("Cole aqui a URL do video: ")
    arquivo_webm = baixar_video(url)  # Baixa o video e obtem nome do arquivo

    if arquivo_webm:  # Converte o arquivo
        converter_webm_para_mp4(arquivo_webm)

#The video will be downloaded at the page the script was exe. in .webm 

#The video will be downloaded at the page the script was exe. in .mp4

#Video in .webm is deleted