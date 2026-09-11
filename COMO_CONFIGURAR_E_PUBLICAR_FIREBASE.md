# SCP Planner — Publicação (GitHub Pages) e Dados (Firebase)

- **Site**: GitHub Pages, publicado a partir da pasta `public/` do repositório
  `regulacaoeinformatizacaosus-coder/SCP-Planner`.
  Endereço: **https://regulacaoeinformatizacaosus-coder.github.io/SCP-Planner/**
- **Dados**: Cloud Firestore do projeto Firebase **`scp-planner-528ed`**, coleção `processos_scp`.
- **Acesso**: login com Google. Só entram os e-mails cadastrados na coleção `autorizados`.

Sem a configuração do Firebase, o site funciona em modo "Só neste navegador" (sem login, dados no `localStorage`).

---

## 1. Ativar o login com Google

1. Firebase Console › **Authentication** › **Primeiros passos** (se ainda não ativou).
2. Aba **Método de login** › **Google** › **Ativar** › escolha o e-mail de suporte › **Salvar**.
3. Aba **Configurações** › **Domínios autorizados** › **Adicionar domínio**:
   `regulacaoeinformatizacaosus-coder.github.io`
   (`localhost` já vem liberado para testes locais).

## 2. Liberar quem pode acessar

Firestore Database › **Dados** › **Iniciar coleção**:

- ID da coleção: `autorizados`
- ID do documento: o e-mail da pessoa **em letras minúsculas** (ex: `fulano@gmail.com`)
- Campo: `nome` (string) com o nome da pessoa

Repita "Adicionar documento" para cada pessoa do setor. Para tirar o acesso, exclua o documento.

## 3. Publicar as regras de segurança

Firestore Database › **Regras** › apague tudo › cole o conteúdo de `firestore.rules` › **Publicar**.

As regras garantem que:
- só usuários logados com e-mail cadastrado em `autorizados` leem ou alteram processos;
- ninguém consegue alterar a lista `autorizados` pelo site (apenas pelo Console);
- os campos gravados têm formato válido (status, urgência, tamanhos) e registram quem criou/alterou.

## 4. Conectar o site ao Firebase

1. Firebase Console › ⚙️ **Configurações do projeto** › **Geral** › **Seus aplicativos**.
2. Se não houver app Web, clique em **`</>`**, nome `SCP Web`, **Registrar app** (não precisa de Hosting).
3. Copie os valores do `firebaseConfig` para `public/firebase-config.js`, faça commit e push.

> A `apiKey` do Firebase Web não é senha — pode ficar no repositório. Quem protege os dados são o login e as regras.

## 5. Publicação automática (GitHub Pages)

O workflow `.github/workflows/pages.yml` publica a pasta `public/` a cada push na branch `main`
que altere algo em `public/`. Também pode ser disparado em **Actions › Publicar site (GitHub Pages) › Run workflow**.

Configuração única (já feita): **Settings › Pages › Source: GitHub Actions**.

## 6. Rodar localmente

Dê dois cliques em `iniciar_local.bat` (precisa do Python) e acesse http://localhost:5000.
