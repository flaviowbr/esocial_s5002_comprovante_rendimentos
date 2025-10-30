# Política de Segurança

## 🔒 Versões Suportadas

Atualmente, as seguintes versões recebem atualizações de segurança:

| Versão | Status | Manutenção |
| ------ | ------ | ---------- |
| **6.1.0** | ✅ Atual | ✅ Ativa |
| 6.0.0 | ⚠️ Deprecated | ❌ Migrar para 6.1.0 |
| 5.x | ⚠️ End-of-life | ❌ Sem suporte |
| < 5.0 | ❌ Obsoleta | ❌ Sem suporte |

### **Recomendações:**

- ✅ **Use sempre a versão 6.1.0** (mais recente e estável)
- ⚠️ **Migre de versões antigas imediatamente**
- 🔒 **Versões 5.x não recebem mais atualizações de segurança**

---

## 🐛 Reportando uma Vulnerabilidade

A segurança dos usuários é nossa prioridade. Se você descobriu uma vulnerabilidade de segurança, por favor:

### **NÃO** abra uma issue pública

Vulnerabilidades de segurança não devem ser divulgadas publicamente até que sejam corrigidas.

### **Reporte Privadamente**

1. Use a funcionalidade **"Security" → "Report a vulnerability"** do GitHub
2. Ou envie um email para o mantenedor através do GitHub
3. Descreva a vulnerabilidade em detalhes:
   - Tipo de vulnerabilidade
   - Versão afetada
   - Passos para reproduzir
   - Impacto potencial
   - Possível solução (se houver)

### **O Que Esperar**

- **Confirmação:** Você receberá uma confirmação dentro de 48 horas
- **Avaliação:** Avaliaremos a vulnerabilidade e sua gravidade
- **Correção:** Trabalharemos em uma correção o mais rápido possível
- **Patch:** Lançaremos uma versão de correção
- **Divulgação:** Após a correção, divulgaremos a vulnerabilidade de forma responsável
- **Crédito:** Você será creditado pela descoberta (se desejar)

---

## 🛡️ Boas Práticas de Segurança

### **Para Usuários**

**Proteção de Dados:**
1. **Dados Sensíveis:** Sempre remova dados sensíveis dos XMLs antes de compartilhar
2. **CPF/CNPJ:** Anonimize CPFs e CNPJs em ambientes de teste
3. **Nomes:** Substitua nomes reais por fictícios em exemplos
4. **Valores:** Use valores fictícios em demonstrações

**Segurança Operacional:**
1. **Atualizações:** Mantenha o conversor atualizado com a versão mais recente
2. **Validação:** Valide os PDFs gerados antes de distribuir
3. **Permissões:** Execute o conversor com as permissões mínimas necessárias
4. **Armazenamento:** Armazene PDFs gerados de forma segura

### **Para Desenvolvedores**

**Código Seguro:**
1. **Dependências:** Mantenha as dependências atualizadas
2. **Validação de Entrada:** Sempre valide XMLs de entrada
3. **Sanitização:** Sanitize dados antes de processar
4. **Testes:** Teste com XMLs malformados e maliciosos

**Revisão de Código:**
1. **Pull Requests:** Revise PRs com foco em segurança
2. **Testes:** Adicione testes de segurança
3. **Documentação:** Documente riscos de segurança
4. **Auditoria:** Realize auditorias periódicas

---

## 📋 Checklist de Segurança

Ao processar XMLs do e-Social:

- [ ] Remova CPFs, nomes e dados pessoais se for compartilhar
- [ ] Valide a origem do XML
- [ ] Verifique se o XML está bem formado
- [ ] Use a versão **6.1.0** (mais recente)
- [ ] Armazene PDFs gerados de forma segura
- [ ] Não compartilhe PDFs com dados reais publicamente
- [ ] Implemente controles de acesso adequados
- [ ] Faça backup regular dos dados
- [ ] Monitore logs de processamento
- [ ] Teste em ambiente isolado primeiro

---

## 🔐 Conformidade

Este projeto processa dados do e-Social que podem conter informações pessoais. Certifique-se de:

### **LGPD (Lei Geral de Proteção de Dados):**
- Obter consentimento para processamento de dados
- Implementar medidas de segurança adequadas
- Garantir direitos dos titulares de dados
- Manter registro de atividades de processamento
- Notificar incidentes de segurança

### **e-Social:**
- Seguir as diretrizes oficiais do e-Social
- Usar apenas dados autorizados
- Proteger dados de funcionários e empresas
- Manter confidencialidade das informações

### **Segurança da Informação:**
- Implementar controles de acesso
- Criptografar dados sensíveis em repouso
- Usar conexões seguras para transmissão
- Realizar backups regulares
- Manter logs de auditoria

---

## 🚨 Vulnerabilidades Conhecidas

### **Versão 6.1.0:**
- ✅ Nenhuma vulnerabilidade conhecida

### **Versão 6.0.0:**
- ⚠️ **DEPRECATED** - Migrar para 6.1.0
- Bug de renderização de PDFs complexos (corrigido na 6.1.0)

### **Versões 5.x:**
- ❌ **END-OF-LIFE** - Sem suporte de segurança
- Múltiplas vulnerabilidades não corrigidas
- Migração obrigatória para 6.1.0

---

## 📞 Contato

### **Segurança:**
- **GitHub Security:** Use "Security" → "Report a vulnerability"
- **Email:** Através do perfil do mantenedor no GitHub

### **Outras Questões:**
- **Issues:** [GitHub Issues](https://github.com/flaviowbr/esocial_s5002_comprovante_rendimentos/issues)
- **Discussões:** [GitHub Discussions](https://github.com/flaviowbr/esocial_s5002_comprovante_rendimentos/discussions)

---

## 📚 Recursos Adicionais

- [CHANGELOG](CHANGELOG.md) - Histórico de mudanças
- [CONTRIBUTING](CONTRIBUTING.md) - Guia de contribuição
- [README](README.md) - Documentação principal
- [SECURITY ADVISORIES](https://github.com/flaviowbr/esocial_s5002_comprovante_rendimentos/security/advisories) - Avisos de segurança

---

**Obrigado por ajudar a manter este projeto seguro!** 🛡️

**Última atualização:** 30 de Outubro de 2025  
**Versão da política:** 2.0
