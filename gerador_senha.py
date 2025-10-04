usar_maiusculas = input("Usar letras maiúsculas? (s/n) ").lower() == "s"
usar_numeros = input("Usar números? (s/n) ").lower() == "s"
usar_simbolos = input("Usar símbolos? (s/n) ").lower() == "s"

caracteres = string.ascii_lowercase
if usar_maiusculas:
    caracteres += string.ascii_uppercase
if usar_numeros:
    caracteres += string.digits
if usar_simbolos:
    caracteres += string.punctuation
def gerar_multiplas_senhas(qtd=5, tamanho=8, simbolos=True):
    senhas = []
    for _ in range(qtd):
        senhas.append(gerar_senha(tamanho, simbolos))
    return senhas

qtd = int(input("Quantas senhas gerar? "))
for s in gerar_multiplas_senhas(qtd, tamanho=12, simbolos=True):
    print(s)
