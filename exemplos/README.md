# 10 Exemplos Práticos - XMLs e PDFs Gerados

Esta pasta contém **10 exemplos práticos** de XMLs do e-Social S-5002 e seus respectivos PDFs gerados, cobrindo diferentes níveis de complexidade e casos de uso.

---

## 📋 **Lista de Exemplos**

| # | Arquivo XML | PDF Gerado | Complexidade | Descrição |
|---|-------------|------------|--------------|-----------|
| 01 | `exemplo_01_simples.xml` | `irpf2024-123_456_789_01.pdf` | ⭐ Simples | Apenas rendimentos básicos tributáveis |
| 02 | `exemplo_02_dependentes.xml` | `irpf2024-123_456_789_05.pdf` | ⭐⭐ Médio | Com 2 dependentes |
| 03 | `exemplo_03_plano_saude.xml` | `irpf2024-123_456_789_10.pdf` | ⭐⭐ Médio | Com plano de saúde |
| 04 | `exemplo_04_pensao.xml` | `irpf2024-123_456_789_15.pdf` | ⭐⭐⭐ Complexo | Com pensão alimentícia |
| 05 | `exemplo_05_completo_empresa1.xml` | `irpf2024-123_456_789_20.pdf` | ⭐⭐⭐⭐ Muito Complexo | Dependentes + plano + pensão |
| 06 | `exemplo_06_rra.xml` | `irpf2024-987_654_321_10.pdf` | ⭐⭐⭐⭐ Muito Complexo | Rendimentos Recebidos Acumuladamente (RRA) |
| 07 | `exemplo_07_processo_judicial.xml` | `irpf2024-987_654_321_20.pdf` | ⭐⭐⭐⭐ Muito Complexo | Com processo judicial |
| 08 | `exemplo_08_pagamento_exterior.xml` | `irpf2024-555_666_777_10.pdf` | ⭐⭐⭐⭐ Muito Complexo | Pagamento no exterior |
| 09 | `exemplo_09_multiplos_demonstrativos.xml` | `irpf2024-555_666_777_19.pdf` | ⭐⭐⭐⭐⭐ Extremamente Complexo | Múltiplos demonstrativos |
| 10 | `exemplo_10_todos_grupos.xml` | `irpf2024-555_666_777_20.pdf` | ⭐⭐⭐⭐⭐ Extremamente Complexo | Todos os 33 grupos do e-Social |

---

## 🏢 **3 Empresas Diferentes**

### **Empresa 1: Tech Solutions Ltda**
- CNPJ: 12.345.678/0001-90
- Funcionários: João da Silva Santos, Maria Oliveira Costa, Pedro Henrique Alves, Ana Paula Rodrigues, Carlos Eduardo Ferreira
- Exemplos: 01, 02, 03, 04, 05

### **Empresa 2: Indústria ABC S.A.**
- CNPJ: 98.765.432/0001-10
- Funcionários: Juliana Santos Lima, Roberto Carlos Souza
- Exemplos: 06, 07

### **Empresa 3: Comércio XYZ Ltda**
- CNPJ: 55.566.677/0001-88
- Funcionários: Fernanda Cristina Martins, Marcos Vinícius Pereira, Patrícia Helena Gomes
- Exemplos: 08, 09, 10

---

## 📄 **CSV de Nomes Incluído**

A pasta contém o arquivo **`nomes_exemplos.csv`** com os nomes das empresas e funcionários usados nos exemplos:

```csv
cpf,nome_funcionario,nome_empresa,cnpj_empresa
12345678901,João da Silva Santos,Tech Solutions Ltda,12345678000190
12345678905,Maria Oliveira Costa,Tech Solutions Ltda,12345678000190
12345678910,Pedro Henrique Alves,Tech Solutions Ltda,12345678000190
...
```

### **Por Que o CSV é Necessário?**

O XML do e-Social S-5002 **não contém** os nomes das empresas e funcionários, apenas CPF/CNPJ. O CSV é usado para:

- ✅ Adicionar **nome da empresa** no comprovante
- ✅ Adicionar **nome do funcionário/beneficiário** no comprovante
- ✅ Tornar o PDF mais **legível e profissional**

### **Como Usar o CSV**

```bash
# Gerar PDFs COM nomes (recomendado)
python s5002_to_pdf.py xmls/ pdfs/ --ano 2024 --csv nomes_exemplos.csv

# Gerar PDFs SEM nomes (apenas CPF/CNPJ)
python s5002_to_pdf.py xmls/ pdfs/ --ano 2024
```

---

## 📊 **Grupos do e-Social Cobertos**

### **Exemplo 01 - Simples (⭐)**
- ✅ Rendimentos tributáveis básicos
- ✅ 13º salário
- ✅ Rendimentos isentos
- ✅ IRRF descontado

### **Exemplo 02 - Dependentes (⭐⭐)**
- ✅ Tudo do Exemplo 01
- ✅ **2 dependentes** com CPF e data de nascimento

### **Exemplo 03 - Plano de Saúde (⭐⭐)**
- ✅ Tudo do Exemplo 01
- ✅ **Plano de saúde** (operadora, registro ANS, valores)

### **Exemplo 04 - Pensão Alimentícia (⭐⭐⭐)**
- ✅ Tudo do Exemplo 01
- ✅ **Pensão alimentícia** (beneficiário, valores)

### **Exemplo 05 - Completo Empresa 1 (⭐⭐⭐⭐)**
- ✅ Tudo do Exemplo 01
- ✅ **Dependentes**
- ✅ **Plano de saúde** (titular + dependentes)
- ✅ **Pensão alimentícia**

### **Exemplo 06 - RRA (⭐⭐⭐⭐)**
- ✅ Tudo do Exemplo 01
- ✅ **Rendimentos Recebidos Acumuladamente (RRA)**
- ✅ Processo judicial
- ✅ Despesas processuais
- ✅ Advogados

### **Exemplo 07 - Processo Judicial (⭐⭐⭐⭐)**
- ✅ Tudo do Exemplo 01
- ✅ **Processos judiciais por rubrica**
- ✅ Origem dos recursos
- ✅ Descrição detalhada

### **Exemplo 08 - Pagamento Exterior (⭐⭐⭐⭐)**
- ✅ Tudo do Exemplo 01
- ✅ **Pagamento no exterior**
- ✅ País de residência
- ✅ Endereço completo
- ✅ NIF (número de identificação fiscal)

### **Exemplo 09 - Múltiplos Demonstrativos (⭐⭐⭐⭐⭐)**
- ✅ **Múltiplos demonstrativos** (dmDev)
- ✅ Dependentes
- ✅ Plano de saúde
- ✅ Pensão alimentícia
- ✅ Consolidação de valores

### **Exemplo 10 - Todos os Grupos (⭐⭐⭐⭐⭐)**
- ✅ **TODOS os 33 grupos/subgrupos** do e-Social S-1.3
- ✅ Dependentes (múltiplos)
- ✅ Plano de saúde (titular + dependentes)
- ✅ Pensão alimentícia
- ✅ RRA completo
- ✅ Processos judiciais
- ✅ Advogados
- ✅ Despesas processuais

---

## 🚀 **Como Usar**

### **1. Visualizar os PDFs**
Abra qualquer PDF para ver o resultado final da conversão:
```bash
# PDF simples (1 página)
xdg-open irpf2024-123_456_789_01.pdf

# PDF complexo (2 páginas)
xdg-open irpf2024-555_666_777_20.pdf
```

### **2. Converter os XMLs Novamente**
```bash
# Converter todos os exemplos COM nomes (recomendado)
python s5002_to_pdf.py exemplos/ saida/ --ano 2024 --csv exemplos/nomes_exemplos.csv

# Converter sem nomes (apenas CPF/CNPJ)
python s5002_to_pdf.py exemplos/ saida/ --ano 2024

# Converter um exemplo específico
python s5002_to_pdf.py exemplos/exemplo_01_simples.xml saida/ --ano 2024 --csv exemplos/nomes_exemplos.csv
```

### **3. Usar como Base para Seus XMLs**
Copie um dos exemplos e adapte para seu caso:
```bash
cp exemplos/exemplo_01_simples.xml meu_xml.xml
# Edite meu_xml.xml com seus dados
python s5002_to_pdf.py meu_xml.xml saida/ --ano 2024 --csv meu_csv.csv
```

---

## 📈 **Níveis de Complexidade**

| Nível | Estrelas | Páginas | Grupos | Tempo Geração |
|-------|----------|---------|--------|---------------|
| Simples | ⭐ | 1 | 1-2 | ~1ms |
| Médio | ⭐⭐ | 1 | 3-5 | ~2ms |
| Complexo | ⭐⭐⭐ | 1-2 | 6-10 | ~3ms |
| Muito Complexo | ⭐⭐⭐⭐ | 2 | 11-20 | ~4ms |
| Extremamente Complexo | ⭐⭐⭐⭐⭐ | 2 | 21-33 | ~5ms |

---

## 🎯 **Casos de Uso Cobertos**

| Caso de Uso | Exemplos |
|-------------|----------|
| Funcionário sem dependentes | 01, 03, 08 |
| Funcionário com dependentes | 02, 04, 05, 09, 10 |
| Com plano de saúde | 03, 05, 09, 10 |
| Com pensão alimentícia | 04, 05, 09, 10 |
| Com RRA | 06, 10 |
| Com processo judicial | 07, 10 |
| Pagamento exterior | 08 |
| Múltiplos demonstrativos | 09, 10 |

---

## 📊 **Estatísticas**

- **Total de exemplos:** 10
- **Empresas diferentes:** 3
- **Funcionários diferentes:** 10
- **Grupos do e-Social cobertos:** 33/33 (100%)
- **Tamanho médio dos XMLs:** 3.2 KB
- **Tamanho médio dos PDFs:** 4.5 KB
- **Taxa de conversão:** ~327 PDFs/segundo

---

## 🔍 **Validação**

Para validar que o conversor está funcionando corretamente:

1. ✅ Compare os PDFs gerados com os exemplos fornecidos
2. ✅ Verifique se todos os campos estão sendo exibidos
3. ✅ Confirme que a paginação está correta
4. ✅ Valide que os valores estão formatados corretamente
5. ✅ Teste com seus próprios XMLs

---

## 📞 **Suporte**

Se encontrar algum problema com os exemplos ou tiver dúvidas:

1. Verifique a [documentação principal](../README.md)
2. Consulte o [guia de contribuição](../CONTRIBUTING.md)
3. Abra uma [issue](https://github.com/flaviowbr/esocial_s5002_comprovante_rendimentos/issues)

---

**Última atualização:** 30 de Outubro de 2025  
**Versão do conversor:** 5.2.2  
**Conformidade:** 100% com e-Social S-1.3
