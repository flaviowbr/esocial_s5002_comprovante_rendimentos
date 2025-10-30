# Política de Segurança

## 🔒 Versões Suportadas

Atualmente, as seguintes versões recebem atualizações de segurança:

| Versão | Suportada          |
| ------ | ------------------ |
| 5.2.x  | :white_check_mark: |
| 5.1.x  | :white_check_mark: |
| 5.0.x  | :x:                |
| < 5.0  | :x:                |

## 🐛 Reportando uma Vulnerabilidade

A segurança dos usuários é nossa prioridade. Se você descobriu uma vulnerabilidade de segurança, por favor:

### **NÃO** abra uma issue pública

Vulnerabilidades de segurança não devem ser divulgadas publicamente até que sejam corrigidas.

### **Reporte Privadamente**

1. Envie um email para o mantenedor através do GitHub
2. Ou use a funcionalidade "Security" → "Report a vulnerability" do GitHub
3. Descreva a vulnerabilidade em detalhes:
   - Tipo de vulnerabilidade
   - Passos para reproduzir
   - Impacto potencial
   - Possível solução (se houver)

### **O Que Esperar**

- **Confirmação:** Você receberá uma confirmação dentro de 48 horas
- **Avaliação:** Avaliaremos a vulnerabilidade e sua gravidade
- **Correção:** Trabalharemos em uma correção o mais rápido possível
- **Divulgação:** Após a correção, divulgaremos a vulnerabilidade de forma responsável
- **Crédito:** Você será creditado pela descoberta (se desejar)

## 🛡️ Boas Práticas de Segurança

### **Para Usuários**

1. **Dados Sensíveis:** Sempre remova dados sensíveis dos XMLs antes de compartilhar
2. **Atualizações:** Mantenha o conversor atualizado com a versão mais recente
3. **Validação:** Valide os PDFs gerados antes de distribuir
4. **Permissões:** Execute o conversor com as permissões mínimas necessárias

### **Para Desenvolvedores**

1. **Dependências:** Mantenha as dependências atualizadas
2. **Validação de Entrada:** Sempre valide XMLs de entrada
3. **Sanitização:** Sanitize dados antes de processar
4. **Testes:** Teste com XMLs malformados e maliciosos

## 📋 Checklist de Segurança

Ao processar XMLs do e-Social:

- [ ] Remova CPFs, nomes e dados pessoais se for compartilhar
- [ ] Valide a origem do XML
- [ ] Verifique se o XML está bem formado
- [ ] Use a versão mais recente do conversor
- [ ] Armazene PDFs gerados de forma segura
- [ ] Não compartilhe PDFs com dados reais publicamente

## 🔐 Conformidade

Este projeto processa dados do e-Social que podem conter informações pessoais. Certifique-se de:

- Cumprir a **LGPD** (Lei Geral de Proteção de Dados)
- Seguir as diretrizes do **e-Social**
- Proteger dados de funcionários e empresas
- Implementar controles de acesso adequados

## 📞 Contato

Para questões de segurança, use os canais privados mencionados acima.

Para outras questões, abra uma issue normal no repositório.

---

**Obrigado por ajudar a manter este projeto seguro!** 🛡️
