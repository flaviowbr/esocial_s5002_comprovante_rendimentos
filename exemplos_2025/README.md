# Exemplos 2025 - XMLs e PDFs Gerados

## 📋 Descrição

Esta pasta contém **30 arquivos XML** de exemplo gerados para o ano de 2025, representando comprovantes de rendimentos do e-Social S-5002 com **12 meses + 13º salário** por funcionário.

---

## 📊 Conteúdo

### **Arquivos XML (30 arquivos)**
- 10 XMLs para **TechCorp Soluções Ltda** (CNPJ 12.345.678/0001-90)
- 10 XMLs para **Inovação Digital S.A.** (CNPJ 98.765.432/0001-10)
- 10 XMLs para **Consultoria Estratégica Brasil** (CNPJ 55.566.677/0001-10)

### **Arquivos PDF (18 arquivos)**
- PDFs gerados com sucesso para funcionários de nível **simples** e **médio**
- **Nota:** PDFs de nível complexo e muito complexo não foram gerados devido a bug conhecido (veja CHANGELOG_v6.md)

### **Arquivos CSV (2 arquivos)**
- `nomes_funcionarios_2025.csv` - Dados completos dos funcionários
- `nomes_para_conversor.csv` - Formato compatível com o conversor

---

## 🏢 Empresas

### **Empresa 1: TechCorp Soluções Ltda**
- **CNPJ:** 12.345.678/0001-90
- **Funcionários:** 10 (CPFs 10000000000 a 10000000090)

### **Empresa 2: Inovação Digital S.A.**
- **CNPJ:** 98.765.432/0001-10
- **Funcionários:** 10 (CPFs 10000001000 a 10000001090)

### **Empresa 3: Consultoria Estratégica Brasil**
- **CNPJ:** 55.566.677/0001-10
- **Funcionários:** 10 (CPFs 10000002000 a 10000002090)

---

## 📅 Estrutura dos XMLs

Cada XML contém **13 demonstrativos** (`dmDev`):
- **12 demonstrativos mensais** (janeiro a dezembro de 2025)
- **1 demonstrativo de 13º salário**

### **Exemplo de Estrutura:**

```xml
<dmDev>
    <perRef>2025-01</perRef>  <!-- Janeiro -->
    <ideDmDev>1</ideDmDev>
    <indRRA>N</indRRA>
    <infoIR>...</infoIR>
</dmDev>
...
<dmDev>
    <perRef>2025-12</perRef>  <!-- Dezembro -->
    <ideDmDev>12</ideDmDev>
    <indRRA>N</indRRA>
    <infoIR>...</infoIR>
</dmDev>
<dmDev>
    <perRef>2025</perRef>     <!-- 13º Salário -->
    <ideDmDev>13</ideDmDev>
    <indRRA>N</indRRA>
    <infoIR>...</infoIR>
</dmDev>
```

---

## 🎯 Níveis de Complexidade

### **Nível 1 - Simples (3 funcionários por empresa)**
- Rendimentos tributáveis (tpInfoIR=11)
- Contribuição previdenciária (tpInfoIR=41)
- Imposto retido (tpInfoIR=31)
- **Total: 9 XMLs**

### **Nível 2 - Médio (3 funcionários por empresa)**
- Tudo do nível simples
- 2 dependentes
- **Total: 9 XMLs**

### **Nível 3 - Complexo (2 funcionários por empresa)**
- Tudo do nível médio
- Plano de saúde (tpInfoIR=67)
- Previdência privada (tpInfoIR=46)
- **Total: 6 XMLs**

### **Nível 4 - Muito Complexo (2 funcionários por empresa)**
- Tudo do nível complexo
- 3 dependentes
- Pensão alimentícia (tpInfoIR=51)
- **Total: 6 XMLs**

---

## 💰 Valores

### **Salário Base:**
- **Mensal:** ~R$ 10.000,00
- **Anual (12 meses):** ~R$ 120.000,00
- **13º Salário:** ~R$ 10.000,00
- **Total Anual:** ~R$ 130.000,00

### **Variações:**
- Simples: ±5%
- Médio: ±10%
- Complexo: ±15%
- Muito Complexo: ±20%

---

## 📁 Nomenclatura dos Arquivos

### **XMLs:**
```
xml_{ano}_{cnpj}_{cpf}_{complexidade}.xml
```

**Exemplo:**
```
xml_2025_12345678000190_10000000000_simples.xml
```

### **PDFs:**
```
irpf{ano}-{cpf_formatado}.pdf
```

**Exemplo:**
```
irpf2025-100_000_000_00.pdf
```

---

## 🔍 Como Usar

### **1. Visualizar XMLs:**
```bash
# Abrir um XML
cat xml_2025_12345678000190_10000000000_simples.xml
```

### **2. Gerar PDFs:**
```bash
# Gerar PDFs de todos os XMLs
python ../s5002_to_pdf.py . ./pdfs --ano 2025 --csv nomes_para_conversor.csv
```

### **3. Validar Estrutura:**
```bash
# Contar demonstrativos em um XML
grep -c "<dmDev>" xml_2025_12345678000190_10000000000_simples.xml
# Resultado esperado: 13
```

---

## ⚠️ Observações Importantes

### **PDFs Não Gerados:**
Os PDFs de funcionários de nível **complexo** e **muito complexo** não foram gerados devido a um bug conhecido no renderizador PDF (veja `CHANGELOG_v6.md` para detalhes).

**Funcionários afetados:**
- Funcionários 07-10 de cada empresa (CPFs terminados em 60, 70, 80, 90)
- **Total:** 12 PDFs não gerados

**Status:** Correção planejada para versão 6.1.0

### **XMLs Válidos:**
Todos os 30 XMLs são **válidos** e seguem a especificação e-Social S-1.3. O problema está apenas na geração do PDF, não na estrutura do XML.

---

## 📝 CSV de Nomes

### **nomes_funcionarios_2025.csv:**
Contém dados completos de todos os funcionários:
- CPF
- Nome
- CNPJ da empresa
- Nome da empresa
- Nível de complexidade

### **nomes_para_conversor.csv:**
Formato compatível com o conversor:
- CPF
- nome_funcionario
- CNPJ
- nome_empresa

---

## 🔗 Referências

- [Documentação e-Social S-1.3](https://www.gov.br/esocial/pt-br/documentacao-tecnica/leiautes-esocial-v-1.3/)
- [CHANGELOG_v6.md](../CHANGELOG_v6.md) - Histórico de mudanças
- [VERSAO_6_DESCRITIVO.md](../VERSAO_6_DESCRITIVO.md) - Descritivo completo

---

## 📊 Estatísticas

| Métrica | Valor |
|---------|-------|
| Total de XMLs | 30 |
| Total de PDFs gerados | 18 |
| Total de empresas | 3 |
| Funcionários por empresa | 10 |
| Demonstrativos por funcionário | 13 |
| Total de demonstrativos | 390 |
| Ano de referência | 2025 |

---

**Gerado automaticamente pelo Gerador de XMLs v6.0.0**
