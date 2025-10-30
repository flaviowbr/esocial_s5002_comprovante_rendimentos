# Estrutura Oficial do e-Social S-5002 - Imposto de Renda Retido na Fonte por Trabalhador

**Fonte:** Portal Gov.br - Documentação Técnica e-Social S-1.3
**Data:** 30/10/2025

## Tabela de Resumo dos Registros

| Grupo | Grupo Pai | Nível | Descrição | Ocor. | Chave | Condição |
|-------|-----------|-------|-----------|-------|-------|----------|
| **eSocial** | - | 1 | eSocial | 1 | - | O |
| **evtIrrfBenef** | eSocial | 2 | Evento IRRF por Trabalhador | 1 | Id | O |
| **ideEvento** | evtIrrfBenef | 3 | Identificação do evento de retorno | 1 | perApur* | O |
| **ideEmpregador** | evtIrrfBenef | 3 | Informações de identificação do empregador | 1 | nrInsc*, tpInsc* | O |
| **ideTrabalhador** | evtIrrfBenef | 3 | Identificação do beneficiário | 1 | nrInsc* | O |
| **dmDev** | ideTrabalhador | 4 | Informações do demonstrativo de valores devidos | 0-N | perRef*, ideDmDev*, tpPgto* | OC |
| **infoIR** | dmDev | 5 | Rendimentos tributáveis, deduções, isenções e retenções do IRRF | 0-999 | tpInfIR* | O |
| **infoProcJudIR** | infoIR | 6 | Informações complementares - Demais rendimentos com exigibilidade suspensa decorrentes de decisão judicial aplicável à rubrica | 0-N | nrL* | OC |
| **totApurMen** | dmDev | 5 | Totalizador dos rendimentos tributáveis, deduções, isenções e retenção de tributos com período de apuração mensal | 0-50 | CRMen* | OC |
| **totApurDia** | dmDev | 5 | Totalizador de rendimentos tributáveis e tributos com período de apuração diário | 0-350 | perApurDia*, CRDia*, tpInfIR*, paisResid* | OC |

**Legenda:**
- O = Obrigatório
- OC = Obrigatório se (condicional)
- * = Campo que compõe a chave do registro

## Grupos Principais (33 grupos implementados no conversor v5.2.1)

### Nível 4 - dmDev (Demonstrativo de Valores Devidos)
- **perRef**: Período de referência (AAAA-MM)
- **ideDmDev**: Identificador do demonstrativo
- **tpPgto**: Tipo de pagamento

### Nível 5 - infoIR (Informações de IRRF)
- **tpInfIR**: Tipo de informação de IRRF
- Contém todos os rendimentos, deduções e retenções

### Grupos de Rendimentos e Deduções (dentro de infoIR):
1. **basesIrrf** - Bases de cálculo do IRRF
2. **irrf** - Valores de IRRF retido
3. **dedDepen** - Dedução por dependentes
4. **penAlim** - Pensão alimentícia
5. **previdSocial** - Previdência social
6. **infoProcRet** - Informações de processos judiciais
7. **planSaude** - Plano de saúde
8. **reembMed** - Reembolso médico
9. **infoPgtoExt** - Informações de pagamento exterior
10. **infoRRA** - Informações de RRA (Rendimentos Recebidos Acumuladamente)

## Observações Importantes:

1. **Estrutura Hierárquica Obrigatória:**
   - eSocial → evtIrrfBenef → ideEvento/ideEmpregador/ideTrabalhador → dmDev → infoIR

2. **Campos Chave Obrigatórios:**
   - perRef (período de referência no formato AAAA-MM)
   - ideDmDev (identificador único do demonstrativo)
   - tpPgto (tipo de pagamento)

3. **Multiplicidade:**
   - dmDev: 0-N (pode ter múltiplos demonstrativos)
   - infoIR: 0-999 (pode ter múltiplas informações de IR por demonstrativo)

4. **Versão do Leiaute:**
   - S-1.3 (aprovada pela Portaria Conjunta RFB/MPS/MTE nº 13, de 25/06/2024)
   - Implantação: 02/12/2024
   - Período de convivência: 02/12/2024 a 02/02/2025

## Próximos Passos:

1. ✅ Validar que o conversor v5.2.1 implementa TODOS os 33 grupos corretamente
2. ⏳ Revisar cada tag do código para garantir conformidade 100%
3. ⏳ Criar gerador de simulação que respeite esta estrutura oficial
4. ⏳ Gerar exemplos com 12 meses + 13º salário
