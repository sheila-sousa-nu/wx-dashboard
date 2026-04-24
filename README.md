# 📊 WX Dashboard – Eventos & CSAT

Dashboard interativo de eventos e satisfação dos escritórios Nubank.
**Acesso:** [sua-url.github.io/wx-dashboard](https://seuusuario.github.io/wx-dashboard)

---

## 🗂 Estrutura do Repositório

```
wx-dashboard/
├── index.html            ← dashboard (não precisa editar)
├── data.json             ← dados (gerado pelo script abaixo)
├── update_dashboard.py   ← script de atualização
├── data/                 ← coloque aqui os arquivos Excel
│   ├── eventos.xlsx
│   └── csat.xlsx
└── README.md
```

---

## 🚀 Como Publicar no GitHub (primeira vez)

### 1. Crie o repositório
1. Acesse [github.com/new](https://github.com/new)
2. Nome: `wx-dashboard`
3. Visibilidade: **Public** (obrigatório para GitHub Pages gratuito)
4. Clique em **Create repository**

### 2. Suba os arquivos
Você pode fazer isso de duas formas:

**Opção A – Interface do GitHub (mais simples):**
1. Na página do repositório, clique em **uploading an existing file**
2. Arraste todos os arquivos desta pasta (`index.html`, `data.json`, `update_dashboard.py`, `README.md`)
3. Clique em **Commit changes**

**Opção B – Terminal (Git):**
```bash
cd wx-dashboard
git init
git add .
git commit -m "feat: dashboard inicial WX"
git branch -M main
git remote add origin https://github.com/SEU-USUARIO/wx-dashboard.git
git push -u origin main
```

### 3. Ative o GitHub Pages
1. No repositório, vá em **Settings → Pages**
2. Em "Branch", selecione `main` e pasta `/ (root)`
3. Clique em **Save**
4. Aguarde ~1 minuto → sua URL estará disponível em:
   `https://SEU-USUARIO.github.io/wx-dashboard`

---

## 🔄 Como Atualizar os Dados

Sempre que tiver novos relatórios Excel:

### Passo 1 – Coloque os arquivos na pasta `data/`
- Arquivo de eventos → `data/eventos.xlsx`
- Arquivo de CSAT → `data/csat.xlsx`

> Os nomes não precisam ser exatos. O script procura por palavras-chave no nome do arquivo.
> **Eventos:** qualquer arquivo com "evento", "event" ou "wx" no nome
> **CSAT:** qualquer arquivo com "csat", "satisfa", "relatorio" ou "relatrio" no nome

### Passo 2 – Execute o script
```bash
# Instalar dependências (só na primeira vez)
pip install pandas openpyxl

# Atualizar dados
python update_dashboard.py
```

O script vai gerar um `data.json` atualizado.

### Passo 3 – Faça upload do novo `data.json` no GitHub
**Opção A – Interface do GitHub:**
1. Clique em `data.json` no repositório
2. Clique no ícone de lápis (editar)
3. Clique em **...** → **Upload file** ou arraste o novo `data.json`
4. Commit → dashboard atualiza em ~1 minuto

**Opção B – Terminal:**
```bash
git add data.json
git commit -m "chore: atualiza dados $(date '+%d/%m/%Y')"
git push
```

---

## 📌 Métricas do Dashboard

| Aba | Métricas |
|-----|----------|
| **Visão Geral** | Total de eventos, concluídos, cancelados, externos; evolução mensal; status; top BUs |
| **Brasil · Detalhes** | Eventos por HQ (HQ1, HQ2, HQ3, Spark, Casinha); evolução por escritório; média de pessoas |
| **Dias & Horários** | Dias da semana mais movimentados; horários de início; sazonalidade mensal |
| **Pessoas & Impacto** | Média/mediana de participantes; distribuição por tamanho; externos por ano |
| **CSAT** | Distribuição de avaliações; nota por dimensão (espaço, catering, A/V); tendência mensal |

---

## 🔒 Quer acesso restrito?

O GitHub Pages em repositório **público** é acessível por qualquer pessoa com o link.

Para acesso privado, as opções são:
- **GitHub Pro/Enterprise** → permite Pages em repos privados
- **Netlify** (gratuito) → com senha de acesso
- **Compartilhar o arquivo `index.html` + `data.json`** diretamente por Drive/email

---

## 🛠 Suporte

Dúvidas? Entre em contato com quem configurou o dashboard ou abra uma issue no repositório.
