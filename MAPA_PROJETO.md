# Mapa do projeto GCPlanner

## 1. Visão geral

O GCPlanner é uma aplicação desktop para cadastro e acompanhamento de demandas/pagamentos. A interface é feita com **PyQt6**, os dados são persistidos em **SQLite** e a distribuição para Windows é preparada com **PyInstaller**.

As responsabilidades estão divididas em três camadas simples:

```text
main.py       -> inicialização do processo Qt e abertura da janela
gui.py        -> interface, eventos, filtros, temas e alertas
logic.py      -> operações de domínio e acesso às tabelas
database.py   -> conexão, criação e migração do banco SQLite
```

## 2. Estrutura de diretórios e arquivos

```text
Planner/
├── main.py                 # ponto de entrada recomendado
├── gui.py                  # janela principal e diálogo de edição
├── logic.py                # classes Categoria e Tarefa
├── database.py             # conexão e inicialização/migração SQLite
├── requirements.txt        # dependência Python da aplicação
├── GCPlanner.spec          # configuração do build PyInstaller
├── gcp_settings.json       # configurações persistentes da interface
├── gcp_v3_pro.db           # banco SQLite local da aplicação
├── icon.jpg                # imagem auxiliar/branding
├── icon.png                # imagem auxiliar/branding
├── icone.ico               # ícone da janela, bandeja e executável
├── icon_concluido.png      # ícone da ação concluir/reabrir
├── icon_editar.png         # ícone da ação editar
├── icon_excluir.png        # ícone da ação excluir
├── dist/                   # saída distribuível do PyInstaller
│   ├── GCPlanner.exe
│   ├── gcp_settings.json
│   └── gcp_v3_pro.db
├── build/                  # artefatos intermediários de um build
├── build_novo/             # artefatos intermediários de outro build
├── venv/                   # ambiente virtual local
└── __pycache__/            # bytecode gerado pelo Python
```

Os diretórios `build/`, `build_novo/`, `dist/`, `venv/` e `__pycache__/` são gerados ou locais ao ambiente. O código-fonte da aplicação está nos quatro arquivos Python da raiz.

## 3. Arquivos-fonte

### `main.py`

Ponto de entrada da aplicação quando executada como script ou pelo executável.

#### `main()`

- Define variáveis de ambiente para manter a escala da interface Qt em `1`, visando monitores High-DPI.
- Cria o `QApplication`.
- Define um `AppUserModelID` no Windows para que o ícone da aplicação seja tratado corretamente na barra de tarefas.
- Seleciona o estilo base `Fusion`.
- Cria `MainWindow`, abre-a maximizada e inicia o loop de eventos com `app.exec()`.

O bloco `if __name__ == "__main__"` chama `main()` quando o arquivo é executado diretamente.

### `database.py`

Responsável exclusivamente pela conexão com o SQLite e pela preparação/evolução do esquema.

#### Constante `DB_NAME`

Nome do arquivo usado pelo SQLite: `gcp_v3_pro.db`. Como o caminho é relativo, o banco é criado/aberto no diretório de trabalho atual do processo.

#### `conectar_db()`

- Abre uma conexão SQLite.
- Configura `sqlite3.Row` como `row_factory`, permitindo acessar resultados por nome de coluna e convertê-los com `dict(...)`.
- Retorna a tupla `(conn, cursor)`.

#### `iniciar_db()`

Inicializa o banco e executa migrações tolerantes a versões antigas:

- Ativa as chaves estrangeiras com `PRAGMA foreign_keys = ON`.
- Cria `categorias` e `tarefas` caso ainda não existam.
- Tenta adicionar a coluna `cor` às categorias existentes.
- Tenta adicionar os campos de negócio introduzidos posteriormente em `tarefas`: `mes_referencia`, `prestador`, `tipo_pagamento`, `financiamento` e `observacao`.
- Preenche `mes_referencia` ausente usando o mês de vencimento ou de criação.
- Migra títulos antigos que começam com `FAEC`, `MAC` ou `OPME` para os campos `financiamento` e `tipo_pagamento`; `OPME` é convertido para `MUNICIPAL`.
- Garante a existência da categoria padrão `Geral`.
- Confirma a transação e fecha a conexão.

### `logic.py`

Camada de persistência usada pela interface. As duas classes são agrupamentos de métodos estáticos; não mantêm estado de instância.

#### Classe `Categoria`

Opera a tabela `categorias`.

##### `Categoria.adicionar(nome, cor="#1f538d")`

Insere uma categoria com nome e cor. Retorna o ID gerado ou `None` se ocorrer qualquer exceção.

##### `Categoria.atualizar(categoria_id, nome, cor)`

Atualiza nome e cor da categoria identificada pelo ID.

##### `Categoria.listar()`

Retorna todas as categorias em ordem alfabética pelo nome.

##### `Categoria.obter_por_id(categoria_id)`

Retorna uma categoria pelo ID ou `None` quando não encontrada.

#### Classe `Tarefa`

Opera a tabela `tarefas` e sempre traz também o nome da categoria nas consultas de listagem.

##### `Tarefa.adicionar(...)`

Cria uma tarefa com título, vencimento, prioridade, categoria, repetição de alerta e dados administrativos. Converte `datetime` para texto no formato `YYYY-MM-DD HH:MM:SS` e calcula `mes_referencia` quando ele não é informado.

##### `Tarefa.listar_por_mes(mes_referencia, categoria_id=None)`

Lista tarefas do mês informado, opcionalmente limitadas a uma categoria. Ordena por status, vencimento e prioridade.

##### `Tarefa.listar_todas_pendentes(mes_referencia=None)`

Lista todas as tarefas pendentes para uso geral ou somente as pendentes de um mês. É a consulta usada pelo verificador de alertas.

##### `Tarefa.obter_por_id(tarefa_id)`

Busca uma tarefa específica, incluindo `categoria_nome` por meio de `JOIN`.

##### `Tarefa.atualizar(...)`

Atualiza os dados editáveis de uma tarefa: título, vencimento, prioridade, categoria, intervalo de alerta, prestador, tipo de pagamento, financiamento, mês de referência e observação.

##### `Tarefa.concluir(tarefa_id)`

Altera o status da tarefa para `Concluida`.

##### `Tarefa.excluir(tarefa_id)`

Remove permanentemente a tarefa pelo ID.

##### `Tarefa.registrar_alerta_enviado(tarefa_id, horario_str)`

Marca a tarefa como notificada e salva o horário do último alerta.

##### `Tarefa.reabrir(tarefa_id)`

Altera o status de volta para `Pendente`.

##### `Tarefa.copiar_mes_anterior(mes_atual)`

Calcula o mês anterior e copia para o mês atual as tarefas encontradas no mês anterior. Preserva os dados administrativos e evita duplicatas pelo par `titulo` + `prestador` no mês de destino. Retorna a quantidade de linhas afetadas.

### `gui.py`

Implementa a interface PyQt6, os temas visuais, as interações com `Categoria`/`Tarefa` e as notificações na bandeja do sistema.

#### Constantes e funções de módulo

##### `APP_VERSION`

Versão exibida no título da janela e usada na identificação do processo Windows: `1.0.0`.

##### `obter_caminho_recurso(nome_ficheiro)`

Resolve recursos tanto no desenvolvimento quanto no executável PyInstaller. Usa `sys._MEIPASS` quando disponível e, caso contrário, o diretório absoluto de execução.

##### `guardar_config(key, value)`

Lê `gcp_settings.json`, atualiza uma chave e grava o JSON formatado. Se o arquivo não existir ou estiver inválido, começa com uma configuração vazia.

##### `carregar_config(key, default=None)`

Lê uma configuração do JSON e retorna o valor padrão quando o arquivo não existe, está inválido ou não contém a chave.

##### `THEMES`

Dicionário com três folhas de estilo QSS: `Dark`, `Light` e `Azure`. Elas definem cores, tabelas, campos, botões, etiquetas de prioridade e lista lateral.

#### Classe `EditTaskDialog(QDialog)`

Diálogo modal para editar uma tarefa existente.

##### `__init__(parent, tarefa_id)`

Define o tamanho do diálogo, guarda o ID, carrega os dados atuais com `Tarefa.obter_por_id()` e monta os controles.

##### `setup_ui()`

Cria os campos de descrição, prestador, tipo de pagamento, financiamento, observação, mês, categoria, prioridade, vencimento e repetição do alerta. Configura os botões Salvar/Cancelar.

##### `get_values()`

Retorna uma tupla com os valores atuais dos controles, na ordem esperada por `Tarefa.atualizar()`.

#### Classe `MainWindow(QMainWindow)`

Janela principal e coordenadora do estado visual da aplicação.

##### `__init__()`

Inicializa o banco, configura título/tamanho/ícone, estado de filtros e mês atual, monta a interface, restaura o tema, prepara a bandeja do sistema e inicia um `QTimer` de 30 segundos para alertas.

##### `setup_ui()`

Monta a janela em duas áreas:

- barra lateral com categorias, filtro global e seletor de tema;
- área principal com mês, cópia do mês anterior, cadastro rápido, filtros por coluna e tabela de tarefas.

Também conecta sinais dos controles aos métodos de interação da janela.

##### `aplicar_tema(nome_tema, setup=False)`

Aplica o QSS escolhido, preserva a geometria/maximização da janela e salva o tema no JSON quando a troca não faz parte da configuração inicial.

##### `setup_tray()`

Cria o ícone na bandeja do sistema com ações para abrir a janela e sair da aplicação.

##### `closeEvent(event)`

Para o timer, esconde o ícone da bandeja e aceita o fechamento da janela.

##### `registrar_tarefa()`

Valida o título, converte o índice do seletor de repetição para minutos, grava a tarefa usando os campos do cadastro rápido, limpa os controles e atualiza a tela.

##### `obter_cor_cat(cat_id)`

Busca a cor de uma categoria pelo ID; retorna `#1f538d` como fallback.

##### `refresh_all()`

Reconstrói a lista de categorias e todas as linhas da tabela para o mês/categoria atuais. Preenche checkboxes, campos editáveis, etiquetas de categoria/prioridade, status e botões de concluir, editar e excluir.

##### `salvar_edicao_celula(item)`

Persiste alterações diretas feitas nas colunas editáveis da tabela. Ignora atualizações provocadas pela própria reconstrução da tabela e mantém os demais campos da tarefa.

##### `valor_da_coluna(tarefa, coluna)`

Converte os dados de uma tarefa para o texto exibido nas colunas usadas pelos filtros.

##### `tarefa_corresponde_a_filtros(tarefa, ignorar_coluna=None)`

Retorna se uma tarefa atende aos filtros de coluna ativos; permite ignorar uma coluna ao recalcular as opções dela.

##### `atualizar_opcoes_filtros(tarefas)`

Recalcula as opções disponíveis nos oito combos de filtro, preservando seleções ainda válidas e evitando sinais durante a reconstrução.

##### `aplicar_filtro_coluna(coluna)`

Ativa ou remove o filtro selecionado para uma coluna e atualiza a tabela.

##### `limpar_filtros()`

Remove todos os filtros de coluna e atualiza a tabela.

##### `nova_categoria()`

Solicita um nome ao usuário, cria a categoria e recarrega a interface.

##### `menu_categoria(pos)`

Abre o menu contextual de uma categoria. Permite renomear ou escolher uma nova cor com `QColorDialog`.

##### `filtrar(cid)`

Define o filtro de categoria, atualiza o título da janela e recarrega as tarefas. `None` representa a visão global.

##### `mudar_mes(data)`

Atualiza `mes_atual` para `YYYY-MM` e recarrega a lista.

##### `copiar_mes_anterior()`

Solicita ao domínio a cópia das tarefas do mês anterior, informa o total copiado e atualiza a tabela.

##### `alternar_conclusao(tid, concluida)`

Conclui ou reabre uma tarefa conforme o estado atual.

##### `marcar_concluida_direta(tid)`

Conclui diretamente uma tarefa e atualiza a tela. É um método auxiliar que atualmente não está conectado a um controle visível.

##### `deletar_tarefa_direta(tid)`

Solicita confirmação e exclui uma tarefa individual.

##### `abrir_edicao_direta(tid)`

Abre `EditTaskDialog`; se o usuário salvar, envia os valores para `Tarefa.atualizar()` e recarrega a tabela.

##### `lote_concluir()`

Percorre as tarefas marcadas e alterna o status de cada uma. É o comportamento de conclusão em lote, embora não haja atualmente um botão da UI conectado a ele.

##### `selecionar_todos()`

Marca todos os checkboxes visíveis se algum estiver desmarcado; caso contrário, desmarca todos.

##### `lote_excluir()`

Coleta as tarefas marcadas, solicita confirmação e exclui todas as selecionadas.

##### `menu_tabela(pos)`

Abre menu contextual na tabela para editar ou concluir/reabrir a tarefa da linha clicada.

##### `verificar_alertas()`

Consulta tarefas pendentes, verifica vencimento e intervalo de repetição, envia uma notificação pela bandeja e registra o horário do alerta enviado.

O bloco `if __name__ == "__main__"` de `gui.py` também consegue iniciar a janela diretamente, mas o caminho normal é executar `main.py`.

## 4. Modelo de dados SQLite

### Tabela `categorias`

| Coluna | Tipo | Função |
|---|---|---|
| `id` | INTEGER | Chave primária autoincremental. |
| `nome` | TEXT | Nome obrigatório e único. |
| `cor` | TEXT | Cor visual, padrão `#1f538d`. |

### Tabela `tarefas`

| Coluna | Tipo | Função |
|---|---|---|
| `id` | INTEGER | Chave primária autoincremental. |
| `titulo` | TEXT | Descrição obrigatória da demanda. |
| `data_criacao` | TEXT | Data/hora de criação. |
| `data_vencimento` | TEXT | Data/hora do alerta/vencimento; pode ser nula. |
| `priority` | INTEGER | Prioridade de 1 a 3: baixa, média ou alta. |
| `status` | TEXT | `Pendente` ou `Concluida`. |
| `categoria_id` | INTEGER | Referência a `categorias.id`; ao excluir a categoria, fica nulo. |
| `notificado` | INTEGER | Flag de alerta já enviado. |
| `alert_interval` | INTEGER | Repetição do alerta em minutos; zero significa aviso único. |
| `last_alerted_at` | TEXT | Horário do último alerta enviado. |
| `mes_referencia` | TEXT | Mês no formato `YYYY-MM`. |
| `prestador` | TEXT | Prestador relacionado. |
| `tipo_pagamento` | TEXT | Tipo de pagamento. |
| `financiamento` | TEXT | Origem do financiamento. |
| `observacao` | TEXT | Observações livres. |

## 5. Fluxos principais

### Inicialização

1. `main.main()` configura o ambiente Qt.
2. `QApplication` é criado.
3. `MainWindow` chama `iniciar_db()`.
4. A janela monta os controles, restaura o tema e cria o timer de alertas.
5. `refresh_all()` carrega categorias e tarefas do mês atual.

### Cadastro e edição

```text
Controles da UI -> MainWindow.registrar_tarefa()
                -> Tarefa.adicionar()
                -> conectar_db() / INSERT
                -> MainWindow.refresh_all()
```

Edição pelo diálogo e edição direta em células seguem o mesmo princípio, terminando em `Tarefa.atualizar()`.

### Alertas

O timer chama `MainWindow.verificar_alertas()` a cada 30 segundos. Para cada tarefa pendente vencida, a aplicação envia um aviso único ou um novo aviso quando o intervalo configurado expirou. Depois, grava `notificado` e `last_alerted_at`.

### Build para Windows

`GCPlanner.spec` usa `main.py` como entrada, inclui os quatro recursos de ícone necessários e gera um executável sem console chamado `GCPlanner.exe`. A saída fica em `dist/` e os intermediários em `build/` ou `build_novo/`.

## 6. Configuração e execução

Instalação da dependência:

```powershell
pip install -r requirements.txt
```

Execução pelo código-fonte:

```powershell
python main.py
```

Build conforme o arquivo de especificação:

```powershell
pyinstaller GCPlanner.spec
```

O tema escolhido é salvo em `gcp_settings.json`. O arquivo `gcp_v3_pro.db` contém os dados do usuário e deve ser tratado como estado persistente, não como código-fonte.

## 7. Observações de manutenção

- Há duas definições consecutivas de `MainWindow.filtrar`; a segunda substitui a primeira e é a que efetivamente executa. A primeira pode ser removida em uma limpeza futura.
- `marcar_concluida_direta()` e `lote_concluir()` existem, mas não estão conectados aos botões atualmente criados em `setup_ui()`.
- A maior parte do acesso a dados abre e fecha uma conexão por operação; isso simplifica o código, mas deve ser considerado se o volume de uso crescer.
- As datas são armazenadas como texto e dependem do formato `YYYY-MM-DD HH:MM:SS`, usado tanto nas consultas quanto nos alertas.
- `Categoria.adicionar()` e alguns blocos da UI usam tratamento amplo de exceções; diagnósticos futuros serão mais fáceis com exceções específicas e mensagens de erro.
- `Tarefa.listar_por_mes()`, `listar_todas_pendentes()` e `obter_por_id()` usam `JOIN` interno com categorias. Uma tarefa com `categoria_id` nulo após a exclusão da categoria não aparecerá nessas consultas até que o relacionamento seja corrigido.
