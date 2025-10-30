# 📁 Exemplos de Uso

Esta pasta contém exemplos de XMLs do e-Social S-5002 e CSVs de nomes para testar o conversor.

---

## 📄 Arquivos Disponíveis

### **XMLs de Exemplo**

1. **exemplo_simples.xml** - Exemplo básico com um trabalhador e poucos grupos
2. **exemplo_completo.xml** - Exemplo com todos os 33 grupos implementados
3. **exemplo_multiplos.xml** - Exemplo com múltiplos trabalhadores no mesmo arquivo

### **CSVs de Exemplo**

1. **exemplo_nomes.csv** - CSV com nomes de empresas e funcionários

---

## 🚀 Como Usar

### **Teste Básico**

```bash
# Converter um XML simples
python s5002_to_pdf.py exemplos/exemplo_simples.xml output/ --ano 2024
```

### **Teste com CSV de Nomes**

```bash
# Converter com nomes de empresas e funcionários
python s5002_to_pdf.py exemplos/ output/ --ano 2024 --csv exemplos/exemplo_nomes.csv
```

### **Teste com Múltiplos Arquivos**

```bash
# Converter todos os XMLs da pasta
python s5002_to_pdf.py exemplos/ output/ --ano 2024
```

### **Teste com Processamento Paralelo**

```bash
# Usar 8 workers para processar mais rápido
python s5002_to_pdf.py exemplos/ output/ --ano 2024 --workers 8
```

---

## 📋 Estrutura do CSV de Nomes

O CSV deve ter as seguintes colunas:

```csv
cpf,nome_funcionario,nome_empresa,cnpj_empresa
12345678901,João da Silva,Empresa ABC Ltda,12345678000190
98765432100,Maria Santos,Empresa XYZ S/A,98765432000199
```

**Observações:**
- CPF e CNPJ devem estar **sem formatação** (apenas números)
- Encoding: **UTF-8**
- Separador: **vírgula**
- Primeira linha: **cabeçalho** (obrigatório)

---

## 🧪 Testando Seus Próprios XMLs

Para testar com seus próprios XMLs:

1. **Remova dados sensíveis** (CPFs, nomes reais, valores)
2. Coloque o XML na pasta `exemplos/`
3. Execute o conversor
4. Verifique o PDF gerado em `output/`

---

## ⚠️ Dados de Teste

**IMPORTANTE:** Todos os dados nestes exemplos são **fictícios** e foram criados apenas para demonstração. Não use dados reais em exemplos públicos.

---

## 📚 Documentação Adicional

Para mais informações sobre o formato do S-5002, consulte:
- [Manual do e-Social](https://www.gov.br/esocial/)
- [Leiautes e-Social v1.3](https://www.gov.br/esocial/pt-br/documentacao-tecnica/leiautes-esocial-v-1.3)

---

## 💡 Dicas

1. **Performance:** Use `--workers` para processar múltiplos arquivos mais rápido
2. **Nomes:** Use CSV para adicionar nomes de empresas e funcionários
3. **Validação:** Sempre valide os PDFs gerados antes de usar
4. **Backup:** Mantenha backup dos XMLs originais

---

## 🐛 Encontrou um Problema?

Se algum exemplo não funcionar corretamente:

1. Verifique se você tem a versão mais recente do conversor
2. Verifique se todas as dependências estão instaladas
3. Abra uma [issue](https://github.com/flaviowbr/esocial_s5002_comprovante_rendimentos/issues) com detalhes

---

**Bons testes!** 🚀
