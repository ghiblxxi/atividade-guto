def poder_ataque(magia, nivel):
    """
    Calcula o poder de ataque de um feiticeiro
    """
    return magia * nivel

# Teste rápido
if __name__ == "__main__":
    print("Poder de ataque:", poder_ataque(10, 5))
