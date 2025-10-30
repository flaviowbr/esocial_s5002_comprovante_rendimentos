# 10 Testes Completos - Ano Completo 2024

Esta pasta contém **10 testes completos** do e-Social S-5002 com:

- ✅ **12 meses** de pagamentos (Janeiro a Dezembro 2024)
- ✅ **13º salário**
- ✅ **Valores mensais variados** (R$ 8.500 a R$ 10.000)
- ✅ **3 empresas diferentes**
- ✅ **Diferentes níveis de complexidade**
- ✅ **CSV com nomes** incluído

## 📋 Lista de Testes

| # | CPF | Empresa | Complexidade | Descrição |
|---|-----|---------|--------------|-----------|
| 01 | 111.222.333-01 | Tech Solutions | ⭐ Simples | Apenas rendimentos mensais + 13º |
| 02 | 222.333.444-02 | Tech Solutions | ⭐⭐ Médio | Com 1 dependente |
| 03 | 333.444.555-03 | Tech Solutions | ⭐⭐ Médio | Com 2 dependentes |
| 04 | 444.555.666-04 | Indústria ABC | ⭐⭐⭐ Complexo | Com plano de saúde |
| 05 | 555.666.777-05 | Indústria ABC | ⭐⭐⭐ Complexo | Com pensão alimentícia |
| 06 | 666.777.888-06 | Indústria ABC | ⭐⭐ Médio | 2 dependentes |
| 07 | 777.888.999-07 | Comércio XYZ | ⭐⭐⭐ Complexo | Plano de saúde |
| 08 | 888.999.000-08 | Comércio XYZ | ⭐⭐⭐ Complexo | Pensão alimentícia |
| 09 | 999.000.111-09 | Comércio XYZ | ⭐⭐⭐⭐ Muito Complexo | Pensão + dependentes |
| 10 | 100.111.222-10 | Tech Solutions | ⭐⭐⭐⭐ Muito Complexo | Todos os grupos |

## 💰 Valores Anuais

- **Salário mensal:** R$ 8.500 a R$ 10.000 (variável)
- **Total anual:** ~R$ 112.000
- **13º salário:** R$ 10.000
- **IRRF médio:** 15% sobre rendimentos

## 🚀 Como Usar

```bash
# Gerar PDFs COM nomes
python s5002_to_pdf.py testes/ pdfs/ --ano 2024 --csv testes/nomes_testes.csv

# Gerar PDFs SEM nomes
python s5002_to_pdf.py testes/ pdfs/ --ano 2024
```

---

**Última atualização:** 30 de Outubro de 2025  
**Versão:** 5.2.2
