import sys

def converter_link_tg(link):
    if link.startswith("tg://resolve?domain="):
        # Extraímos o nome de usuário do link
        usuario = link[len("tg://resolve?domain="):]
        # Convertendo para o formato de URL do Telegram
        link_convertido = f"https://t.me/{usuario}"
        return link_convertido
    else:
        return "Link inválido ou não suportado"

if __name__ == "__main__":
    # Verificar se o usuário forneceu um argumento
    if len(sys.argv) != 2:
        print("Uso correto: python script.py <link_tg>")
        sys.exit(1)
    
    link_original = sys.argv[1]
    link_convertido = converter_link_tg(link_original)
    print(f"Link convertido: {link_convertido}")
def converter_link_tg(link):
    if link.startswith("tg://resolve?domain="):
        # Extraímos o nome de usuário do link
        usuario = link[len("tg://resolve?domain="):]
        # Convertendo para o formato de URL do Telegram
        link_convertido = f"https://t.me/{usuario}"
        return link_convertido
    else:
        return "Link inválido ou não suportado"

# Exemplo de uso
link_original = "tg://resolve?domain=example"
link_convertido = converter_link_tg(link_original)
print(f"Link convertido: {link_convertido}")
