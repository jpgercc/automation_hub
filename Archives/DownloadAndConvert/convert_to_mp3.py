from moviepy.editor import AudioFileClip
import os

def converter_webm_para_mp4(input_file, output_file):
    try:
        # Carrega arquivo
        audio = AudioFileClip(input_file)

        # Converte e salva na pasta onde o script eh exe. como .mp4 (apenas audio)
        audio.write_audiofile(output_file, codec='aac')  # codec para .mp4

        print(f"Conversão concluída: {output_file}")
    except Exception as e:
        print(f"Erro durante a conversão: {e}")
    finally:
        audio.close()

if __name__ == "__main__":
    entrada = input("Digite o caminho do arquivo .webm: ")
    saida = os.path.splitext(entrada)[0] + ".mp4"
    
    converter_webm_para_mp4(entrada, saida)