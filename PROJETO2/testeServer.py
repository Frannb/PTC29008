from app_server import Ordem, Sistema


lista_ordens = []
op = True
while op:
    opcao = int(input('''Selecione uma opção:
    1. Compra de Ativo
    2. Venda de Ativo
    3. Cancelamento de Ordem (compra ou venda de ativos)
    4. Informações do ativo
    0. Sair
    '''))

    s = Sistema()

    if opcao == 1:

        nome_ativo = input("Nome do ativo \n")
        preco = int(input("Preço \n"))
        num = int(input("Quantidade \n"))
        user = input(print("Usuário\n"))
        o = Ordem(ativo=nome_ativo, preco=preco, num=num, usuario=user)
        resultado = s.lanca_ordem(o)
        lista_ordens.append(o)

    elif opcao == 2:
        nome_ativo = input(print("Nome do ativo \n"))
        preco = int(input(print("Preço \n")))
        num = int(input(print("Quantidade \n")))
        user = input(print("Usuário\n"))
        o = Ordem(ativo=nome_ativo, preco=preco,
                  compra=False, num=num, usuario=user)
        resultado = s.lanca_ordem(o)
        lista_ordens.append(o)

    elif opcao == 3:
        print("Selecione o número da ordem que deseja cancelar \n")
        i = 0
        for ordem in lista_ordens:
            print(i, ". Ordem: ", ordem)
            i = 1 + i
        num_ordem = int(input())
        ordem_obj = lista_ordens.__getitem__(num_ordem)
        s.cancela(ordem_obj)

    elif opcao == 4:
        nome_ativo = input(print("Informe o nome do Ativo \n"))
        s.info(nome_ativo)
    else:
        print("encerrando...")
        op = False
