# Hydra

Hydra é um cockpit desktop para trabalhar com vários navegadores independentes dentro de uma única janela.

Cada navegador ocupa um painel na interface, podendo ter seu próprio perfil, sessão, áudio e configuração de atualização. O objetivo é facilitar o uso simultâneo de diferentes sites e contas sem depender de várias janelas ou instalações separadas do navegador.

## Funcionalidades

* Vários navegadores dentro da mesma janela
* Perfis persistentes para diferentes contas
* Perfis anônimos para sessões temporárias
* Isolamento de cookies e dados entre perfis
* Compartilhamento de identidade entre painéis que usam o mesmo perfil
* Sessões diferentes para diferentes contextos de trabalho
* Layouts de 1 a 9 painéis
* Auto reload configurável individualmente
* Controle de áudio por painel
* Barra de URL em cada navegador
* Edição de nome, URL, perfil e intervalo de atualização
* Execução de JavaScript por painel
* Salvamento automático das sessões
* Atalhos `Ctrl+1` até `Ctrl+9` para trocar de sessão

## Perfis

Cada painel pode usar um perfil nomeado ou funcionar de forma anônima.

Um perfil nomeado mantém os dados de navegação entre execuções, permitindo permanecer conectado a uma conta.

```text
Painel 1 → perfil: conta_1
Painel 2 → perfil: conta_2
Painel 3 → perfil: conta_1
```

Os dois primeiros painéis possuem identidades diferentes. O terceiro compartilha a identidade de `conta_1`.

Painéis sem perfil utilizam uma sessão temporária.

## Sessões

Sessões permitem salvar diferentes conjuntos de painéis.

Por exemplo:

```text
Social
├── Facebook
├── Instagram
├── X
└── YouTube

Trabalho
├── Gmail
├── Slack
└── Linear
```

Cada sessão possui seu próprio layout e configuração. Ao reabrir o Hydra, o estado da última sessão utilizada é restaurado.

## Instalação

### Requisitos

* Python 3.12 ou 3.13
* `uv`

### Criar o ambiente

Dentro da pasta do projeto:

```bash
uv python install 3.12
uv venv --python 3.12
source .venv/bin/activate
```

### Instalar as dependências

```bash
uv sync --extra dev
```

## Executar

```bash
uv run hydra
```

Também é possível executar como módulo:

```bash
python -m hydra
```

Para verificar o ambiente:

```bash
uv run hydra --diagnostics
```

## Desenvolvimento

Testes:

```bash
uv run pytest
```

Verificação:

```bash
uv run ruff check .
```

Formatação:

```bash
uv run ruff format .
```

Também existem scripts para facilitar essas tarefas:

```bash
./scripts/setup.sh
./scripts/run.sh
./scripts/check.sh
```

## Dados

Os dados do Hydra são armazenados em:

```text
~/.hydra/
├── sessions.json
└── profiles/
```

As sessões são salvas automaticamente e os perfis nomeados permanecem disponíveis entre execuções.

## Tecnologias

Hydra utiliza Python, PySide6 e Qt WebEngine para fornecer a interface desktop e a renderização dos navegadores.


