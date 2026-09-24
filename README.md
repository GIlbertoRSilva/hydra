# Hydra

Hydra é um cockpit desktop para abrir vários navegadores dentro de uma única janela. Cada painel pode usar uma identidade persistente própria ou uma sessão anônima.

O foco desta versão é estabilidade, isolamento de perfis, persistência do estado e uma interface mais limpa.

## O que foi preservado

- Vários painéis na mesma janela
- Perfis persistentes por nome
- Painéis anônimos
- Sessões com layouts independentes
- Auto reload individual
- Áudio independente por painel
- Edição de nome, URL, perfil e intervalo
- Execução de JavaScript por painel
- Persistência em `~/.hydra`
- CRUD de sessões
- Atalhos `Ctrl+1` até `Ctrl+9`

## Estrutura

```text
hydra/
├── hydra/
│   ├── application/
│   │   └── session_manager.py
│   ├── domain/
│   │   ├── models.py
│   │   └── validation.py
│   ├── infrastructure/
│   │   ├── settings.py
│   │   └── storage.py
│   ├── ui/
│   │   ├── dialogs.py
│   │   ├── pane.py
│   │   └── window.py
│   ├── web/
│   │   └── profiles.py
│   ├── app.py
│   ├── config.py
│   └── __main__.py
├── tests/
├── pyproject.toml
└── README.md
```

A divisão é intencional:

- `domain` contém dados e validações sem depender da interface.
- `application` controla o estado das sessões.
- `infrastructure` cuida dos arquivos locais.
- `web` controla perfis e páginas do Qt WebEngine.
- `ui` cuida apenas da apresentação e interação.

## Requisitos

Python 3.12 ou 3.13.

O projeto usa PySide6 6.11.x. A versão 6.11.2 é a versão estável mais recente no momento da preparação deste projeto e possui pacotes para Python 3.12 e 3.13.

## Instalação com uv

### 1. Entre na pasta do projeto

```bash
cd hydra
```

### 2. Confirme o Python

```bash
python3 --version
```

O esperado é `3.12.x` ou `3.13.x`.

Caso precise instalar o Python 3.12 pelo `uv`:

```bash
uv python install 3.12
```

### 3. Crie o ambiente

```bash
uv venv --python 3.12
```

Ative:

```bash
source .venv/bin/activate
```

### 4. Instale o projeto

Com dependências de desenvolvimento:

```bash
uv sync --extra dev
```

O `uv sync` resolve as dependências do `pyproject.toml` e cria o `uv.lock` para registrar as versões resolvidas.

### 5. Verifique o ambiente

```bash
uv run hydra --diagnostics
```

A saída deve mostrar Python, PySide6, Chromium e os caminhos usados pelo Hydra.

### 6. Inicie

```bash
uv run hydra
```

Também funciona:

```bash
python -m hydra
```

## Atalhos de desenvolvimento

Depois de instalar o `uv`, o projeto também possui scripts para reduzir trabalho manual:

```bash
./scripts/setup.sh
./scripts/run.sh
./scripts/check.sh
```

Por padrão, `setup.sh` usa Python 3.12. Para usar Python 3.13:

```bash
HYDRA_PYTHON=3.13 ./scripts/setup.sh
```

## Git desde o início

O ZIP é entregue sem histórico Git para começar uma base nova e limpa.

Na pasta do projeto:

```bash
git init
git branch -M main
git add .
git commit -m "refactor: rebuild hydra"
```

Para adicionar um repositório remoto:

```bash
git remote add origin URL_DO_REPOSITORIO
git push -u origin main
```

Não versionar `~/.hydra`. Esses dados ficam fora do projeto.

## Migração da base anterior

Você pode substituir o conteúdo do repositório antigo por esta estrutura sem apagar `~/.hydra`. O `sessions.json` antigo é lido e convertido para o formato atual quando o estado for salvo. Os diretórios dos perfis mantêm o caminho original, então os logins já armazenados podem continuar disponíveis.

Antes da primeira execução, vale fazer uma cópia de segurança: 

```bash
cp -a ~/.hydra ~/.hydra.backup
```

## Dados locais

```text
~/.hydra/
├── sessions.json
├── sessions.json.bak
└── profiles/
    ├── conta_1/
    ├── conta_2/
    └── ...
```

Perfis nomeados usam diretórios separados. Duas páginas que usam o mesmo perfil compartilham a mesma identidade do navegador. Páginas com nomes de perfil diferentes usam armazenamentos diferentes. O Qt WebEngine organiza cookies, cache e outros dados de navegação dentro do perfil.

Painéis sem perfil usam um perfil temporário e não persistente.

## Primeiro uso

Ao iniciar pela primeira vez, o Hydra cria a sessão `Social` com cinco painéis de exemplo. Faça login manualmente nos serviços que quiser manter persistentes.

Quando o Hydra for fechado, o estado da sessão é salvo. Na abertura seguinte, a sessão ativa anterior é restaurada.

## Interface

A interface foi simplificada para reduzir ruído visual:

- Sem emojis em botões e títulos.
- Controles do painel usam símbolos curtos e tooltips.
- Perfil aparece como texto simples.
- A sidebar mostra apenas nome, quantidade de painéis e layout.
- O layout é alterado sem recriar os painéis.

## Problemas com o WebEngine

Comece por:

```bash
uv run hydra --diagnostics
```

Depois tente executar:

```bash
uv run hydra
```

Para investigar problemas gráficos no Linux, você pode testar temporariamente:

```bash
QTWEBENGINE_CHROMIUM_FLAGS="--disable-gpu" uv run hydra
```

Isso é diagnóstico, não configuração padrão.

Se aparecer uma mensagem relacionada ao sandbox do Chromium, confira primeiro se o processo não está sendo executado como `root`. Não transforme a desativação do sandbox em configuração permanente sem necessidade.

## Testes

```bash
uv run pytest
```

Lint:

```bash
uv run ruff check .
```

Formatação:

```bash
uv run ruff format .
```

## Comportamento dos perfis

Perfil vazio:

```text
Painel -> perfil temporário -> cookies e dados em memória -> fim do processo -> descartado
```

Perfil nomeado:

```text
Painel A -> perfil conta_1 ┐
                          ├-> mesmo armazenamento
Painel B -> perfil conta_1 ┘

Painel C -> perfil conta_2 -> armazenamento separado
```

O gerenciador de perfis mantém uma única instância de cada perfil nomeado durante a execução. Isso é importante para que vários painéis possam compartilhar a mesma identidade sem criar múltiplas instâncias concorrentes do mesmo perfil.

## Escopo atual

Hydra é um cockpit visual de navegadores. Não é um substituto para Selenium ou Playwright.

Não há proxy, VPN, distribuição remota ou troca automática de credenciais nesta versão.

## Próximos incrementos sugeridos

### 1. Presets de painéis

Salvar conjuntos de painel e configuração para criar uma nova sessão rapidamente.

### 2. Automação por regras

Em vez de apenas expor `run_js`, criar ações encadeadas como abrir URL, esperar carregamento, executar JavaScript, extrair resultado e registrar status.

### 3. Agendamento

Permitir iniciar uma sessão em horários definidos, com auto reload e encerramento automático.

### 4. Captura

Screenshot de um painel, da grade inteira e exportação simples para arquivo.

### 5. Indicadores de saúde

Mostrar carregando, online, erro de rede e última atualização sem aumentar a poluição visual.

### 6. Recuperação automática

Detectar uma página travada ou falha do processo WebEngine e recriar somente o painel afetado.

### 7. Gerenciamento de perfis

Tela dedicada para listar perfis, abrir uma sessão usando um perfil existente e remover dados de um perfil.

### 8. Importação e exportação

Exportar sessões para um arquivo `.json` e importar em outra instalação, sem copiar credenciais por padrão.

### 9. Segurança da automação

Separar scripts confiáveis de scripts editáveis pelo usuário, registrar execuções e limitar ações destrutivas.

### 10. Métricas do cockpit

Tempo de carregamento, número de reloads, erros de navegação e uso por sessão.

## Critério de pronto

A primeira versão refatorada deve ser considerada funcional quando:

1. o projeto cria o ambiente sem intervenção manual extra;
2. o Hydra abre sem depender de arquivos antigos do repositório;
3. cada painel navega de forma independente;
4. perfis diferentes não compartilham armazenamento;
5. o mesmo perfil pode ser usado por mais de um painel;
6. perfis nomeados sobrevivem ao reinício;
7. perfis anônimos não sobrevivem ao encerramento;
8. sessões e layouts voltam corretamente na próxima abertura;
9. um painel pode ser alterado ou fechado sem derrubar os outros.
