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
