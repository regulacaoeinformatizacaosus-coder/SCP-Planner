import { firebaseConfig as defaultConfigFile } from './firebase-config.js';

const FIREBASE_SDK = 'https://www.gstatic.com/firebasejs/10.13.0';
const COLECAO_AUTORIZADOS = 'autorizados';
const CHAVE_CONFIG = 'scp_firebase_config';
const CHAVE_NUCLEO = 'scp_nucleo';

// Núcleos do setor: cada um com a sua coleção no Firestore
const NUCLEOS = {
  scp: {
    rotulo: 'SCP',
    nome: 'Setor de Comandos de Pagamento',
    colecao: 'processos_scp',
    chaveLocal: 'scp_local_processos_v2',
    equipe: ['Alzira', 'Camila', 'Cássio', 'Leonardo', 'Lucas', 'Tito', 'Comissão', 'Laboratórios'],
    temQuadro: true
  },
  pd: {
    rotulo: 'Processamento de Dados',
    nome: 'Processamento de Dados',
    colecao: 'processos_pd',
    chaveLocal: 'scp_local_processos_pd',
    equipe: [],
    temQuadro: false
  }
};

const URGENCIAS = {
  Critica: { label: 'Crítica', peso: 4 },
  Alta: { label: 'Alta', peso: 3 },
  Media: { label: 'Média', peso: 2 },
  Baixa: { label: 'Baixa', peso: 1 }
};

const STATUS = {
  'Pendente': 'Pendente',
  'Em Andamento': 'Em andamento',
  'Aguardando': 'Aguardando',
  'Concluido': 'Concluído'
};

// ============================================================================
// PROCESSOS DO QUADRO BRANCO DO SETOR (transcritos na ordem do quadro)
// ============================================================================
function processosDoQuadro() {
  const base = Date.now();
  const lista = [
    {
      descricao: 'Lei 5984 de 15/05/26',
      quem: 'Lucas',
      status: 'Aguardando',
      progresso: 'Justificativa entregue p/ Lucas em 10/09'
    },
    {
      descricao: 'Nota Técnica Res. 11212 e 11010 (Opera Mais)',
      quem: 'Tito',
      status: 'Aguardando',
      progresso: 'Aguardando publicação'
    },
    {
      descricao: 'Anexo III - Metas Hosp. e Sistema de Pagamento',
      quem: 'Comissão',
      status: 'Aguardando',
      progresso: 'Disponibilizada p/ Comissão em 11/09'
    },
    {
      descricao: 'POA Otorrino Center',
      quem: 'Alzira e Cássio',
      status: 'Em Andamento',
      progresso: 'Iniciando análise p/ repassar p/ Comissão'
    },
    {
      descricao: 'Análise Portaria 12.116/Agosto 2026 - Tab Dif',
      quem: 'Laboratórios',
      status: 'Pendente',
      progresso: 'Pendência: Laboratórios'
    },
    {
      descricao: 'Acompanhamento Edital 08/2026 p/ confecção dos POAs',
      quem: 'Camila e Leonardo',
      status: 'Em Andamento',
      progresso: ''
    },
    {
      descricao: 'Acompanhar no 1DOC: Processos Contratos Novos Ed. 04/2025',
      quem: '',
      status: 'Em Andamento',
      progresso: '',
      itens: ['AT-33.826', 'SC-34.374 e 33.826', 'DG-34.146', 'HU-30.297', 'HC-30.979']
        .map(texto => ({ texto, feito: false }))
    }
  ];

  return lista.map((p, i) => ({
    id: `quadro_${i + 1}`,
    urgencia: 'Media',
    obs: '',
    itens: [],
    ...p,
    criadoEm: base + i
  }));
}

// ============================================================================
// ESTADO
// ============================================================================
let db = null;
let fs = null;
let auth = null;
let authApi = null;
let usuario = null;
let firestoreUnsubscribe = null;
let authUnsubscribe = null;
let processos = [];
let modo = 'carregando'; // 'carregando' | 'firebase' | 'local'
let filtroRapido = 'todos';
let ultimaListaPessoas = '';
let edicaoAtiva = false;
let seletorModal = null;
let acessoLiberado = false;
let nucleo = lerNucleoSalvo();

const $ = (id) => document.getElementById(id);

const processList = $('processList');
const emptyState = $('emptyState');
const resultCount = $('resultCount');

const demandaModal = $('demandaModal');
const demandaForm = $('demandaForm');
const modalTitle = $('modalTitle');
const formDemandaId = $('formDemandaId');
const inputDescricao = $('inputDescricao');
const seletorQuem = $('seletorQuem');
const inputUrgencia = $('inputUrgencia');
const inputStatus = $('inputStatus');
const inputProgresso = $('inputProgresso');
const inputItens = $('inputItens');
const inputObs = $('inputObs');
const btnSaveModal = $('btnSaveModal');

const searchInput = $('searchInput');
const filterQuem = $('filterQuem');
const filterUrgencia = $('filterUrgencia');
const filterStatus = $('filterStatus');
const btnLimparFiltros = $('btnLimparFiltros');

const connectionStatus = $('connectionStatus');
const statusText = $('statusText');
const firebaseModal = $('firebaseModal');
const inputFirebaseConfig = $('inputFirebaseConfig');

// ============================================================================
// UTILITÁRIOS
// ============================================================================
function nucleoAtual() {
  return NUCLEOS[nucleo];
}

function lerNucleoSalvo() {
  try {
    const salvo = localStorage.getItem(CHAVE_NUCLEO);
    if (salvo in NUCLEOS) return salvo;
  } catch {
    // navegador sem localStorage: usa o padrão
  }
  return 'scp';
}

function escapeHtml(valor) {
  return String(valor ?? '').replace(/[&<>'"]/g,
    c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[c])
  );
}

function normalizar(texto) {
  return String(texto ?? '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().trim();
}

function normalizarUrgencia(valor) {
  return Object.keys(URGENCIAS).find(k => normalizar(k) === normalizar(valor)) || 'Media';
}

function normalizarStatus(valor) {
  return Object.keys(STATUS).find(k => normalizar(k) === normalizar(valor)) || 'Pendente';
}

function paraMillis(valor) {
  if (!valor) return 0;
  if (typeof valor === 'number') return valor;
  if (typeof valor.toMillis === 'function') return valor.toMillis();
  if (typeof valor.seconds === 'number') return valor.seconds * 1000;
  return 0;
}

function formatarData(ms) {
  const d = new Date(ms);
  const data = d.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' });
  const hora = d.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
  return `${data} às ${hora}`;
}

// "Alzira e Cássio", "Cássio / SCP", "Ana, Beto" -> lista de nomes
function pessoasDe(quem) {
  return String(quem ?? '')
    .split(/\s*(?:\/|,|;|&|\+|\s+e\s+)\s*/i)
    .map(s => s.trim())
    .filter(Boolean);
}

function iniciais(nome) {
  const partes = nome.trim().split(/\s+/);
  if (partes.length === 1) return partes[0].substring(0, 2).toUpperCase();
  return (partes[0][0] + partes[partes.length - 1][0]).toUpperCase();
}

function itensDe(processo) {
  return Array.isArray(processo.itens) ? processo.itens : [];
}

function estaConcluido(p) {
  return normalizarStatus(p.status) === 'Concluido';
}

function eUrgente(p) {
  const u = normalizarUrgencia(p.urgencia);
  return (u === 'Alta' || u === 'Critica') && !estaConcluido(p);
}

function showToast(mensagem, tipo = 'info') {
  const toast = document.createElement('div');
  toast.className = `toast toast-${tipo}`;
  toast.textContent = mensagem;
  $('toastContainer').appendChild(toast);
  setTimeout(() => {
    toast.classList.add('saindo');
    setTimeout(() => toast.remove(), 250);
  }, 3500);
}

// ============================================================================
// TELAS: LISTA DE PROCESSOS OU LOGIN / ACESSO NEGADO / ERRO
// ============================================================================
function mostrarLista() {
  $('authGate').hidden = true;
  $('appContent').hidden = false;
  document.body.classList.remove('bloqueado');
}

function mostrarPortao(tela, texto = '') {
  const email = usuario?.email || '';
  const telas = {
    login: {
      titulo: 'Entrar no SCP Planner',
      texto: 'Use a sua conta Google liberada pelo setor para ver e editar os processos.',
      botoes: ['btnEntrarGoogle']
    },
    negado: {
      titulo: 'Acesso ainda não liberado',
      texto: `Você entrou como ${email}, mas essa conta não está liberada. No Firebase (projeto ${db?.app?.options?.projectId || '?'}), a coleção "autorizados" precisa ter um documento com o ID exatamente igual a: ${email.toLowerCase()}`,
      botoes: ['btnTentarNovamente', 'btnTrocarConta']
    },
    erro: {
      titulo: 'Não foi possível conectar',
      texto: texto || 'Verifique sua conexão com a internet e tente novamente.',
      botoes: usuario ? ['btnTentarNovamente', 'btnTrocarConta'] : ['btnEntrarGoogle', 'btnTentarNovamente']
    }
  }[tela];

  $('gateTitulo').textContent = telas.titulo;
  $('gateTexto').textContent = telas.texto;
  ['btnEntrarGoogle', 'btnTentarNovamente', 'btnTrocarConta'].forEach(id => {
    $(id).hidden = !telas.botoes.includes(id);
  });

  $('appContent').hidden = true;
  $('authGate').hidden = false;
  document.body.classList.add('bloqueado');
}

function atualizarUsuarioNoHeader() {
  const btn = $('btnUsuario');
  btn.hidden = !usuario;
  if (!usuario) return;

  const nome = usuario.displayName || usuario.email;
  $('userEmail').textContent = usuario.email;
  btn.title = `Conectado como ${usuario.email}. Clique para sair.`;

  const avatar = $('userAvatar');
  avatar.textContent = '';
  if (usuario.photoURL) {
    const img = document.createElement('img');
    img.src = usuario.photoURL;
    img.alt = '';
    img.referrerPolicy = 'no-referrer';
    img.onerror = () => { avatar.textContent = iniciais(nome); };
    avatar.appendChild(img);
  } else {
    avatar.textContent = iniciais(nome);
  }
}

// ============================================================================
// CONEXÃO: FIREBASE (LOGIN + TEMPO REAL) OU LOCAL (NAVEGADOR)
// ============================================================================
function definirStatusConexao(estado, texto, titulo = '') {
  connectionStatus.className = `status-pill ${estado}`;
  statusText.textContent = texto;
  connectionStatus.title = titulo || texto;
}

function lerConfigFirebase(texto) {
  const inicio = texto.indexOf('{');
  const fim = texto.lastIndexOf('}');
  if (inicio === -1 || fim <= inicio) return null;
  const trecho = texto.slice(inicio, fim + 1);
  try {
    return JSON.parse(trecho);
  } catch {
    try {
      return new Function(`return (${trecho});`)();
    } catch {
      return null;
    }
  }
}

function configValida(config) {
  return Boolean(config && config.apiKey && config.projectId && config.apiKey !== 'SUA_API_KEY_AQUI');
}

// A configuração do arquivo (compartilhada por todos) sempre tem prioridade;
// a salva no navegador só vale quando o arquivo não está configurado.
function obterConfigAtiva() {
  if (configValida(defaultConfigFile)) return defaultConfigFile;
  try {
    const salva = JSON.parse(localStorage.getItem(CHAVE_CONFIG) || 'null');
    if (configValida(salva)) return salva;
  } catch (e) {
    console.warn('Configuração do Firebase salva é inválida:', e);
  }
  return null;
}

function pararSincronizacao() {
  if (firestoreUnsubscribe) {
    firestoreUnsubscribe();
    firestoreUnsubscribe = null;
  }
}

function pararAutenticacao() {
  if (authUnsubscribe) {
    authUnsubscribe();
    authUnsubscribe = null;
  }
}

async function initFirebase() {
  const config = obterConfigAtiva();
  if (!config) {
    ativarModoLocal();
    return;
  }

  pararSincronizacao();
  pararAutenticacao();
  modo = 'carregando';
  definirStatusConexao('connecting', 'Conectando...');
  mostrarLista();
  render();

  try {
    const { initializeApp, getApps } = await import(`${FIREBASE_SDK}/firebase-app.js`);
    [fs, authApi] = await Promise.all([
      import(`${FIREBASE_SDK}/firebase-firestore.js`),
      import(`${FIREBASE_SDK}/firebase-auth.js`)
    ]);

    const nomeApp = `scp-${config.projectId}-${config.apiKey.slice(-6)}`;
    const app = getApps().find(a => a.name === nomeApp) || initializeApp(config, nomeApp);
    db = fs.getFirestore(app);
    auth = authApi.getAuth(app);
    authApi.useDeviceLanguage(auth);

    authUnsubscribe = authApi.onAuthStateChanged(auth, aoMudarUsuario);
  } catch (err) {
    console.error('Falha ao inicializar o Firebase:', err);
    definirStatusConexao('offline', 'Desconectado');
    mostrarPortao('erro', 'Não foi possível carregar o Firebase. Verifique sua conexão e tente novamente.');
  }
}

async function aoMudarUsuario(user) {
  pararSincronizacao();
  usuario = user;
  acessoLiberado = false;
  processos = [];
  atualizarUsuarioNoHeader();

  if (!user) {
    modo = 'carregando';
    definirStatusConexao('offline', 'Não conectado');
    mostrarPortao('login');
    return;
  }

  modo = 'carregando';
  definirStatusConexao('connecting', 'Conectando...');
  mostrarLista();
  render();

  try {
    const liberado = await fs.getDoc(fs.doc(db, COLECAO_AUTORIZADOS, user.email.toLowerCase()));
    if (usuario !== user) return;
    if (!liberado.exists()) {
      definirStatusConexao('offline', 'Sem acesso');
      mostrarPortao('negado');
      return;
    }
  } catch (err) {
    console.error('Erro ao verificar acesso:', err);
    if (usuario !== user) return;
    definirStatusConexao('offline', 'Sem acesso');
    mostrarPortao('erro', `Não foi possível verificar o acesso de ${user.email}. Código: ${err.code || err.message}`);
    return;
  }

  acessoLiberado = true;
  assinarProcessos();
}

// Escuta em tempo real a coleção do núcleo selecionado
function assinarProcessos() {
  pararSincronizacao();
  processos = [];
  modo = 'carregando';
  definirStatusConexao('connecting', 'Conectando...');
  mostrarLista();
  render();

  const { colecao, nome } = nucleoAtual();
  firestoreUnsubscribe = fs.onSnapshot(fs.collection(db, colecao), (snapshot) => {
    processos = snapshot.docs.map(d => ({ ...d.data({ serverTimestamps: 'estimate' }), id: d.id }));
    modo = 'firebase';
    definirStatusConexao('online', 'Online', `Sincronizado com o Firestore (${db.app.options.projectId} / ${colecao})`);
    render();
  }, (error) => {
    console.error('Erro no Firestore:', error);
    pararSincronizacao();
    definirStatusConexao('offline', 'Desconectado');
    mostrarPortao('erro', (error.code === 'permission-denied'
      ? `Sua conta não tem permissão para acessar os processos de ${nome}.`
      : 'A conexão com o banco de dados foi perdida.') + ` Código: ${error.code || error.message}`);
  });
}

async function entrarComGoogle() {
  const provider = new authApi.GoogleAuthProvider();
  provider.setCustomParameters({ prompt: 'select_account' });
  try {
    await authApi.signInWithPopup(auth, provider);
  } catch (err) {
    console.error('Erro no login:', err);
    const mensagens = {
      'auth/popup-closed-by-user': null,
      'auth/cancelled-popup-request': null,
      'auth/unauthorized-domain': 'Este endereço não está nos "Domínios autorizados" do Firebase Authentication.',
      'auth/operation-not-allowed': 'O login com Google não está ativado no Firebase Authentication.',
      'auth/network-request-failed': 'Sem conexão com a internet.'
    };
    if (err.code === 'auth/popup-blocked') {
      await authApi.signInWithRedirect(auth, provider);
      return;
    }
    const mensagem = err.code in mensagens ? mensagens[err.code] : 'Não foi possível entrar com o Google.';
    if (mensagem) mostrarPortao('erro', `${mensagem} Código: ${err.code || err.message}`);
  }
}

async function sair() {
  if (!auth) return;
  await authApi.signOut(auth);
}

function ativarModoLocal() {
  pararSincronizacao();
  pararAutenticacao();
  db = null;
  usuario = null;
  modo = 'local';
  atualizarUsuarioNoHeader();
  mostrarLista();
  definirStatusConexao('offline', 'Só neste navegador', 'Os dados estão salvos apenas neste navegador. Configure o Firebase para compartilhar com o setor.');

  let salvos = null;
  try {
    salvos = JSON.parse(localStorage.getItem(nucleoAtual().chaveLocal) || 'null');
  } catch (e) {
    console.warn('Dados locais inválidos:', e);
  }

  if (Array.isArray(salvos)) {
    processos = salvos.map((p, i) => ({ ...p, id: p.id || `local_${Date.now()}_${i}` }));
  } else {
    processos = nucleoAtual().temQuadro ? processosDoQuadro() : [];
    salvarLocalmente();
  }
  render();
}

function salvarLocalmente() {
  try {
    localStorage.setItem(nucleoAtual().chaveLocal, JSON.stringify(processos));
  } catch (e) {
    console.error('Falha ao salvar localmente:', e);
    showToast('Não foi possível salvar neste navegador.', 'error');
  }
}

// ============================================================================
// GRAVAÇÃO
// ============================================================================
async function criarProcesso(dados) {
  if (modo === 'firebase') {
    await fs.addDoc(fs.collection(db, nucleoAtual().colecao), {
      ...dados,
      criadoEm: fs.serverTimestamp(),
      criadoPor: usuario.email
    });
    return;
  }
  processos.push({ ...dados, id: `local_${Date.now()}`, criadoEm: Date.now() });
  salvarLocalmente();
  render();
}

async function atualizarProcesso(id, dados) {
  if (modo === 'firebase') {
    await fs.updateDoc(fs.doc(db, nucleoAtual().colecao, id), {
      ...dados,
      atualizadoEm: fs.serverTimestamp(),
      atualizadoPor: usuario.email
    });
    return;
  }
  const item = processos.find(p => p.id === id);
  if (!item) return;
  Object.assign(item, dados, { atualizadoEm: Date.now() });
  salvarLocalmente();
  render();
}

async function removerProcesso(id) {
  if (modo === 'firebase') {
    await fs.deleteDoc(fs.doc(db, nucleoAtual().colecao, id));
    return;
  }
  processos = processos.filter(p => p.id !== id);
  salvarLocalmente();
  render();
}

async function tentar(acao, mensagemErro) {
  try {
    await acao();
    return true;
  } catch (err) {
    console.error(err);
    showToast(err.code === 'permission-denied' ? 'Sem permissão para esta alteração.' : mensagemErro, 'error');
    return false;
  }
}

async function carregarProcessosDoQuadro() {
  const lista = processosDoQuadro();
  const ok = await tentar(async () => {
    if (modo === 'firebase') {
      // Um por vez, para manter a ordem do quadro
      for (const { id, criadoEm, ...dados } of lista) {
        await criarProcesso(dados);
      }
    } else {
      processos = lista;
      salvarLocalmente();
      render();
    }
  }, 'Erro ao carregar os processos do quadro.');
  if (ok) showToast('Processos do quadro carregados.', 'success');
}

// ============================================================================
// FILTROS E ORDENAÇÃO
// ============================================================================
function passaFiltros(p) {
  const termo = normalizar(searchInput.value);
  if (termo) {
    const texto = normalizar([p.descricao, p.quem, p.progresso, p.obs, ...itensDe(p).map(i => i.texto)].join(' '));
    // Protocolos: "33826" também encontra "33.826"
    const semPontos = (s) => s.replace(/\./g, '');
    if (!texto.includes(termo) && !semPontos(texto).includes(semPontos(termo))) return false;
  }
  if (filterQuem.value && !pessoasDe(p.quem).some(n => normalizar(n) === normalizar(filterQuem.value))) return false;
  if (filterUrgencia.value && normalizarUrgencia(p.urgencia) !== filterUrgencia.value) return false;
  if (filterStatus.value && normalizarStatus(p.status) !== filterStatus.value) return false;

  if (filtroRapido === 'abertos' && estaConcluido(p)) return false;
  if (filtroRapido === 'urgentes' && !eUrgente(p)) return false;
  if (filtroRapido === 'concluidos' && !estaConcluido(p)) return false;
  return true;
}

function temFiltroAtivo() {
  return Boolean(searchInput.value.trim() || filterQuem.value || filterUrgencia.value || filterStatus.value || filtroRapido !== 'todos');
}

// Em aberto primeiro, depois urgência, depois ordem de cadastro (como no quadro)
function compararProcessos(a, b) {
  const concluidoA = estaConcluido(a);
  const concluidoB = estaConcluido(b);
  if (concluidoA !== concluidoB) return concluidoA ? 1 : -1;
  const peso = URGENCIAS[normalizarUrgencia(b.urgencia)].peso - URGENCIAS[normalizarUrgencia(a.urgencia)].peso;
  if (peso) return peso;
  return paraMillis(a.criadoEm) - paraMillis(b.criadoEm);
}

function limparFiltros() {
  searchInput.value = '';
  filterQuem.value = '';
  filterUrgencia.value = '';
  filterStatus.value = '';
  filtroRapido = 'todos';
  render();
}

// ============================================================================
// RENDERIZAÇÃO
// ============================================================================
function nomesConhecidos(extras = []) {
  const porChave = new Map();
  [...processos.flatMap(p => pessoasDe(p.quem)), ...nucleoAtual().equipe, ...extras].forEach(nome => {
    const chave = normalizar(nome);
    if (!porChave.has(chave)) porChave.set(chave, nome);
  });
  return [...porChave.values()].sort((a, b) => a.localeCompare(b, 'pt-BR'));
}

function atualizarListasDePessoas() {
  const nomes = nomesConhecidos();
  const assinatura = nomes.join('|');
  if (assinatura === ultimaListaPessoas) return;
  ultimaListaPessoas = assinatura;

  const selecionado = filterQuem.value;
  filterQuem.innerHTML = '<option value="">Quem: todos</option>' +
    nomes.map(n => `<option value="${escapeHtml(n)}">${escapeHtml(n)}</option>`).join('');
  filterQuem.value = nomes.includes(selecionado) ? selecionado : '';
}

// ["Alzira", "Cássio", "Tito"] -> "Alzira, Cássio e Tito"
function formatarPessoas(nomes) {
  if (nomes.length <= 1) return nomes.join('');
  return `${nomes.slice(0, -1).join(', ')} e ${nomes[nomes.length - 1]}`;
}

// Pessoas para marcar/desmarcar (uma ou mais), com campo para incluir alguém novo
function montarSeletorPessoas(container, nomesIniciais) {
  let selecionados = [...nomesIniciais];
  const marcado = (nome) => selecionados.some(s => normalizar(s) === normalizar(nome));

  container.innerHTML = `
    <div class="people-options"></div>
    <div class="people-add">
      <input type="text" placeholder="Incluir outra pessoa..." maxlength="60" autocomplete="off" aria-label="Nome de outra pessoa">
      <button type="button" class="btn btn-secondary">Incluir</button>
    </div>`;
  const opcoes = container.querySelector('.people-options');
  const campo = container.querySelector('input');

  const desenhar = () => {
    opcoes.innerHTML = nomesConhecidos(selecionados).map(n => `
      <button type="button" class="person-option" data-nome="${escapeHtml(n)}" aria-pressed="${marcado(n)}">
        <span class="avatar">${escapeHtml(iniciais(n))}</span>${escapeHtml(n)}
      </button>`).join('');
  };

  const incluir = () => {
    pessoasDe(campo.value).forEach(n => {
      if (!marcado(n)) selecionados.push(n);
    });
    campo.value = '';
    desenhar();
  };

  opcoes.addEventListener('click', (e) => {
    const botao = e.target.closest('.person-option');
    if (!botao) return;
    const nome = botao.dataset.nome;
    const estava = marcado(nome);
    selecionados = estava
      ? selecionados.filter(s => normalizar(s) !== normalizar(nome))
      : [...selecionados, nome];
    botao.setAttribute('aria-pressed', String(!estava));
  });
  container.querySelector('.people-add button').addEventListener('click', () => {
    incluir();
    campo.focus();
  });
  campo.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      incluir();
    }
  });

  desenhar();
  return {
    // Considera também um nome digitado e ainda não incluído
    valor: () => {
      if (campo.value.trim()) incluir();
      return formatarPessoas(selecionados);
    }
  };
}

function atualizarKpis() {
  $('kpiTotal').textContent = processos.length;
  $('kpiAbertos').textContent = processos.filter(p => !estaConcluido(p)).length;
  $('kpiUrgentes').textContent = processos.filter(eUrgente).length;
  $('kpiConcluidos').textContent = processos.filter(estaConcluido).length;

  document.querySelectorAll('.kpi-card').forEach(card => {
    const ativo = card.dataset.filtro === filtroRapido;
    card.classList.toggle('active', ativo);
    card.setAttribute('aria-pressed', String(ativo));
  });
}

const ICONES = {
  check: '<svg viewBox="0 0 24 24" aria-hidden="true"><polyline points="20 6 9 17 4 12"></polyline></svg>',
  reabrir: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M1 4v6h6"></path><path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"></path></svg>',
  editar: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 20h9"></path><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4 12.5-12.5z"></path></svg>',
  excluir: '<svg viewBox="0 0 24 24" aria-hidden="true"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>'
};

function htmlProcesso(p) {
  const concluido = estaConcluido(p);
  const urgencia = normalizarUrgencia(p.urgencia);
  const status = normalizarStatus(p.status);
  const pessoas = pessoasDe(p.quem);
  const itens = itensDe(p);
  const feitos = itens.filter(i => i.feito).length;
  const atualizado = paraMillis(p.atualizadoEm);
  const atualizadoPor = p.atualizadoPor ? ` por ${String(p.atualizadoPor).split('@')[0]}` : '';

  const htmlItens = itens.length ? `
    <div class="checklist">
      <div class="checklist-head">
        <span>Itens</span>
        <span class="checklist-count">${feitos}/${itens.length}</span>
        <span class="checklist-bar"><span style="width:${Math.round(feitos / itens.length * 100)}%"></span></span>
      </div>
      <ul>
        ${itens.map((item, i) => `
          <li class="${item.feito ? 'feito' : ''}">
            <label>
              <input type="checkbox" data-acao="item" data-index="${i}" ${item.feito ? 'checked' : ''}>
              <span>${escapeHtml(item.texto)}</span>
            </label>
          </li>`).join('')}
      </ul>
    </div>` : '';

  return `
    <li class="process urg-${urgencia.toLowerCase()} ${concluido ? 'is-done' : ''}" data-id="${escapeHtml(p.id)}">
      <div class="process-main">
        <h3 class="process-title">${escapeHtml(p.descricao)}</h3>
        ${htmlItens}
        ${p.obs ? `<p class="process-obs">${escapeHtml(p.obs)}</p>` : ''}
      </div>

      <div class="process-quem">
        <button type="button" class="quem-cell" data-acao="quem" title="Clique para marcar quem é responsável">
          ${pessoas.length
            ? pessoas.map(n => `<span class="person"><span class="avatar">${escapeHtml(iniciais(n))}</span>${escapeHtml(n)}</span>`).join('')
            : '<span class="person person-empty">+ Definir</span>'}
        </button>
      </div>

      <div class="process-urgencia">
        <span class="urgency-pill urgency-${urgencia.toLowerCase()}">${URGENCIAS[urgencia].label}</span>
      </div>

      <div class="process-status">
        <select class="status-select status-${normalizar(status).replace(/\s+/g, '-')}" data-acao="status" aria-label="Alterar status">
          ${Object.entries(STATUS).map(([valor, label]) => `<option value="${valor}" ${valor === status ? 'selected' : ''}>${label}</option>`).join('')}
        </select>
      </div>

      <div class="process-progresso">
        <button type="button" class="progress-cell ${p.progresso ? '' : 'is-empty'}" data-acao="progresso" title="Clique para registrar a última coisa feita">${p.progresso ? escapeHtml(p.progresso) : 'Registrar progresso'}</button>
        ${atualizado ? `<p class="process-meta">Atualizado em ${formatarData(atualizado)}${escapeHtml(atualizadoPor)}</p>` : ''}
      </div>

      <div class="process-actions">
        <button type="button" class="btn-icon action-check" data-acao="concluir" title="${concluido ? 'Reabrir' : 'Concluir'}">
          ${concluido ? ICONES.reabrir : ICONES.check}<span class="action-label">${concluido ? 'Reabrir' : 'Concluir'}</span>
        </button>
        <button type="button" class="btn-icon" data-acao="editar" title="Editar">
          ${ICONES.editar}<span class="action-label">Editar</span>
        </button>
        <button type="button" class="btn-icon action-delete" data-acao="excluir" title="Excluir">
          ${ICONES.excluir}<span class="action-label">Excluir</span>
        </button>
      </div>
    </li>`;
}

function render() {
  document.body.classList.toggle('carregando', modo === 'carregando');
  // Não redesenha a lista enquanto alguém digita o progresso (atualizações de colegas chegam depois)
  if (edicaoAtiva) {
    atualizarKpis();
    return;
  }
  atualizarListasDePessoas();
  atualizarKpis();

  const visiveis = processos.filter(passaFiltros).sort(compararProcessos);
  processList.innerHTML = visiveis.map(htmlProcesso).join('');

  const filtrando = temFiltroAtivo();
  btnLimparFiltros.hidden = !filtrando;
  resultCount.textContent = filtrando ? `${visiveis.length} de ${processos.length}` : '';

  const vazio = visiveis.length === 0;
  emptyState.hidden = !vazio;
  if (vazio) {
    const semNada = processos.length === 0;
    $('emptyTitle').textContent = modo === 'carregando' ? 'Conectando ao banco de dados...'
      : semNada ? 'Nenhum processo cadastrado' : 'Nenhum processo encontrado';
    $('emptyText').textContent = modo === 'carregando' ? 'Aguarde um instante.'
      : semNada
        ? (nucleoAtual().temQuadro ? 'Carregue os processos do quadro do setor ou cadastre um novo.' : `Cadastre o primeiro processo de ${nucleoAtual().nome}.`)
        : 'Nenhum processo corresponde aos filtros aplicados.';
    $('btnLimparVazio').hidden = semNada || modo === 'carregando';
    $('btnCarregarQuadro').hidden = !semNada || modo === 'carregando' || !nucleoAtual().temQuadro;
    $('btnNovoVazio').hidden = modo === 'carregando';
  }
}

// ============================================================================
// AÇÕES NA LISTA
// ============================================================================
processList.addEventListener('click', async (e) => {
  const botao = e.target.closest('button[data-acao]');
  if (!botao) return;
  const id = botao.closest('.process').dataset.id;
  const item = processos.find(p => p.id === id);
  if (!item) return;

  if (botao.dataset.acao === 'editar') {
    abrirModal(item);
  } else if (botao.dataset.acao === 'progresso') {
    editarProgresso(botao, item);
  } else if (botao.dataset.acao === 'quem') {
    editarPessoas(botao, item);
  } else if (botao.dataset.acao === 'concluir') {
    const novoStatus = estaConcluido(item) ? 'Em Andamento' : 'Concluido';
    const ok = await tentar(() => atualizarProcesso(id, { status: novoStatus }), 'Erro ao alterar o status.');
    if (ok) showToast(novoStatus === 'Concluido' ? 'Processo concluído.' : 'Processo reaberto.', 'success');
  } else if (botao.dataset.acao === 'excluir') {
    if (!confirm(`Excluir o processo "${item.descricao}"?`)) return;
    const ok = await tentar(() => removerProcesso(id), 'Erro ao excluir o processo.');
    if (ok) showToast('Processo excluído.');
  }
});

// Edição rápida de "Quem?" direto na lista: clicar fora ou Salvar grava, Esc cancela
function editarPessoas(ancora, item) {
  const pop = document.createElement('div');
  pop.className = 'people-popover';
  pop.setAttribute('role', 'dialog');
  pop.setAttribute('aria-label', 'Quem é responsável');
  pop.innerHTML = `
    <div class="people-popover-title">Quem?</div>
    <div class="people-picker"></div>
    <div class="people-popover-actions">
      <button type="button" class="btn btn-secondary" data-pop="cancelar">Cancelar</button>
      <button type="button" class="btn btn-primary" data-pop="salvar">Salvar</button>
    </div>`;
  document.body.appendChild(pop);
  const seletor = montarSeletorPessoas(pop.querySelector('.people-picker'), pessoasDe(item.quem));
  edicaoAtiva = true;

  // Abre logo abaixo dos nomes (ou acima, se não couber)
  const r = ancora.getBoundingClientRect();
  const cabeAbaixo = r.bottom + pop.offsetHeight + 8 <= window.innerHeight;
  const left = Math.max(12, Math.min(r.left, window.innerWidth - pop.offsetWidth - 12));
  const top = cabeAbaixo ? r.bottom + 6 : Math.max(12, r.top - pop.offsetHeight - 6);
  pop.style.left = `${window.scrollX + left}px`;
  pop.style.top = `${window.scrollY + top}px`;

  const aoClicarFora = (e) => {
    if (!pop.contains(e.target)) concluir(true);
  };
  const aoTeclar = (e) => {
    if (e.key === 'Escape') concluir(false);
  };

  let finalizado = false;
  async function concluir(salvar) {
    if (finalizado) return;
    finalizado = true;
    const novo = seletor.valor();
    pop.remove();
    document.removeEventListener('mousedown', aoClicarFora, true);
    document.removeEventListener('keydown', aoTeclar, true);
    edicaoAtiva = false;

    if (!salvar || novo === (item.quem || '')) {
      render();
      return;
    }
    if (novo.length > 200) {
      showToast('Nomes demais em "Quem?" (máximo de 200 caracteres).', 'error');
      render();
      return;
    }
    const ok = await tentar(() => atualizarProcesso(item.id, { quem: novo }), 'Erro ao salvar quem é responsável.');
    if (ok) showToast('Responsáveis atualizados.', 'success');
    else render();
  }

  pop.querySelector('[data-pop="salvar"]').addEventListener('click', () => concluir(true));
  pop.querySelector('[data-pop="cancelar"]').addEventListener('click', () => concluir(false));
  document.addEventListener('mousedown', aoClicarFora, true);
  document.addEventListener('keydown', aoTeclar, true);
}

// Edição rápida do progresso direto na lista: Enter salva, Esc cancela
function editarProgresso(celula, item) {
  const campo = document.createElement('textarea');
  campo.className = 'progress-input';
  campo.rows = 2;
  campo.maxLength = 1000;
  campo.placeholder = 'Última coisa feita...';
  campo.value = item.progresso || '';
  celula.replaceWith(campo);
  edicaoAtiva = true;
  campo.focus();
  campo.setSelectionRange(campo.value.length, campo.value.length);

  let finalizado = false;
  const finalizar = async (salvar) => {
    if (finalizado) return;
    finalizado = true;
    edicaoAtiva = false;
    const novo = campo.value.trim();
    if (!salvar || novo === (item.progresso || '')) {
      render();
      return;
    }
    const ok = await tentar(() => atualizarProcesso(item.id, { progresso: novo }), 'Erro ao salvar o progresso.');
    if (ok) showToast('Progresso atualizado.', 'success');
    else render();
  };

  campo.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      finalizar(true);
    } else if (e.key === 'Escape') {
      finalizar(false);
    }
  });
  campo.addEventListener('blur', () => finalizar(true));
}

processList.addEventListener('change', async (e) => {
  const campo = e.target.closest('[data-acao]');
  if (!campo) return;
  const id = campo.closest('.process').dataset.id;
  const item = processos.find(p => p.id === id);
  if (!item) return;

  if (campo.dataset.acao === 'status') {
    await tentar(() => atualizarProcesso(id, { status: campo.value }), 'Erro ao alterar o status.');
  } else if (campo.dataset.acao === 'item') {
    const index = Number(campo.dataset.index);
    const itens = itensDe(item).map((it, i) => (i === index ? { ...it, feito: campo.checked } : it));
    await tentar(() => atualizarProcesso(id, { itens }), 'Erro ao atualizar o item.');
  }
});

// ============================================================================
// MODAL DE CADASTRO / EDIÇÃO
// ============================================================================
function abrirModal(item = null) {
  demandaForm.reset();
  formDemandaId.value = item ? item.id : '';
  modalTitle.textContent = item ? 'Editar processo' : 'Novo processo';
  btnSaveModal.textContent = item ? 'Salvar alterações' : 'Cadastrar';

  inputDescricao.value = item?.descricao || '';
  seletorModal = montarSeletorPessoas(seletorQuem, pessoasDe(item?.quem));
  inputUrgencia.value = item ? normalizarUrgencia(item.urgencia) : 'Media';
  inputStatus.value = item ? normalizarStatus(item.status) : 'Em Andamento';
  inputProgresso.value = item?.progresso || '';
  inputItens.value = item ? itensDe(item).map(i => i.texto).join('\n') : '';
  inputObs.value = item?.obs || '';

  abrir(demandaModal);
  inputDescricao.focus();
}

demandaForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const id = formDemandaId.value;
  const existente = id ? processos.find(p => p.id === id) : null;

  // Mantém marcados os itens que continuam na lista
  const feitosAntes = new Set(itensDe(existente || {}).filter(i => i.feito).map(i => normalizar(i.texto)));
  const itens = inputItens.value.split('\n').map(t => t.trim()).filter(Boolean)
    .map(texto => ({ texto, feito: feitosAntes.has(normalizar(texto)) }));

  const dados = {
    descricao: inputDescricao.value.trim(),
    quem: seletorModal.valor(),
    urgencia: inputUrgencia.value,
    status: inputStatus.value,
    progresso: inputProgresso.value.trim(),
    itens,
    obs: inputObs.value.trim()
  };

  if (dados.quem.length > 200) {
    showToast('Nomes demais em "Quem?" (máximo de 200 caracteres).', 'error');
    return;
  }

  btnSaveModal.disabled = true;
  const ok = await tentar(
    () => (id ? atualizarProcesso(id, dados) : criarProcesso(dados)),
    'Erro ao salvar o processo.'
  );
  btnSaveModal.disabled = false;

  if (ok) {
    fechar(demandaModal);
    showToast(id ? 'Processo atualizado.' : 'Processo cadastrado.', 'success');
  }
});

// ============================================================================
// MODAL DO FIREBASE
// ============================================================================
function abrirModalFirebase() {
  const config = obterConfigAtiva();
  inputFirebaseConfig.value = config ? JSON.stringify(config, null, 2) : '';
  abrir(firebaseModal);
  inputFirebaseConfig.focus();
}

$('btnSalvarFirebase').addEventListener('click', async () => {
  const config = lerConfigFirebase(inputFirebaseConfig.value.trim());
  if (!configValida(config)) {
    showToast("Configuração inválida: cole o objeto firebaseConfig com 'apiKey' e 'projectId'.", 'error');
    return;
  }
  localStorage.setItem(CHAVE_CONFIG, JSON.stringify(config));
  fechar(firebaseModal);
  await initFirebase();
});

$('btnRestaurarPadrao').addEventListener('click', () => {
  localStorage.removeItem(CHAVE_CONFIG);
  fechar(firebaseModal);
  if (configValida(defaultConfigFile)) {
    initFirebase();
    return;
  }
  ativarModoLocal();
  showToast('Usando dados salvos neste navegador.');
});

// ============================================================================
// MODAIS (GENÉRICO)
// ============================================================================
function abrir(modal) {
  modal.classList.add('active');
  document.body.classList.add('modal-open');
}

function fechar(modal) {
  modal.classList.remove('active');
  if (!document.querySelector('.modal-backdrop.active')) document.body.classList.remove('modal-open');
}

[demandaModal, firebaseModal].forEach(modal => {
  modal.addEventListener('mousedown', (e) => {
    if (e.target === modal) fechar(modal);
  });
});

window.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    fechar(demandaModal);
    fechar(firebaseModal);
  }
});

// ============================================================================
// EVENTOS GERAIS
// ============================================================================
$('btnNovaDemanda').addEventListener('click', () => abrirModal());
$('btnNovoVazio').addEventListener('click', () => abrirModal());
$('btnCloseModal').addEventListener('click', () => fechar(demandaModal));
$('btnCancelModal').addEventListener('click', () => fechar(demandaModal));
$('btnConfigFirebase').addEventListener('click', abrirModalFirebase);
$('btnCloseFirebaseModal').addEventListener('click', () => fechar(firebaseModal));
$('btnCarregarQuadro').addEventListener('click', carregarProcessosDoQuadro);
$('btnLimparVazio').addEventListener('click', limparFiltros);
btnLimparFiltros.addEventListener('click', limparFiltros);

$('btnEntrarGoogle').addEventListener('click', entrarComGoogle);
$('btnTentarNovamente').addEventListener('click', () => initFirebase());
$('btnTrocarConta').addEventListener('click', async () => {
  await sair();
  entrarComGoogle();
});
$('btnUsuario').addEventListener('click', () => {
  if (confirm(`Sair da conta ${usuario?.email}?`)) sair();
});

$('btnImprimir').addEventListener('click', () => {
  $('printData').textContent = new Date().toLocaleString('pt-BR');
  window.print();
});

document.querySelectorAll('.kpi-card').forEach(card => {
  card.addEventListener('click', () => {
    filtroRapido = card.dataset.filtro === filtroRapido ? 'todos' : card.dataset.filtro;
    render();
  });
});

searchInput.addEventListener('input', render);
[filterQuem, filterUrgencia, filterStatus].forEach(sel => sel.addEventListener('change', render));

// Com o Firebase definido no arquivo, não há o que configurar pela tela
$('btnConfigFirebase').hidden = configValida(defaultConfigFile);

// ============================================================================
// NÚCLEOS: CHAVE SCP | PROCESSAMENTO DE DADOS
// ============================================================================
function atualizarCabecalhoNucleo() {
  const n = nucleoAtual();
  $('nucleoNome').textContent = n.nome;
  $('printTitulo').textContent = n.rotulo === n.nome ? n.nome : `${n.rotulo} - ${n.nome}`;
  document.title = `SCP Planner - ${n.nome}`;
  document.querySelectorAll('[data-nucleo]').forEach(botao => {
    botao.setAttribute('aria-pressed', String(botao.dataset.nucleo === nucleo));
  });
}

function trocarNucleo(novo) {
  if (novo === nucleo || !(novo in NUCLEOS)) return;
  nucleo = novo;
  try {
    localStorage.setItem(CHAVE_NUCLEO, novo);
  } catch {
    // navegador sem localStorage: vale só nesta visita
  }

  // Cada núcleo começa sem filtros
  searchInput.value = '';
  filterQuem.value = '';
  filterUrgencia.value = '';
  filterStatus.value = '';
  filtroRapido = 'todos';
  ultimaListaPessoas = '';
  atualizarCabecalhoNucleo();

  if (modo === 'local') {
    ativarModoLocal();
  } else if (usuario && acessoLiberado) {
    assinarProcessos();
  }
}

document.querySelectorAll('[data-nucleo]').forEach(botao => {
  botao.addEventListener('click', () => trocarNucleo(botao.dataset.nucleo));
});

atualizarCabecalhoNucleo();
initFirebase();
