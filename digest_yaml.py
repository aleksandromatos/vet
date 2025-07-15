import re
import os

def corrigir_e_estruturar_yaml(arquivo_entrada, arquivo_saida):
    """
    Lê um arquivo YAML com formatação inconsistente, corrige a estrutura
    e salva um novo arquivo formatado corretamente.

    A lógica principal é:
    1. Ler todo o conteúdo do arquivo.
    2. Usar expressões regulares para identificar os blocos de cada "órgão".
    3. Para cada bloco de órgão, identificar os blocos de cada "doença".
    4. Formatar cada chave (doença) e valor (descrição) no padrão YAML desejado.
    5. Escrever o conteúdo formatado no arquivo de saída.
    """
    print(f"Lendo o arquivo de entrada: '{arquivo_entrada}'...")
    
    if not os.path.exists(arquivo_entrada):
        print(f"Erro: O arquivo de entrada '{arquivo_entrada}' não foi encontrado.")
        print("Certifique-se de que o script está na mesma pasta do seu arquivo YAML.")
        return

    with open(arquivo_entrada, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # --- Pré-correções para erros específicos e comuns ---
    # Corrige chaves concatenadas com valores ou outras chaves
    correcoes_especificas = {
        r'MielolipomaÁrea de Fibrose/ Mielolipoma:': "'Área de Fibrose/ Mielolipoma':",
        r'Hiperplasia Cística BenignaHiperplasia Cística Benigna': "'Hiperplasia Cística Benigna':",
        r'UlcerativaColite Histiocítica Ulcerativa': "'Colite Histiocítica Ulcerativa':",
        r'AdrenalectomiaAdrenalectomia': "'Adrenalectomia':"
    }
    for padrao, substituicao in correcoes_especificas.items():
        conteudo = re.sub(padrao, substituicao, conteudo)

    # --- Início da Estruturação ---
    linhas_corrigidas = []
    
    # Divide o conteúdo em blocos, onde cada bloco é um órgão.
    # O padrão r'\n(?=[A-ZÁÉÍÓÚÇÃÕ\s]{4,}:)' identifica um órgão pelo seu título em maiúsculas.
    blocos_orgaos = re.split(r'\n(?=[A-ZÁÉÍÓÚÇÃÕ\s]{4,}:)', conteudo)

    for bloco in blocos_orgaos:
        bloco = bloco.strip()
        if not bloco:
            continue

        linhas_bloco = bloco.split('\n')
        
        # A primeira linha do bloco é o nome do órgão
        chave_orgao = linhas_bloco[0].strip()
        linhas_corrigidas.append(chave_orgao)

        # O restante são as doenças e descrições
        conteudo_doencas = "\n".join(linhas_bloco[1:])
        
        # Divide o conteúdo do órgão em blocos de doenças, separados por uma ou mais linhas em branco
        blocos_doencas = re.split(r'\n\s*\n', conteudo_doencas)

        for doenca_bloco in blocos_doencas:
            doenca_bloco = doenca_bloco.strip()
            if not doenca_bloco:
                continue

            linhas_doenca = doenca_bloco.split('\n')
            
            # A primeira linha é a chave da doença
            chave_doenca = linhas_doenca[0].strip()
            # Remove o ':' se já existir, para evitar duplicação
            if chave_doenca.endswith(':'):
                chave_doenca = chave_doenca[:-1].strip()

            # Adiciona aspas se contiver caracteres especiais como '/'
            if '/' in chave_doenca:
                chave_doenca = f"'{chave_doenca}'"

            # Adiciona a chave da doença formatada
            linhas_corrigidas.append(f"    {chave_doenca}: |")
            
            # O restante das linhas é a descrição
            descricao = "\n".join(linhas_doenca[1:]).strip()
            
            # Adiciona cada linha da descrição com a indentação correta
            for linha_desc in descricao.split('\n'):
                # Adiciona indentação extra para o valor
                linhas_corrigidas.append(f"        {linha_desc.strip()}")
        
        linhas_corrigidas.append("") # Adiciona uma linha em branco entre os órgãos

    print("Processamento concluído. Gerando arquivo de saída...")
    
    # Escreve o resultado no arquivo de saída
    with open(arquivo_saida, 'w', encoding='utf-8') as f:
        f.write("\n".join(linhas_corrigidas))

    print(f"Sucesso! Arquivo corrigido e estruturado salvo como '{arquivo_saida}'.")


if __name__ == "__main__":
    arquivo_original = "laudo.yaml"
    arquivo_corrigido = "laudo_corrigido.yaml"
    corrigir_e_estruturar_yaml(arquivo_original, arquivo_corrigido)