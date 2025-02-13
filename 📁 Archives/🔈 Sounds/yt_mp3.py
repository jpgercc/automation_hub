import yt_dlp
import os

def baixar_musica(link):
    # Configurações para baixar apenas o vídeo específico, mesmo se for parte de uma playlist
    opcoes = {
        'format': 'bestaudio/best',  # Melhor qualidade de áudio disponível
        'postprocessors': [
            {  # Converte o áudio para MP3 após o download
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',  # Qualidade máxima do MP3
            }
        ],
        'outtmpl': '%(title)s.%(ext)s',  # Nome do arquivo de saída
        'quiet': False,  # Exibe o progresso no terminal
        'noplaylist': True,  # Garante que apenas o vídeo especificado será baixado
    }

    try:
        with yt_dlp.YoutubeDL(opcoes) as ydl:
            print(f"Baixando música do link: {link}")
            ydl.download([link])
            print("Download concluído!")
    except Exception as e:
        print(f"Ocorreu um erro: {e}")

if __name__ == "__main__":
    link = input("Digite o link do YouTube (apenas o vídeo desejado): ")
    baixar_musica(link)
