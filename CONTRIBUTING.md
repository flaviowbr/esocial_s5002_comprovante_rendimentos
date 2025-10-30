# 🤝 Guia de Contribuição

Obrigado por considerar contribuir com o **Conversor S-5002 para PDF**! Este documento fornece diretrizes para contribuir com o projeto.

---

## 📋 Como Contribuir

### **1. Reportar Bugs**

Se você encontrou um bug, por favor:

1. Verifique se o bug já não foi reportado nas [Issues](https://github.com/flaviowbr/esocial_s5002_comprovante_rendimentos/issues)
2. Se não foi, crie uma nova issue com:
   - **Título claro** descrevendo o problema
   - **Descrição detalhada** do bug
   - **Passos para reproduzir** o problema
   - **Comportamento esperado** vs **comportamento atual**
   - **Versão do Python** e sistema operacional
   - **Exemplo de XML** que causa o problema (se possível)

### **2. Sugerir Melhorias**

Para sugerir novas funcionalidades:

1. Abra uma [Issue](https://github.com/flaviowbr/esocial_s5002_comprovante_rendimentos/issues) com a tag `enhancement`
2. Descreva claramente:
   - **O que** você gostaria de adicionar
   - **Por que** isso seria útil
   - **Como** deveria funcionar

### **3. Contribuir com Código**

#### **Preparação do Ambiente**

```bash
# Clone o repositório
git clone https://github.com/flaviowbr/esocial_s5002_comprovante_rendimentos.git
cd esocial_s5002_comprovante_rendimentos

# Instale as dependências
pip install -r requirements.txt

# Crie uma branch para sua feature
git checkout -b feature/minha-feature
```

#### **Padrões de Código**

- Use **Python 3.8+**
- Siga **PEP 8** para estilo de código
- Adicione **docstrings** para funções e classes
- Mantenha **compatibilidade** com versões anteriores quando possível
- Escreva **código limpo** e bem comentado

#### **Estrutura de Commits**

Use commits semânticos:

```
feat: adiciona suporte para novo grupo X do e-Social
fix: corrige erro de parsing em dependentes
docs: atualiza README com exemplos
refactor: melhora performance do parser XML
test: adiciona testes para grupo Y
```

#### **Pull Request**

1. Certifique-se de que seu código funciona
2. Teste com diferentes XMLs do e-Social
3. Atualize a documentação se necessário
4. Faça commit das suas mudanças
5. Push para sua branch
6. Abra um Pull Request com:
   - **Título claro**
   - **Descrição detalhada** das mudanças
   - **Referência** às issues relacionadas (se houver)

---

## 🧪 Testes

Antes de enviar um PR, teste seu código:

```bash
# Teste com XMLs de exemplo
python s5002_to_pdf.py exemplos/ output/ --ano 2024

# Teste com CSV de nomes
python s5002_to_pdf.py exemplos/ output/ --ano 2024 --csv exemplo_nomes.csv
```

---

## 📚 Áreas que Precisam de Ajuda

- **Testes automatizados** - Implementar suite de testes
- **Documentação** - Melhorar exemplos e tutoriais
- **Performance** - Otimizações de velocidade
- **Novos grupos** - Suporte a grupos adicionais do e-Social
- **Validação** - Validação mais robusta de XMLs
- **Internacionalização** - Suporte a outros idiomas (se aplicável)

---

## 💬 Dúvidas?

Se tiver dúvidas sobre como contribuir:

1. Abra uma [Discussion](https://github.com/flaviowbr/esocial_s5002_comprovante_rendimentos/discussions)
2. Entre em contato através das Issues

---

## 📜 Código de Conduta

Ao contribuir, você concorda em:

- Ser respeitoso com outros contribuidores
- Aceitar feedback construtivo
- Focar no que é melhor para a comunidade
- Mostrar empatia com outros membros da comunidade

---

## 🎉 Reconhecimento

Todos os contribuidores serão reconhecidos no README do projeto!

---

**Obrigado por contribuir! 🚀**
