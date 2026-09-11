# SCP Planner — Publicação (GitHub Pages) e Dados (Firebase)

- **Site**: hospedado no GitHub Pages a partir da pasta `public/` do repositório
  `regulacaoeinformatizacaosus-coder/SCP-Planner`.
  Endereço: **https://regulacaoeinformatizacaosus-coder.github.io/SCP-Planner/**
- **Dados**: Cloud Firestore do projeto Firebase **`scp-planner-528ed`**, coleção `processos_scp`.
  Todos que abrirem o site veem as alterações em tempo real.

Sem a configuração do Firebase, o site funciona em modo "Só neste navegador" (dados no `localStorage`).

---

## 1. Conectar o site ao Firebase

1. Firebase Console › projeto `scp-planner-528ed` › ⚙️ **Configurações do projeto** › aba **Geral**.
2. Em **Seus aplicativos**, clique no ícone **Web `</>`** (se ainda não houver app web), dê o nome `SCP Web` e registre.
   **Não** precisa marcar "Firebase Hosting".
3. Copie os valores do objeto `firebaseConfig` para `public/firebase-config.js`.
4. Faça commit e push — o site publicado passa a usar o Firestore para todos.

> A `apiKey` do Firebase Web não é uma senha: ela só identifica o projeto e pode ficar no repositório.
> Quem controla o acesso aos dados são as **regras do Firestore** (passo 3).

## 2. Publicação automática no GitHub Pages

O workflow `.github/workflows/pages.yml` publica a pasta `public/` a cada push na branch `main`
que altere algo em `public/`.

Configuração única no GitHub (precisa ser administrador do repositório):
**Settings › Pages › Build and deployment › Source: GitHub Actions**.

Depois de ativar, rode o workflow uma vez em **Actions › Publicar site (GitHub Pages) › Run workflow**.

## 3. Regras de segurança do Firestore

O arquivo `firestore.rules` define quem pode ler e gravar. Para publicar as regras, use o Console
(Firestore Database › **Regras** › colar o conteúdo › Publicar).

⚠️ As regras atuais permitem que **qualquer pessoa com o link** leia, altere e apague os processos.
Como o site é público, o recomendado é adicionar login (ex: Google) e liberar só os e-mails do setor.

## 4. Rodar localmente

Dê dois cliques em `iniciar_local.bat` (precisa do Python) e acesse http://localhost:5000.
