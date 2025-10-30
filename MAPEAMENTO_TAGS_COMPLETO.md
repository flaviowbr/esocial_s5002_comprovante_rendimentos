# Mapeamento Completo de Tags e-Social S-5002

**Versão:** 6.1.0  
**Data:** 30 de Outubro de 2025  
**Especificação:** e-Social S-1.3  
**Evento:** S-5002 - Imposto de Renda Retido na Fonte

---

## 📋 Sumário

Este documento apresenta o **mapeamento completo** entre as tags do e-Social S-1.3, a estrutura XML, os campos do CSV complementar e a saída em PDF, além de mostrar como o código implementa cada elemento.

**Objetivo:** Facilitar o entendimento do fluxo de dados desde a entrada (XML + CSV) até a saída (PDF), permitindo que desenvolvedores e usuários compreendam exatamente como cada informação é processada.

---

## 🔄 Fluxo de Dados

```
┌─────────────────┐
│   e-Social      │
│  Especificação  │
│     S-1.3       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌─────────────────┐
│   XML S-5002    │────▶│  CSV (Nomes)    │
│  (Dados Fiscais)│     │ (Complementar)  │
└────────┬────────┘     └────────┬────────┘
         │                       │
         └───────────┬───────────┘
                     ▼
         ┌───────────────────────┐
         │   Parser Python       │
         │  (s5002_to_pdf.py)    │
         └───────────┬───────────┘
                     ▼
         ┌───────────────────────┐
         │   PDF Generator       │
         │    (ReportLab)        │
         └───────────┬───────────┘
                     ▼
         ┌───────────────────────┐
         │  Comprovante PDF      │
         │ (Receita Federal)     │
         └───────────────────────┘
```

---

## 📊 Origem dos Dados

### **Dados que VÊM do XML:**

Todos os dados fiscais e a maioria das informações pessoais vêm diretamente do XML S-5002:

- ✅ **Valores financeiros** (rendimentos, deduções, impostos)
- ✅ **Dependentes** (CPF, nome, data de nascimento)
- ✅ **Planos de saúde** (operadora, valores, dependentes)
- ✅ **Previdência privada** (CNPJ, valores)
- ✅ **Pensão alimentícia** (CPF, valores)
- ✅ **Advogados** (CPF, nome, valores)
- ✅ **Processos judiciais** (número, vara, valores)

### **Dados que VÊM do CSV:**

Apenas **2 campos** não existem no XML S-5002 e precisam vir do CSV:

- ❌ **Nome da Empresa** (só CNPJ existe no XML)
- ❌ **Nome do Funcionário/Beneficiário** (só CPF existe no XML)

**Formato do CSV:**
```csv
cpf,nome_funcionario,cnpj,nome_empresa
12345678901,João da Silva,12345678000190,Tech Solutions Ltda
```

---

## 🏗️ Estrutura Hierárquica do S-5002

### **Nível 1: Raiz**
```xml
<eSocial>
  <evtIrrfBenef>
    <!-- Conteúdo -->
  </evtIrrfBenef>
</eSocial>
```

### **Nível 2: Identificação do Evento**
```xml
<ideEvento>
  <indRetif>1</indRetif>
  <nrRecibo>1.2.0000000000000000001</nrRecibo>
  <perApur>2025-12</perApur>
  <tpAmb>1</tpAmb>
  <procEmi>1</procEmi>
  <verProc>1.0</verProc>
</ideEvento>
```

### **Nível 3: Empregador**
```xml
<ideEmpregador>
  <tpInsc>1</tpInsc>
  <nrInsc>12345678000190</nrInsc>
</ideEmpregador>
```

### **Nível 4: Trabalhador**
```xml
<ideTrabalhador>
  <cpfBenef>12345678901</cpfBenef>
  <!-- Demonstrativos, dependentes, etc. -->
</ideTrabalhador>
```

---

## 📖 Mapeamento Detalhado por Grupo

### **GRUPO 1: Identificação do Evento (ideEvento)**

| Tag e-Social | Tag XML | Tipo | Obrig. | Origem | Campo PDF | Código |
|--------------|---------|------|--------|--------|-----------|--------|
| `indRetif` | `ideEvento/indRetif` | String | Sim | XML | - | `ide_evento.find('esocial:indRetif')` |
| `nrRecibo` | `ideEvento/nrRecibo` | String | Cond. | XML | - | `ide_evento.find('esocial:nrRecibo')` |
| `perApur` | `ideEvento/perApur` | String | Sim | XML | Cabeçalho "Ano-Calendário" | `ide_evento.find('esocial:perApur')` |
| `tpAmb` | `ideEvento/tpAmb` | Int | Sim | XML | - | `ide_evento.find('esocial:tpAmb')` |
| `procEmi` | `ideEvento/procEmi` | Int | Sim | XML | - | `ide_evento.find('esocial:procEmi')` |
| `verProc` | `ideEvento/verProc` | String | Sim | XML | - | `ide_evento.find('esocial:verProc')` |

**Exemplo de Saída no PDF:**
```
COMPROVANTE DE RENDIMENTOS PAGOS E DE RETENÇÃO
DE IMPOSTO DE RENDA NA FONTE
Ano-Calendário: 2025
```

---

### **GRUPO 2: Identificação do Empregador (ideEmpregador)**

| Tag e-Social | Tag XML | Tipo | Obrig. | Origem | Campo PDF | Código |
|--------------|---------|------|--------|--------|-----------|--------|
| `tpInsc` | `ideEmpregador/tpInsc` | Int | Sim | XML | - | `ide_empregador.find('esocial:tpInsc')` |
| `nrInsc` | `ideEmpregador/nrInsc` | String | Sim | XML | "CNPJ: XX.XXX.XXX/XXXX-XX" | `ide_empregador.find('esocial:nrInsc')` |
| - | - | - | - | **CSV** | "NOME EMPRESARIAL: [Nome]" | `csv_data[cnpj]['nome_empresa']` |

**Exemplo de Saída no PDF:**
```
1. FONTE PAGADORA
NOME EMPRESARIAL/NOME: Tech Solutions Ltda
CNPJ: 12.345.678/0001-90
```

**Observação:** O nome da empresa **NÃO existe no XML**, vem do CSV.

---

### **GRUPO 3: Identificação do Trabalhador (ideTrabalhador)**

| Tag e-Social | Tag XML | Tipo | Obrig. | Origem | Campo PDF | Código |
|--------------|---------|------|--------|--------|-----------|--------|
| `cpfBenef` | `ideTrabalhador/cpfBenef` | String | Sim | XML | "CPF: XXX.XXX.XXX-XX" | `ide_trab.find('esocial:cpfBenef')` |
| - | - | - | - | **CSV** | "NOME COMPLETO: [Nome]" | `csv_data[cpf]['nome_funcionario']` |

**Exemplo de Saída no PDF:**
```
2. PESSOA FÍSICA BENEFICIÁRIA
CPF: 123.456.789-01
NOME COMPLETO: João da Silva Santos
```

**Observação:** O nome do beneficiário **NÃO existe no XML**, vem do CSV.

---

### **GRUPO 4: Demonstrativos de Valores (dmDev)**

| Tag e-Social | Tag XML | Tipo | Obrig. | Origem | Campo PDF | Código |
|--------------|---------|------|--------|--------|-----------|--------|
| `ideDmDev` | `dmDev/ideDmDev` | String | Sim | XML | - | `dm_dev.find('esocial:ideDmDev')` |
| `perRef` | `dmDev/infoPerRef/perRef` | String | Cond. | XML | - | `info_per_ref.find('esocial:perRef')` |
| `tpInfoIR` | `dmDev/infoIR/tpInfoIR` | Int | Sim | XML | Código do tipo | `info_ir.find('esocial:tpInfoIR')` |
| `valor` | `dmDev/infoIR/valor` | Decimal | Sim | XML | "R$ X.XXX,XX" | `info_ir.find('esocial:valor')` |

**Exemplo de Saída no PDF:**
```
3. RENDIMENTOS TRIBUTÁVEIS
Rendimentos do trabalho assalariado............R$ 120.000,00
```

**Mapeamento de Códigos tpInfoIR:**

| Código | Descrição | Seção PDF |
|--------|-----------|-----------|
| 11 | Rendimentos do trabalho assalariado | 3. Rendimentos Tributáveis |
| 12 | Rendimentos de férias | 3. Rendimentos Tributáveis |
| 13 | 13º salário | 3. Rendimentos Tributáveis |
| 31 | Contribuição previdenciária oficial | 4. Deduções |
| 41 | Imposto de renda retido | 7. Imposto Retido |

---

### **GRUPO 5: Dependentes (dependente)**

| Tag e-Social | Tag XML | Tipo | Obrig. | Origem | Campo PDF | Código |
|--------------|---------|------|--------|--------|-----------|--------|
| `tpDep` | `dependente/tpDep` | String | Sim | XML | Código do tipo | `dep.find('esocial:tpDep')` |
| `cpfDep` | `dependente/cpfDep` | String | Sim | XML | "CPF: XXX.XXX.XXX-XX" | `dep.find('esocial:cpfDep')` |
| `nmDep` | `dependente/nmDep` | String | Sim | XML | Nome do dependente | `dep.find('esocial:nmDep')` |
| `dtNascto` | `dependente/dtNascto` | Date | Sim | XML | "Nascimento: DD/MM/AAAA" | `dep.find('esocial:dtNascto')` |
| `descrDep` | `dependente/descrDep` | String | Cond. | XML | - | `dep.find('esocial:descrDep')` |

**Exemplo de Saída no PDF:**
```
5. RELAÇÃO DE DEPENDENTES
1. Maria da Silva Santos
   CPF: 987.654.321-00
   Nascimento: 15/03/2010
   Tipo: Filho(a)
```

**Observação:** O nome do dependente **VEM do XML** (campo `nmDep`).

---

### **GRUPO 6: Planos de Saúde (planSaude)**

| Tag e-Social | Tag XML | Tipo | Obrig. | Origem | Campo PDF | Código |
|--------------|---------|------|--------|--------|-----------|--------|
| `cnpjOper` | `planSaude/cnpjOper` | String | Sim | XML | "CNPJ: XX.XXX.XXX/XXXX-XX" | `plano.find('esocial:cnpjOper')` |
| `nmRazao` | `planSaude/nmRazao` | String | Sim | XML | "Operadora: [Nome]" | `plano.find('esocial:nmRazao')` |
| `regANS` | `planSaude/regANS` | String | Sim | XML | "Registro ANS: XXXXXX" | `plano.find('esocial:regANS')` |
| `vlrSaudeTit` | `planSaude/vlrSaudeTit` | Decimal | Sim | XML | "R$ XXX,XX" | `plano.find('esocial:vlrSaudeTit')` |

**Subgrupo: Dependentes do Plano (infoDepSau)**

| Tag e-Social | Tag XML | Tipo | Obrig. | Origem | Campo PDF | Código |
|--------------|---------|------|--------|--------|-----------|--------|
| `cpfDep` | `infoDepSau/cpfDep` | String | Sim | XML | "CPF: XXX.XXX.XXX-XX" | `info_dep.find('esocial:cpfDep')` |
| `nmDep` | `infoDepSau/nmDep` | String | Sim | XML | Nome do dependente | `info_dep.find('esocial:nmDep')` |
| `vlrSaudeDep` | `infoDepSau/vlrSaudeDep` | Decimal | Sim | XML | "R$ XXX,XX" | `info_dep.find('esocial:vlrSaudeDep')` |

**Exemplo de Saída no PDF:**
```
6. PLANOS DE SAÚDE COLETIVOS EMPRESARIAIS
1. Operadora: Unimed São Paulo
   CNPJ: 12.345.678/0001-90
   Registro ANS: 123456
   
   Valor Pago pelo Titular........................R$ 500,00
   
   Dependentes:
   1. Maria da Silva Santos (CPF: 987.654.321-00)...R$ 300,00
```

---

### **GRUPO 7: Previdência Complementar (prevCompl)**

| Tag e-Social | Tag XML | Tipo | Obrig. | Origem | Campo PDF | Código |
|--------------|---------|------|--------|--------|-----------|--------|
| `cnpjEntidPC` | `prevCompl/cnpjEntidPC` | String | Sim | XML | "CNPJ: XX.XXX.XXX/XXXX-XX" | `prev.find('esocial:cnpjEntidPC')` |
| `vlrDedPC` | `prevCompl/vlrDedPC` | Decimal | Sim | XML | "R$ XXX,XX" | `prev.find('esocial:vlrDedPC')` |
| `vlrPatrocFunp` | `prevCompl/vlrPatrocFunp` | Decimal | Sim | XML | "R$ XXX,XX" | `prev.find('esocial:vlrPatrocFunp')` |

**Exemplo de Saída no PDF:**
```
7. PREVIDÊNCIA COMPLEMENTAR
CNPJ da Entidade: 12.345.678/0001-90
Contribuição do Participante.....................R$ 1.000,00
Contribuição Patronal Dedutível...................R$ 1.000,00
```

---

### **GRUPO 8: Pensão Alimentícia (penAlim)**

| Tag e-Social | Tag XML | Tipo | Obrig. | Origem | Campo PDF | Código |
|--------------|---------|------|--------|--------|-----------|--------|
| `cpfDep` | `penAlim/cpfDep` | String | Sim | XML | "CPF: XXX.XXX.XXX-XX" | `pensao.find('esocial:cpfDep')` |
| `vlrPensao` | `penAlim/vlrPensao` | Decimal | Sim | XML | "R$ XXX,XX" | `pensao.find('esocial:vlrPensao')` |

**Exemplo de Saída no PDF:**
```
8. PENSÃO ALIMENTÍCIA
CPF do Beneficiário: 987.654.321-00
Valor Pago........................................R$ 2.000,00
```

---

### **GRUPO 9: Processos Judiciais (infoRRA)**

| Tag e-Social | Tag XML | Tipo | Obrig. | Origem | Campo PDF | Código |
|--------------|---------|------|--------|--------|-----------|--------|
| `nrProc` | `infoRRA/ideProc/nrProc` | String | Sim | XML | "Processo: XXXXXXX-XX.XXXX.X.XX.XXXX" | `ide_proc.find('esocial:nrProc')` |
| `codSusp` | `infoRRA/ideProc/codSusp` | String | Cond. | XML | - | `ide_proc.find('esocial:codSusp')` |
| `descRRA` | `infoRRA/descRRA` | String | Sim | XML | Descrição | `info_rra.find('esocial:descRRA')` |
| `qtdMesesRRA` | `infoRRA/qtdMesesRRA` | Int | Sim | XML | "Meses: XX" | `info_rra.find('esocial:qtdMesesRRA')` |

**Subgrupo: Despesas Processuais (despProcJud)**

| Tag e-Social | Tag XML | Tipo | Obrig. | Origem | Campo PDF | Código |
|--------------|---------|------|--------|--------|-----------|--------|
| `vlrDespCustas` | `despProcJud/vlrDespCustas` | Decimal | Sim | XML | "Custas Judiciais: R$ XXX,XX" | `desp_proc.find('esocial:vlrDespCustas')` |
| `vlrDespAdvogados` | `despProcJud/vlrDespAdvogados` | Decimal | Sim | XML | "Honorários: R$ XXX,XX" | `desp_proc.find('esocial:vlrDespAdvogados')` |

**Subgrupo: Advogados (ideAdv)**

| Tag e-Social | Tag XML | Tipo | Obrig. | Origem | Campo PDF | Código |
|--------------|---------|------|--------|--------|-----------|--------|
| `tpInsc` | `ideAdv/tpInsc` | Int | Sim | XML | - | `ide_adv.find('esocial:tpInsc')` |
| `nrInsc` | `ideAdv/nrInsc` | String | Sim | XML | "CPF: XXX.XXX.XXX-XX" | `ide_adv.find('esocial:nrInsc')` |
| `nmAdv` | `ideAdv/nmAdv` | String | Sim | XML | Nome do advogado | `ide_adv.find('esocial:nmAdv')` |
| `vlrAdv` | `ideAdv/vlrAdv` | Decimal | Sim | XML | "R$ XXX,XX" | `ide_adv.find('esocial:vlrAdv')` |

**Exemplo de Saída no PDF:**
```
9. RENDIMENTOS RECEBIDOS ACUMULADAMENTE (RRA)
Processo: 0001234-56.2024.5.02.0001
Descrição: Diferenças salariais
Meses: 24

Despesas com Processo Judicial:
Custas Judiciais.................................R$ 500,00
Honorários Advocatícios..........................R$ 2.000,00

Advogados:
1. Dr. José Santos (CPF: 111.222.333-44).........R$ 2.000,00
```

**Observação:** O nome do advogado **VEM do XML** (campo `nmAdv`).

---

### **GRUPO 10: Pagamentos no Exterior (pagExterior)**

| Tag e-Social | Tag XML | Tipo | Obrig. | Origem | Campo PDF | Código |
|--------------|---------|------|--------|--------|-----------|--------|
| `paisResid` | `pagExterior/paisResid` | String | Sim | XML | Código do país | `pag_ext.find('esocial:paisResid')` |
| `tpRendimento` | `pagExterior/tpRendimento` | Int | Sim | XML | Tipo | `pag_ext.find('esocial:tpRendimento')` |
| `vlrPago` | `pagExterior/vlrPago` | Decimal | Sim | XML | "R$ XXX,XX" | `pag_ext.find('esocial:vlrPago')` |

**Subgrupo: Endereço Exterior (endExt)**

| Tag e-Social | Tag XML | Tipo | Obrig. | Origem | Campo PDF | Código |
|--------------|---------|------|--------|--------|-----------|--------|
| `dscLograd` | `endExt/dscLograd` | String | Sim | XML | Endereço | `end_ext.find('esocial:dscLograd')` |
| `nrLograd` | `endExt/nrLograd` | String | Cond. | XML | Número | `end_ext.find('esocial:nrLograd')` |
| `cidade` | `endExt/cidade` | String | Sim | XML | Cidade | `end_ext.find('esocial:cidade')` |
| `codPostal` | `endExt/codPostal` | String | Cond. | XML | CEP | `end_ext.find('esocial:codPostal')` |

---

## 📋 Tabela de Referência Rápida

### **Todas as Tags em Ordem Alfabética**

| Tag e-Social | Tipo | Obrig. | Origem | Seção PDF |
|--------------|------|--------|--------|-----------|
| `cidade` | String | Sim | XML | Endereço Exterior |
| `cnpjEntidPC` | String | Sim | XML | Previdência Complementar |
| `cnpjOper` | String | Sim | XML | Planos de Saúde |
| `codMunic` | String | Cond. | XML | Processo Judicial |
| `codPostal` | String | Cond. | XML | Endereço Exterior |
| `codSusp` | String | Cond. | XML | Processo Judicial |
| `cpfBenef` | String | Sim | XML | Pessoa Física Beneficiária |
| `cpfDep` | String | Sim | XML | Dependentes / Pensão |
| `CRDia` | String | Sim | XML | Totalizador Diário |
| `CRMen` | String | Sim | XML | Totalizador Mensal |
| `descRRA` | String | Sim | XML | RRA |
| `descrDep` | String | Cond. | XML | Dependentes |
| `dscLograd` | String | Sim | XML | Endereço Exterior |
| `dtNascto` | Date | Sim | XML | Dependentes |
| `frmTribut` | String | Sim | XML | Totalizador Diário |
| `ideDmDev` | String | Sim | XML | Demonstrativo |
| `idVara` | String | Cond. | XML | Processo Judicial |
| `indRetif` | String | Sim | XML | Evento |
| `nmAdv` | String | Sim | XML | Advogado |
| `nmDep` | String | Sim | XML | Dependente |
| `nmRazao` | String | Sim | XML | Operadora de Saúde |
| `nome_empresa` | String | - | **CSV** | Fonte Pagadora |
| `nome_funcionario` | String | - | **CSV** | Beneficiário |
| `nrInsc` | String | Sim | XML | Empregador / Advogado |
| `nrLograd` | String | Cond. | XML | Endereço Exterior |
| `nrProc` | String | Sim | XML | Processo Judicial |
| `nrRecibo` | String | Cond. | XML | Evento |
| `paisResid` | String | Sim | XML | Pagamento Exterior |
| `paisResidExt` | String | Cond. | XML | Totalizador Diário |
| `perApurDia` | String | Sim | XML | Totalizador Diário |
| `perApur` | String | Sim | XML | Evento |
| `perRef` | String | Cond. | XML | Demonstrativo |
| `procEmi` | Int | Sim | XML | Evento |
| `qtdMesesRRA` | Int | Sim | XML | RRA |
| `regANS` | String | Sim | XML | Plano de Saúde |
| `tpAmb` | Int | Sim | XML | Evento |
| `tpCR` | String | Sim | XML | Código de Receita |
| `tpDep` | String | Sim | XML | Dependente |
| `tpInfoIR` | Int | Sim | XML | Informação de IR |
| `tpInsc` | Int | Sim | XML | Empregador / Advogado |
| `tpRendimento` | Int | Sim | XML | Pagamento Exterior |
| `ufVara` | String | Cond. | XML | Processo Judicial |
| `valor` | Decimal | Sim | XML | Informação de IR |
| `verProc` | String | Sim | XML | Evento |
| `vlrAdv` | Decimal | Sim | XML | Advogado |
| `vlrCRDia` | Decimal | Sim | XML | Totalizador Diário |
| `vlrCRMen` | Decimal | Sim | XML | Totalizador Mensal |
| `vlrCRMen13` | Decimal | Sim | XML | Totalizador Mensal 13º |
| `vlrDedPC` | Decimal | Sim | XML | Previdência Complementar |
| `vlrDespAdvogados` | Decimal | Sim | XML | Despesa Processual |
| `vlrDespCustas` | Decimal | Sim | XML | Despesa Processual |
| `vlrPago` | Decimal | Sim | XML | Pagamento Exterior |
| `vlrPatrocFunp` | Decimal | Sim | XML | Previdência Complementar |
| `vlrPensao` | Decimal | Sim | XML | Pensão Alimentícia |
| `vlrRendTrib` | Decimal | Sim | XML | Totalizador |
| `vlrRendTrib13` | Decimal | Sim | XML | Totalizador 13º |
| `vlrSaudeDep` | Decimal | Sim | XML | Plano de Saúde Dependente |
| `vlrSaudeTit` | Decimal | Sim | XML | Plano de Saúde Titular |

**Legenda:**
- **Obrig.:** Obrigatório (Sim), Condicional (Cond.)
- **Origem:** XML ou CSV

---

## 🔍 Casos Especiais

### **Caso 1: Nomes que NÃO existem no XML**

**Problema:** O XML S-5002 contém apenas CPF e CNPJ, sem nomes.

**Solução:** CSV complementar

**Tags afetadas:**
- `nome_empresa` (não existe no e-Social)
- `nome_funcionario` (não existe no e-Social)

**Implementação:**
```python
# Ler CSV
csv_data = {}
with open(csv_file, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        cpf = row['cpf']
        cnpj = row['cnpj']
        csv_data[cpf] = {
            'nome_funcionario': row['nome_funcionario'],
            'nome_empresa': row['nome_empresa']
        }

# Usar no PDF
nome_empresa = csv_data.get(cnpj, {}).get('nome_empresa', '')
nome_funcionario = csv_data.get(cpf, {}).get('nome_funcionario', '')
```

---

### **Caso 2: Tags com Aliases Incorretos**

**Problema:** Versões antigas usavam aliases não oficiais.

**Solução:** Sistema de fallback (v6.1.0)

**Tags afetadas:**

| Alias Antigo | Tag Oficial | Status |
|--------------|-------------|--------|
| `vlrCustas` | `vlrDespCustas` | ✅ Corrigido na v6.1.0 |
| `vlrAdvogados` | `vlrDespAdvogados` | ✅ Corrigido na v6.1.0 |
| `vrCR` | `vlrCR` | ✅ Corrigido na v6.1.0 |
| `vlrIRRF` | `vlrCRDia` / `vlrCRMen` | ✅ Corrigido na v6.1.0 |
| `vlrIRRF13` | `vlrCRMen13` | ✅ Corrigido na v6.1.0 |

**Implementação (v6.1.0):**
```python
# Tentar tag oficial primeiro, depois fallback para alias
vlr_custas = desp_proc_elem.find('esocial:vlrDespCustas', self.NS)
if vlr_custas is None:
    vlr_custas = desp_proc_elem.find('esocial:vlrCustas', self.NS)  # Fallback
    if vlr_custas is not None:
        logger.warning("Tag 'vlrCustas' é um alias. Use 'vlrDespCustas' (oficial)")
```

---

### **Caso 3: Tags Calculadas**

**Problema:** Alguns valores no PDF são calculados, não vêm diretamente do XML.

**Exemplos:**

**Cálculo 1: Total de Rendimentos Tributáveis**
```python
total_tributavel = sum(
    valor for tipo, valor in rendimentos.items()
    if tipo in [11, 12, 13, 14, 15, 16, 17, 18]
)
```

**Cálculo 2: Total de Deduções**
```python
total_deducoes = (
    contrib_previdenciaria +
    dependentes_valor +
    pensao_alimenticia +
    previdencia_privada
)
```

**Cálculo 3: Base de Cálculo**
```python
base_calculo = total_tributavel - total_deducoes
```

---

### **Caso 4: Múltiplos Demonstrativos (12 meses + 13º)**

**Problema:** Um XML pode ter 13 demonstrativos (12 meses + 13º salário).

**Solução:** Processar todos os `dmDev` e consolidar.

**Implementação:**
```python
for dm_dev in ide_trab.findall('esocial:dmDev', self.NS):
    ide_dm_dev = dm_dev.find('esocial:ideDmDev', self.NS)
    
    # Processar cada demonstrativo
    for info_ir in dm_dev.findall('esocial:infoIR', self.NS):
        tp_info_ir = info_ir.find('esocial:tpInfoIR', self.NS)
        valor = info_ir.find('esocial:valor', self.NS)
        
        # Acumular valores por tipo
        rendimentos[int(tp_info_ir.text)] += Decimal(valor.text)
```

---

## 🛠️ Guia de Implementação

### **Como Adicionar uma Nova Tag**

**Passo 1:** Verificar especificação oficial
```
1. Acessar: https://www.gov.br/esocial/pt-br/documentacao-tecnica/leiautes-esocial-v-1.3/
2. Localizar a tag no S-5002
3. Anotar: nome, tipo, obrigatoriedade, grupo pai
```

**Passo 2:** Adicionar ao dataclass
```python
@dataclass
class NovoGrupo:
    """Descrição do grupo"""
    nova_tag: str = ""  # Descrição da tag
    outra_tag: Decimal = Decimal('0.00')
```

**Passo 3:** Adicionar ao parser
```python
def _parse_novo_grupo(self, elem) -> Optional[NovoGrupo]:
    """Parse do novo grupo"""
    try:
        nova_tag = elem.find('esocial:novaTag', self.NS)
        outra_tag = elem.find('esocial:outraTag', self.NS)
        
        return NovoGrupo(
            nova_tag=nova_tag.text if nova_tag is not None else "",
            outra_tag=Decimal(outra_tag.text) if outra_tag is not None else Decimal('0.00')
        )
    except Exception as e:
        logger.warning(f"Erro ao parse novo grupo: {e}")
        return None
```

**Passo 4:** Adicionar ao gerador de PDF
```python
def _desenhar_novo_grupo(self, c, comprovante, y, pagina_atual, total_pages):
    """Desenha o novo grupo no PDF"""
    c.setFont("Helvetica-Bold", 12)
    c.drawString(self.margin_left, y, "NOVO GRUPO")
    y -= 6*mm
    
    c.setFont("Helvetica", 12)
    c.drawString(self.margin_left, y, f"Nova Tag: {comprovante.novo_grupo.nova_tag}")
    y -= 4.5*mm
    
    return y, pagina_atual
```

**Passo 5:** Testar
```python
# Criar XML de teste
xml_test = """
<eSocial>
  <evtIrrfBenef>
    <novoGrupo>
      <novaTag>Valor Teste</novaTag>
      <outraTag>123.45</outraTag>
    </novoGrupo>
  </evtIrrfBenef>
</eSocial>
"""

# Executar parser
parser = S5002Parser('test.xml')
resultado = parser.parse()

# Validar
assert resultado[0].novo_grupo.nova_tag == "Valor Teste"
assert resultado[0].novo_grupo.outra_tag == Decimal('123.45')
```

---

### **Como Modificar um Mapeamento Existente**

**Exemplo:** Mudar o formato de exibição de um valor

**Antes:**
```python
c.drawString(self.margin_left, y, f"Valor: {valor}")
```

**Depois:**
```python
c.drawString(self.margin_left, y, f"Valor: {self._formatar_valor(valor)}")
```

**Função auxiliar:**
```python
def _formatar_valor(self, valor: Decimal) -> str:
    """Formata valor monetário"""
    return f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
```

---

## 📚 Referências

### **Documentação Oficial:**
- [e-Social S-1.3](https://www.gov.br/esocial/pt-br/documentacao-tecnica/leiautes-esocial-v-1.3/)
- [Manual de Orientação do e-Social](https://www.gov.br/esocial/pt-br/documentacao-tecnica/)
- [Tabelas do e-Social](https://www.gov.br/esocial/pt-br/documentacao-tecnica/tabelas)

### **Documentação do Projeto:**
- [README.md](README.md) - Documentação principal
- [CHANGELOG_v6_1.md](CHANGELOG_v6_1.md) - Histórico de mudanças
- [VERSAO_6_DESCRITIVO.md](VERSAO_6_DESCRITIVO.md) - Descritivo de funcionalidades
- [relatorio_conformidade_s5002.md](relatorio_conformidade_s5002.md) - Análise de conformidade

### **Código-Fonte:**
- [s5002_to_pdf.py](s5002_to_pdf.py) - Conversor principal
- [gerador_xml_s5002_v6.py](gerador_xml_s5002_v6.py) - Gerador de XMLs

---

## 📞 Suporte

Para dúvidas sobre mapeamento de tags:

- **Issues:** [GitHub Issues](https://github.com/flaviowbr/esocial_s5002_comprovante_rendimentos/issues)
- **Discussões:** [GitHub Discussions](https://github.com/flaviowbr/esocial_s5002_comprovante_rendimentos/discussions)

---

**Última atualização:** 30 de Outubro de 2025  
**Versão:** 6.1.0  
**Autor:** Sistema Automatizado de Desenvolvimento
