import streamlit as st
import pandas as pd
import sqlite3

# Conexão com o banco de dados SQLite
conn = sqlite3.connect('oficina.db')
c = conn.cursor()

# Criar tabela de clientes se ainda não existir
c.execute('''CREATE TABLE IF NOT EXISTS clientes
             (id INTEGER PRIMARY KEY, nome TEXT, telefone TEXT, email TEXT, data_entrada DATE)''')

# Criar tabela de itens do estoque se ainda não existir
c.execute('''CREATE TABLE IF NOT EXISTS estoque
             (id INTEGER PRIMARY KEY, item TEXT, quantidade INTEGER, preco_compra REAL, preco_venda REAL)''')

# Criar tabela de ordens de serviço se ainda não existir
c.execute('''CREATE TABLE IF NOT EXISTS ordens
             (id INTEGER PRIMARY KEY, cliente_id INTEGER, item TEXT, quantidade INTEGER, total REAL)''')

# Função para adicionar clientes ao banco de dados
def adicionar_cliente(nome, telefone, email, data_entrada):
    c.execute("INSERT INTO clientes (nome, telefone, email, data_entrada) VALUES (?, ?, ?, ?)", (nome, telefone, email, data_entrada))
    conn.commit()

# Função para adicionar itens ao estoque no banco de dados
def adicionar_item_estoque(item, quantidade, preco_compra, preco_venda):
    c.execute("INSERT INTO estoque (item, quantidade, preco_compra, preco_venda) VALUES (?, ?, ?, ?)", (item, quantidade, preco_compra, preco_venda))
    conn.commit()

# Função para simular ordens de serviço e atualizar o estoque
def simular_ordem(cliente_id, item, quantidade, total):
    c.execute("INSERT INTO ordens (cliente_id, item, quantidade, total) VALUES (?, ?, ?, ?)", (cliente_id, item, quantidade, total))
    c.execute("UPDATE estoque SET quantidade = quantidade - ? WHERE item = ?", (quantidade, item))
    conn.commit()

# Função para exibir clientes
def exibir_clientes():
    st.header('Clientes Cadastrados')
    clientes = pd.read_sql_query("SELECT * FROM clientes", conn)
    st.dataframe(clientes)

# Função para exibir itens do estoque
def exibir_estoque():
    st.header('Estoque de Peças')
    estoque = pd.read_sql_query("SELECT * FROM estoque", conn)
    st.dataframe(estoque)

# Função para exibir ordens de serviço
def exibir_ordens():
    st.header('Ordens de Serviço')
    ordens = pd.read_sql_query("SELECT * FROM ordens", conn)
    st.dataframe(ordens)

# Página para adicionar cliente
def adicionar_cliente_page():
    st.header('Adicionar Cliente')
    nome = st.text_input('Nome do cliente:')
    telefone = st.text_input('Telefone do cliente:')
    email = st.text_input('Email do cliente:')
    data_entrada = st.date_input('Data de entrada da moto do cliente:')
    if st.button('Adicionar'):
        adicionar_cliente(nome, telefone, email, data_entrada)
        st.success('Cliente adicionado com sucesso!')

# Página para adicionar item ao estoque
def adicionar_item_page():
    st.header('Adicionar Item ao Estoque')
    item = st.text_input('Nome do item:')
    quantidade = st.number_input('Quantidade:', min_value=1, value=1)
    preco_compra = st.number_input('Preço de compra por unidade:')
    preco_venda = st.number_input('Preço de venda por unidade:')
    if st.button('Adicionar'):
        adicionar_item_estoque(item, quantidade, preco_compra, preco_venda)
        st.success('Item adicionado ao estoque com sucesso!')
        # Exibir tabela atualizada com os itens no estoque
        exibir_estoque()

# Página para simular ordem de serviço
def simular_ordem_page():
    st.header('Simulação de Ordem de Serviço')
    exibir_clientes()
    cliente_id = st.number_input('ID do cliente:', min_value=1)
    
    # Recuperar a data de entrada da moto do cliente
    data_entrada = pd.read_sql_query("SELECT data_entrada FROM clientes WHERE id = ?", conn, params=(cliente_id,))
    if not data_entrada.empty:
        data_entrada = data_entrada.iloc[0]['data_entrada']
        st.write(f'Data de entrada da moto do cliente: {data_entrada}')
    else:
        st.warning('Cliente não encontrado ou data de entrada não registrada.')

    # Recuperar os itens disponíveis no estoque do banco de dados
    estoque_items = pd.read_sql_query("SELECT item, preco_venda FROM estoque", conn)

    items = []
    total_venda = 0.0

    st.write('**Itens da Ordem de Serviço:**')
    num_items = st.number_input('Quantidade de itens:', min_value=1, value=1)
    col1, col2, col3 = st.columns(3)  # Dividir a tela em três colunas para exibir os itens
    for i in range(num_items):
        with col1:
            item = st.selectbox(f'Selecione o item {i+1}:', options=estoque_items['item'], key=f'item_selectbox_{i}')
        with col2:
            quantidade = st.number_input(f'Quantidade do item {i+1}:', min_value=1, value=1)
        with col3:
            preco_venda = estoque_items.loc[estoque_items['item'] == item, 'preco_venda'].iloc[0]
            items.append((item, quantidade, preco_venda))

    total_venda = sum([quantidade * preco_venda for item, quantidade, preco_venda in items])

    if st.button('Simular Ordem'):
        for item, quantidade, _ in items:
            simular_ordem(cliente_id, item, quantidade, total_venda)
        st.success(f'Ordem de serviço simulada com sucesso! Total da venda: R${total_venda:.2f}')
        exibir_ordens()
        exibir_estoque()

    # Exibir tabela com os itens selecionados para a ordem de serviço
    st.write('**Itens Selecionados para a Ordem de Serviço:**')
    df_items = pd.DataFrame(items, columns=['Item', 'Quantidade', 'Preço de Venda'])
    st.dataframe(df_items)

# Configuração da barra lateral
st.sidebar.title('Menu')
menu_options = ['Adicionar Cliente', 'Adicionar Item ao Estoque', 'Simular Ordem de Serviço']
choice = st.sidebar.radio('Selecione uma opção:', menu_options)

# Mostra a página selecionada
if choice == 'Adicionar Cliente':
    adicionar_cliente_page()
elif choice == 'Adicionar Item ao Estoque':
    adicionar_item_page()
elif choice == 'Simular Ordem de Serviço':
    simular_ordem_page()

# Fechar a conexão com o banco de dados no final da execução
conn.close()
