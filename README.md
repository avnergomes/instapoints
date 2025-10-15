# Instapoints

Aplicativo Streamlit para visualização de coordenadas geográficas a partir de arquivos CSV ou XLSX.

## Como executar localmente

1. Crie e ative um ambiente virtual (opcional, mas recomendado).
2. Instale as dependências: `pip install -r requirements.txt`.
3. Execute: `streamlit run app.py`.

## Preparando o deploy no Streamlit Community Cloud

1. Faça um fork ou crie um repositório no GitHub contendo os arquivos `app.py`, `requirements.txt` e este `README.md`.
2. Acesse [https://share.streamlit.io](https://share.streamlit.io) com a sua conta do Streamlit Community Cloud.
3. Clique em **New app** e conecte sua conta do GitHub.
4. Selecione o repositório e branch que contêm o aplicativo.
5. Informe `app.py` como arquivo principal.
6. Clique em **Deploy**. A aplicação será construída automaticamente utilizando o `requirements.txt`.
7. Sempre que fizer push de novas alterações, o Streamlit reconstruirá a aplicação automaticamente.

## Uso

1. Faça upload de um arquivo CSV ou XLSX com colunas `latitude` e `longitude`.
2. Aguarde o carregamento do mapa. Os pontos serão agrupados automaticamente por proximidade.
3. Utilize o zoom e clique nos clusters ou marcadores individuais para explorar os dados.

## Estrutura do projeto

```
.
├── app.py
├── requirements.txt
└── README.md
```

## Licença

Distribuído nos termos da licença MIT. Consulte o arquivo `LICENSE` se disponível.
