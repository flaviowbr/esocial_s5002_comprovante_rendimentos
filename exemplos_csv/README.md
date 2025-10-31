# Exemplos de CSVs Auxiliares

Esta pasta contém exemplos de arquivos CSV auxiliares para complementar informações que podem estar vazias nos XMLs do e-Social.

## 📋 Arquivos Disponíveis

### 1. `exemplo_dependentes.csv`

Contém informações de dependentes para preencher nomes vazios.

**Formato:**
```csv
cpf_titular,cpf_dependente,nome_dependente,data_nascimento,tipo_dependente
```

**Campos:**
- `cpf_titular`: CPF do titular (11 dígitos, sem formatação)
- `cpf_dependente`: CPF do dependente (11 dígitos, sem formatação)
- `nome_dependente`: Nome completo do dependente
- `data_nascimento`: Data de nascimento (DD/MM/AAAA)
- `tipo_dependente`: Tipo de dependente (Filho, Filha, Cônjuge, etc.)

**Exemplo:**
```csv
12345678901,09140313174,Maria Silva Santos,15/03/2010,Filha
12345678901,82679231368,Pedro Silva Santos,20/08/2015,Filho
```

---

### 2. `exemplo_entidades.csv`

Contém informações de entidades (operadoras de saúde e previdência) para preencher nomes vazios.

**Formato:**
```csv
cnpj,tipo,nome,registro
```

**Campos:**
- `cnpj`: CNPJ da entidade (14 dígitos, sem formatação)
- `tipo`: Tipo da entidade (`plano_saude`, `previdencia`, ou `empresa`)
- `nome`: Nome completo da entidade
- `registro`: Número de registro (ANS para planos de saúde, vazio para previdência)

**Exemplo:**
```csv
33719485000127,plano_saude,Unimed São Paulo Cooperativa de Trabalho Médico,346659
33754482000124,previdencia,Bradesco Vida e Previdência S.A.,
```

---

## 🚀 Como Usar

### Uso Básico (apenas funcionários)
```bash
python3 s5002_to_pdf.py \
  /caminho/xmls \
  /caminho/pdfs \
  --ano 2025 \
  --csv funcionarios.csv
```

### Uso Completo (com todos os CSVs)
```bash
python3 s5002_to_pdf.py \
  /caminho/xmls \
  /caminho/pdfs \
  --ano 2025 \
  --csv funcionarios.csv \
  --csv-dependentes dependentes.csv \
  --csv-entidades entidades.csv
```

---

## 💡 Sistema de Fallback

O conversor usa um sistema inteligente de fallback:

1. **Tenta ler do XML primeiro** (prioridade)
2. **Se vazio, busca no CSV correspondente**
3. **Se não encontrar, usa valor padrão**: `(Nome não informado)`

**Exemplo:**
```
XML: <nmDep></nmDep>  (vazio)
CSV: 12345678901,09140313174,Maria Silva Santos,...
PDF: Nome: Maria Silva Santos  ✅
```

---

## 📝 Notas Importantes

1. **CSVs são opcionais** - O conversor funciona sem eles
2. **CPFs sem formatação** - Use apenas dígitos (11 para CPF, 14 para CNPJ)
3. **Encoding UTF-8** - Salve os CSVs com encoding UTF-8
4. **Cabeçalho obrigatório** - Primeira linha deve conter os nomes das colunas
5. **Compatibilidade** - Funciona com XMLs antigos e novos

---

## 🔧 Criando Seus Próprios CSVs

### Dependentes
```bash
# Criar CSV de dependentes
cat > meus_dependentes.csv << 'EOF'
cpf_titular,cpf_dependente,nome_dependente,data_nascimento,tipo_dependente
12345678901,11122233344,João Silva,01/01/2010,Filho
12345678901,55566677788,Maria Silva,15/06/2012,Filha
EOF
```

### Entidades
```bash
# Criar CSV de entidades
cat > minhas_entidades.csv << 'EOF'
cnpj,tipo,nome,registro
12345678000190,plano_saude,Minha Operadora de Saúde,123456
98765432000110,previdencia,Minha Previdência Privada,
EOF
```

---

## 📚 Documentação Completa

Para mais informações, consulte:
- [README.md principal](../README.md)
- [MAPEAMENTO_TAGS_COMPLETO.md](../MAPEAMENTO_TAGS_COMPLETO.md)
- [CHANGELOG_v6_2.md](../CHANGELOG_v6_2.md)
