# Arquivos de Teste

Esta pasta contém arquivos de teste para demonstração e validação do conversor S-5002 para PDF.

## 📁 Estrutura

```
testes/
├── xmls/          # XMLs de entrada (10 cenários)
├── pdfs/          # PDFs de saída (exemplos gerados)
└── README.md      # Este arquivo
```

## 📄 XMLs de Teste (10 cenários)

Os XMLs de teste cobrem diferentes cenários de complexidade e casos de uso:

### **Empresa 1 - Tech Solutions Ltda (CNPJ: 12.345.678/0001-90)**

| Arquivo | Cenário | Complexidade | Descrição |
|---------|---------|--------------|-----------|
| `cenario_01_empresa1_12345678901.xml` | Básico | ⭐ Simples | Apenas rendimentos básicos |
| `cenario_05_empresa1_12345678905.xml` | Dependentes | ⭐⭐ Médio | Com 2 dependentes |
| `cenario_10_empresa1_12345678910.xml` | Plano de saúde | ⭐⭐ Médio | Com plano de saúde |
| `cenario_15_empresa1_12345678915.xml` | Pensão alimentícia | ⭐⭐⭐ Complexo | Com pensão alimentícia |
| `cenario_20_empresa1_12345678920.xml` | Completo | ⭐⭐⭐⭐ Muito complexo | Múltiplos grupos |

### **Empresa 2 - Indústria ABC S.A. (CNPJ: 98.765.432/0001-10)**

| Arquivo | Cenário | Complexidade | Descrição |
|---------|---------|--------------|-----------|
| `cenario_30_empresa2_98765432110.xml` | RRA | ⭐⭐⭐ Complexo | Rendimentos recebidos acumuladamente |
| `cenario_40_empresa2_98765432120.xml` | Processo judicial | ⭐⭐⭐⭐ Muito complexo | Com processos judiciais |

### **Empresa 3 - Comércio XYZ Ltda (CNPJ: 55.566.677/0001-88)**

| Arquivo | Cenário | Complexidade | Descrição |
|---------|---------|--------------|-----------|
| `cenario_50_empresa3_55566677710.xml` | Pagamento exterior | ⭐⭐⭐ Complexo | Pagamento no exterior |
| `cenario_59_empresa3_55566677719.xml` | Múltiplos demonstrativos | ⭐⭐⭐⭐⭐ Extremamente complexo | Todos os grupos |
| `cenario_60_empresa3_55566677720.xml` | Consolidação completa | ⭐⭐⭐⭐⭐ Extremamente complexo | Todos os 33 grupos |

## 📊 PDFs de Exemplo

Os PDFs de exemplo demonstram o resultado final da conversão:

### **exemplo_simples.pdf**
- **Origem:** `cenario_01_empresa1_12345678901.xml`
- **Páginas:** 1
- **Conteúdo:** Comprovante básico com apenas rendimentos tributáveis
- **Ideal para:** Entender o formato básico do PDF gerado

### **exemplo_complexo.pdf**
- **Origem:** `cenario_60_empresa3_55566677720.xml`
- **Páginas:** 2
- **Conteúdo:** Comprovante completo com todos os 33 grupos do e-Social S-1.3
- **Ideal para:** Ver todas as funcionalidades do conversor

## 🚀 Como Usar

### **1. Testar com os XMLs fornecidos:**

```bash
# Converter todos os XMLs de teste
python s5002_to_pdf.py testes/xmls/ saida/ --ano 2024

# Converter com CSV de nomes
python s5002_to_pdf.py testes/xmls/ saida/ --ano 2024 --csv exemplo_nomes.csv
```

### **2. Testar um XML específico:**

```bash
# Cenário simples
python s5002_to_pdf.py testes/xmls/cenario_01_empresa1_12345678901.xml saida/ --ano 2024

# Cenário complexo
python s5002_to_pdf.py testes/xmls/cenario_60_empresa3_55566677720.xml saida/ --ano 2024
```

### **3. Comparar com os exemplos:**

Após gerar os PDFs, compare com os exemplos fornecidos em `testes/pdfs/` para validar o resultado.

## 📋 Grupos do e-Social Cobertos

Os XMLs de teste cobrem **todos os 33 grupos/subgrupos** do e-Social S-5002 (versão S-1.3):

- ✅ Identificação do trabalhador
- ✅ Demonstrativos de valores devidos
- ✅ Informações de IR complementares
- ✅ Dependentes
- ✅ Planos de saúde
- ✅ Reembolsos médicos
- ✅ Pensão alimentícia
- ✅ Rendimentos recebidos acumuladamente (RRA)
- ✅ Processos judiciais
- ✅ Pagamentos no exterior
- ✅ Informações por código de receita (DIRF)
- ✅ Totalizações diárias
- ✅ Consolidações mensais
- ✅ Períodos anteriores
- ✅ E muito mais!

## 🎯 Casos de Uso Cobertos

| Caso de Uso | Cenários |
|-------------|----------|
| Funcionário sem dependentes | 01, 10, 30, 50 |
| Funcionário com dependentes | 05, 15, 20, 40, 59, 60 |
| Com plano de saúde | 10, 20, 40, 59, 60 |
| Com pensão alimentícia | 15, 20, 59, 60 |
| Com RRA | 30, 59, 60 |
| Com processo judicial | 40, 59, 60 |
| Pagamento exterior | 50, 59, 60 |
| Múltiplos demonstrativos | 59, 60 |

## 📊 Estatísticas

- **Total de XMLs:** 10
- **Total de PDFs de exemplo:** 2
- **Empresas diferentes:** 3
- **Funcionários diferentes:** 10
- **Grupos do e-Social cobertos:** 33/33 (100%)
- **Tamanho médio dos XMLs:** 2.5 KB
- **Tamanho médio dos PDFs:** 4.8 KB

## 🔍 Validação

Para validar que o conversor está funcionando corretamente:

1. ✅ Execute o conversor nos XMLs de teste
2. ✅ Compare os PDFs gerados com os exemplos fornecidos
3. ✅ Verifique se todos os campos estão sendo exibidos
4. ✅ Confirme que a paginação está correta
5. ✅ Valide que os nomes aparecem corretamente (quando usar CSV)

## 📞 Suporte

Se encontrar algum problema com os arquivos de teste ou tiver dúvidas:

1. Verifique a [documentação principal](../README.md)
2. Consulte o [guia de contribuição](../CONTRIBUTING.md)
3. Abra uma [issue](https://github.com/flaviowbr/esocial_s5002_comprovante_rendimentos/issues)

---

**Última atualização:** 30 de Outubro de 2025  
**Versão do conversor:** 5.2.2  
**Conformidade:** 100% com e-Social S-1.3
