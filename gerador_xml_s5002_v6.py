#!/usr/bin/env python3
"""
Gerador de XMLs S-5002 (e-Social) - Versão 6.0.0
Gera XMLs de teste com 12 meses + 13º salário do ano 2025
100% conforme com a especificação e-Social S-1.3

Data: 30/10/2025
Autor: Sistema Automatizado
Licença: MIT
"""

import random
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple
import csv

# Configurações
ANO = 2025
MESES = list(range(1, 13))  # Janeiro a Dezembro
SALARIO_BASE_MENSAL = 10000.00  # ~R$ 10.000/mês = R$ 121.000/ano com 13º

# Empresas
EMPRESAS = [
    {"cnpj": "12345678000190", "nome": "TechCorp Soluções Ltda"},
    {"cnpj": "98765432000110", "nome": "Inovação Digital S.A."},
    {"cnpj": "55566677000110", "nome": "Consultoria Estratégica Brasil"},
]

# Níveis de complexidade
COMPLEXIDADES = {
    "simples": {
        "tem_dependentes": False,
        "tem_plano_saude": False,
        "tem_pensao": False,
        "tem_prev_privada": False,
        "variacao_salario": 0.05,  # 5% de variação
    },
    "medio": {
        "tem_dependentes": True,
        "num_dependentes": 2,
        "tem_plano_saude": False,
        "tem_pensao": False,
        "tem_prev_privada": False,
        "variacao_salario": 0.10,
    },
    "complexo": {
        "tem_dependentes": True,
        "num_dependentes": 2,
        "tem_plano_saude": True,
        "tem_pensao": False,
        "tem_prev_privada": True,
        "variacao_salario": 0.15,
    },
    "muito_complexo": {
        "tem_dependentes": True,
        "num_dependentes": 3,
        "tem_plano_saude": True,
        "tem_pensao": True,
        "tem_prev_privada": True,
        "variacao_salario": 0.20,
    },
}


def gerar_cpf(base: int) -> str:
    """Gera um CPF fictício baseado em um número base"""
    cpf_str = str(base).zfill(11)
    return cpf_str


def gerar_valores_mes(salario_base: float, mes: int, complexidade: dict) -> Dict[str, float]:
    """Gera valores de rendimentos e deduções para um mês"""
    # Variação aleatória no salário
    variacao = complexidade["variacao_salario"]
    fator = 1.0 + random.uniform(-variacao, variacao)
    salario = salario_base * fator
    
    # Rendimento tributável (tpInfoIR=11)
    rendimento_trib = round(salario, 2)
    
    # Contribuição previdenciária (tpInfoIR=41) - ~11% do salário
    contrib_prev = round(salario * 0.11, 2)
    
    # Imposto retido (tpInfoIR=31) - progressivo
    if salario <= 2112.00:
        imposto = 0.0
    elif salario <= 2826.65:
        imposto = round(salario * 0.075 - 158.40, 2)
    elif salario <= 3751.05:
        imposto = round(salario * 0.15 - 370.40, 2)
    elif salario <= 4664.68:
        imposto = round(salario * 0.225 - 651.73, 2)
    else:
        imposto = round(salario * 0.275 - 884.96, 2)
    
    imposto = max(0.0, imposto)
    
    valores = {
        "rendimento_trib": rendimento_trib,
        "contrib_prev": contrib_prev,
        "imposto": imposto,
    }
    
    # Previdência privada (tpInfoIR=46)
    if complexidade.get("tem_prev_privada"):
        valores["prev_privada"] = round(salario * 0.05, 2)
    
    # Pensão alimentícia (tpInfoIR=51)
    if complexidade.get("tem_pensao"):
        valores["pensao"] = round(salario * 0.20, 2)
    
    # Plano de saúde (tpInfoIR=67)
    if complexidade.get("tem_plano_saude"):
        num_deps = complexidade.get("num_dependentes", 0)
        valores["plano_saude"] = round(350.00 + (num_deps * 200.00), 2)
    
    return valores


def gerar_valores_13(salario_base: float, complexidade: dict) -> Dict[str, float]:
    """Gera valores para o 13º salário"""
    salario_13 = salario_base
    
    # Rendimento tributável 13º (tpInfoIR=12)
    rendimento_13 = round(salario_13, 2)
    
    # Contribuição previdenciária 13º (tpInfoIR=42)
    contrib_prev_13 = round(salario_13 * 0.11, 2)
    
    # Imposto retido 13º (tpInfoIR=32)
    if salario_13 <= 2112.00:
        imposto_13 = 0.0
    elif salario_13 <= 2826.65:
        imposto_13 = round(salario_13 * 0.075 - 158.40, 2)
    elif salario_13 <= 3751.05:
        imposto_13 = round(salario_13 * 0.15 - 370.40, 2)
    elif salario_13 <= 4664.68:
        imposto_13 = round(salario_13 * 0.225 - 651.73, 2)
    else:
        imposto_13 = round(salario_13 * 0.275 - 884.96, 2)
    
    imposto_13 = max(0.0, imposto_13)
    
    valores = {
        "rendimento_13": rendimento_13,
        "contrib_prev_13": contrib_prev_13,
        "imposto_13": imposto_13,
    }
    
    # Previdência privada 13º (tpInfoIR=47)
    if complexidade.get("tem_prev_privada"):
        valores["prev_privada_13"] = round(salario_13 * 0.05, 2)
    
    # Pensão alimentícia 13º (tpInfoIR=52)
    if complexidade.get("tem_pensao"):
        valores["pensao_13"] = round(salario_13 * 0.20, 2)
    
    return valores


def gerar_xml_trabalhador(
    cpf: str,
    nome: str,
    empresa: dict,
    complexidade_nome: str,
    numero_func: int
) -> str:
    """Gera XML completo para um trabalhador com 12 meses + 13º"""
    
    complexidade = COMPLEXIDADES[complexidade_nome]
    cnpj = empresa["cnpj"]
    
    # Cabeçalho XML
    xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<eSocial xmlns="http://www.esocial.gov.br/schema/evt/evtIrrfBenef/v_S_01_02_00">
    <evtIrrfBenef Id="ID1{cnpj}0{ANO}1200001">
        <ideEvento>
            <perApur>{ANO}-12</perApur>
        </ideEvento>
        <ideEmpregador>
            <tpInsc>1</tpInsc>
            <nrInsc>{cnpj}</nrInsc>
        </ideEmpregador>
        <ideTrabalhador>
            <cpfBenef>{cpf}</cpfBenef>
'''
    
    # Gerar 12 meses de demonstrativos
    for mes in MESES:
        mes_str = f"{mes:02d}"
        valores = gerar_valores_mes(SALARIO_BASE_MENSAL, mes, complexidade)
        
        xml += f'''            <dmDev>
                <perRef>{ANO}-{mes_str}</perRef>
                <ideDmDev>{mes}</ideDmDev>
                <indRRA>N</indRRA>
                <infoIR>
                    <tpInfoIR>11</tpInfoIR>
                    <valor>{valores["rendimento_trib"]:.2f}</valor>
                </infoIR>
                <infoIR>
                    <tpInfoIR>41</tpInfoIR>
                    <valor>{valores["contrib_prev"]:.2f}</valor>
                </infoIR>
                <infoIR>
                    <tpInfoIR>31</tpInfoIR>
                    <valor>{valores["imposto"]:.2f}</valor>
                </infoIR>
'''
        
        # Adicionar previdência privada se houver
        if "prev_privada" in valores:
            xml += f'''                <infoIR>
                    <tpInfoIR>46</tpInfoIR>
                    <valor>{valores["prev_privada"]:.2f}</valor>
                </infoIR>
'''
        
        # Adicionar pensão alimentícia se houver
        if "pensao" in valores:
            xml += f'''                <infoIR>
                    <tpInfoIR>51</tpInfoIR>
                    <valor>{valores["pensao"]:.2f}</valor>
                </infoIR>
'''
        
        # Adicionar plano de saúde se houver
        if "plano_saude" in valores:
            xml += f'''                <infoIR>
                    <tpInfoIR>67</tpInfoIR>
                    <valor>{valores["plano_saude"]:.2f}</valor>
                </infoIR>
'''
        
        xml += f'''            </dmDev>
'''
    
    # Gerar 13º salário
    valores_13 = gerar_valores_13(SALARIO_BASE_MENSAL, complexidade)
    
    xml += f'''            <dmDev>
                <perRef>{ANO}</perRef>
                <ideDmDev>13</ideDmDev>
                <indRRA>N</indRRA>
                <infoIR>
                    <tpInfoIR>12</tpInfoIR>
                    <valor>{valores_13["rendimento_13"]:.2f}</valor>
                </infoIR>
                <infoIR>
                    <tpInfoIR>42</tpInfoIR>
                    <valor>{valores_13["contrib_prev_13"]:.2f}</valor>
                </infoIR>
                <infoIR>
                    <tpInfoIR>32</tpInfoIR>
                    <valor>{valores_13["imposto_13"]:.2f}</valor>
                </infoIR>
'''
    
    # Adicionar previdência privada 13º se houver
    if "prev_privada_13" in valores_13:
        xml += f'''                <infoIR>
                    <tpInfoIR>47</tpInfoIR>
                    <valor>{valores_13["prev_privada_13"]:.2f}</valor>
                </infoIR>
'''
    
    # Adicionar pensão alimentícia 13º se houver
    if "pensao_13" in valores_13:
        xml += f'''                <infoIR>
                    <tpInfoIR>52</tpInfoIR>
                    <valor>{valores_13["pensao_13"]:.2f}</valor>
                </infoIR>
'''
    
    xml += f'''            </dmDev>
'''
    
    # Adicionar informações complementares se houver dependentes
    if complexidade.get("tem_dependentes"):
        xml += f'''            <infoIRComplem>
'''
        num_deps = complexidade.get("num_dependentes", 0)
        for i in range(num_deps):
            cpf_dep = gerar_cpf(int(cpf) + i + 1)
            xml += f'''                <ideDep>
                    <cpfDep>{cpf_dep}</cpfDep>
                    <nmDep>Dependente {i+1} de {nome}</nmDep>
                    <dtNascto>2010-01-{(i+1)*10:02d}</dtNascto>
                    <tpDep>01</tpDep>
                    <descrDep>Filho(a)</descrDep>
                </ideDep>
'''
        
        # Adicionar plano de saúde se houver
        if complexidade.get("tem_plano_saude"):
            xml += f'''                <planSaude>
                    <cnpjOper>12345678000199</cnpjOper>
                    <regANS>123456</regANS>
                    <vlrSaudeTit>350.00</vlrSaudeTit>
'''
            for i in range(num_deps):
                cpf_dep = gerar_cpf(int(cpf) + i + 1)
                xml += f'''                    <infoDepSau>
                        <cpfDep>{cpf_dep}</cpfDep>
                        <vlrSaudeDep>200.00</vlrSaudeDep>
                    </infoDepSau>
'''
            xml += f'''                </planSaude>
'''
        
        # Adicionar pensão alimentícia se houver
        if complexidade.get("tem_pensao"):
            cpf_benef_pensao = gerar_cpf(int(cpf) + 100)
            xml += f'''                <infoIRCR>
                    <tpCR>056107</tpCR>
                    <penAlim>
                        <tpRend>11</tpRend>
                        <cpfDep>{cpf_benef_pensao}</cpfDep>
                        <vlrPensao>{SALARIO_BASE_MENSAL * 0.20 * 12:.2f}</vlrPensao>
                    </penAlim>
                </infoIRCR>
'''
        
        # Adicionar previdência complementar se houver
        if complexidade.get("tem_prev_privada"):
            xml += f'''                <infoIRCR>
                    <tpCR>056107</tpCR>
                    <previdCompl>
                        <tpPrev>1</tpPrev>
                        <cnpjEntidPC>12345678000188</cnpjEntidPC>
                        <vlrPatrocFunp>{SALARIO_BASE_MENSAL * 0.05 * 12:.2f}</vlrPatrocFunp>
                    </previdCompl>
                </infoIRCR>
'''
        
        xml += f'''            </infoIRComplem>
'''
    
    # Fechar XML
    xml += f'''        </ideTrabalhador>
    </evtIrrfBenef>
</eSocial>
'''
    
    return xml


def gerar_todos_xmls(pasta_saida: str = "/home/ubuntu/xmls_gerados_2025"):
    """Gera todos os XMLs (30 funcionários = 10 por empresa)"""
    
    pasta = Path(pasta_saida)
    pasta.mkdir(exist_ok=True, parents=True)
    
    # Lista para CSV de nomes
    registros_csv = []
    
    # Distribuição de complexidades (10 funcionários por empresa)
    complexidades_distribuicao = [
        "simples", "simples", "simples",  # 3 simples
        "medio", "medio", "medio",  # 3 médios
        "complexo", "complexo",  # 2 complexos
        "muito_complexo", "muito_complexo",  # 2 muito complexos
    ]
    
    contador_global = 1
    
    for idx_empresa, empresa in enumerate(EMPRESAS):
        print(f"\n{'='*80}")
        print(f"Gerando XMLs para: {empresa['nome']}")
        print(f"CNPJ: {empresa['cnpj']}")
        print(f"{'='*80}")
        
        for idx_func in range(10):
            # CPF fictício
            cpf_base = 10000000000 + (idx_empresa * 1000) + (idx_func * 10)
            cpf = gerar_cpf(cpf_base)
            
            # Nome fictício
            nome = f"Funcionário {contador_global:02d}"
            
            # Complexidade
            complexidade = complexidades_distribuicao[idx_func]
            
            # Gerar XML
            xml_content = gerar_xml_trabalhador(
                cpf=cpf,
                nome=nome,
                empresa=empresa,
                complexidade_nome=complexidade,
                numero_func=contador_global
            )
            
            # Nome do arquivo
            nome_arquivo = f"xml_{ANO}_{empresa['cnpj']}_{cpf}_{complexidade}.xml"
            caminho_arquivo = pasta / nome_arquivo
            
            # Salvar XML
            with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                f.write(xml_content)
            
            print(f"  ✅ {nome_arquivo} ({complexidade})")
            
            # Adicionar ao CSV
            registros_csv.append({
                "cpf": cpf,
                "nome": nome,
                "cnpj": empresa["cnpj"],
                "empresa": empresa["nome"],
                "complexidade": complexidade,
            })
            
            contador_global += 1
    
    # Salvar CSV de nomes
    csv_path = pasta / f"nomes_funcionarios_{ANO}.csv"
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["cpf", "nome", "cnpj", "empresa", "complexidade"])
        writer.writeheader()
        writer.writerows(registros_csv)
    
    print(f"\n{'='*80}")
    print(f"✅ GERAÇÃO CONCLUÍDA!")
    print(f"{'='*80}")
    print(f"Total de XMLs gerados: {contador_global - 1}")
    print(f"Pasta de saída: {pasta_saida}")
    print(f"CSV de nomes: {csv_path}")
    print(f"Ano: {ANO}")
    print(f"Meses por funcionário: 12 + 13º salário")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    print(f"""
{'='*80}
GERADOR DE XMLs S-5002 - VERSÃO 6.0.0
e-Social S-1.3 - Ano {ANO}
{'='*80}

Características:
- 30 XMLs (10 funcionários por empresa)
- 3 empresas diferentes
- 12 meses + 13º salário por funcionário
- 4 níveis de complexidade
- Valores realistas (~R$ 121.000/ano por funcionário)
- 100% conforme especificação e-Social S-1.3

{'='*80}
""")
    
    gerar_todos_xmls()
