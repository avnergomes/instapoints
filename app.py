"""
Aplicativo Streamlit para visualização de pontos geoespaciais a partir de arquivos CSV ou XLSX.
"""

from __future__ import annotations

import io
from typing import Optional

import pandas as pd
import streamlit as st

try:
    from folium import Map, Marker
    from folium.plugins import MarkerCluster
except ModuleNotFoundError as exc:
    st.error(
        "A biblioteca Folium não está instalada. Verifique se o arquivo "
        "requirements.txt inclui 'folium' e reinstale as dependências."
    )
    st.stop()

from streamlit_folium import st_folium


# Configuração inicial da página para um layout amplo.
st.set_page_config(page_title="Instapoints", layout="wide")


def carregar_dados(arquivo_subido: io.BytesIO) -> Optional[pd.DataFrame]:
    """Lê o arquivo CSV ou XLSX enviado pelo usuário.

    A função tenta identificar automaticamente o formato com base na extensão
    informada pelo widget de upload. Caso a leitura falhe, uma mensagem de
    erro amigável é apresentada e ``None`` é retornado.
    """

    if arquivo_subido is None:
        return None

    try:
        nome_arquivo = getattr(arquivo_subido, "name", "")
        extensao = nome_arquivo.split(".")[-1].lower() if "." in nome_arquivo else ""

        conteudo = arquivo_subido.getvalue()
        buffer = io.BytesIO(conteudo)

        if extensao == "xlsx":
            return pd.read_excel(buffer, engine="openpyxl")

        if extensao == "csv":
            buffer.seek(0)
            return pd.read_csv(buffer)

        # Se a extensão for desconhecida, tentamos primeiro como CSV e, em caso de
        # falha, como XLSX para cobrir cenários em que o usuário enviou o arquivo
        # correto, porém sem extensão ou com um tipo MIME inesperado.
        try:
            buffer.seek(0)
            return pd.read_csv(buffer)
        except Exception:
            buffer.seek(0)
            return pd.read_excel(buffer, engine="openpyxl")

    except Exception as exc:  # Captura qualquer falha de leitura.
        st.error(f"Não foi possível ler o arquivo enviado. Detalhes: {exc}")
        return None


def validar_colunas(dados: pd.DataFrame) -> bool:
    """Confere se as colunas obrigatórias estão presentes na planilha."""

    colunas_necessarias = {"latitude", "longitude"}
    colunas_encontradas = set(dados.columns.str.lower())

    if not colunas_necessarias.issubset(colunas_encontradas):
        st.error(
            "O arquivo deve conter as colunas 'latitude' e 'longitude'. "
            f"Colunas encontradas: {', '.join(dados.columns)}"
        )
        return False

    return True


def construir_mapa(dados: pd.DataFrame) -> Map:
    """Cria e retorna o objeto Folium com os pontos carregados."""

    # Normaliza nomes das colunas para acessar independentemente de caixa.
    dados = dados.rename(columns=str.lower)
    dados["latitude"] = pd.to_numeric(dados["latitude"], errors="coerce")
    dados["longitude"] = pd.to_numeric(dados["longitude"], errors="coerce")
    dados = dados.dropna(subset=["latitude", "longitude"])

    if dados.empty:
        raise ValueError(
            "Não há registros válidos após remover linhas sem latitude/longitude."
        )

    # Calcula o centro a partir da média das coordenadas.
    centro = [dados["latitude"].mean(), dados["longitude"].mean()]

    mapa = Map(location=centro, zoom_start=4, tiles="CartoDB positron")

    marcador_cluster = MarkerCluster(name="Pontos").add_to(mapa)
    for _, linha in dados.iterrows():
        Marker(
            location=[linha["latitude"], linha["longitude"]],
        ).add_to(marcador_cluster)

    return mapa


def main() -> None:
    """Ponto de entrada do aplicativo."""

    st.title("Instapoints - Visualizador de Coordenadas")
    st.markdown(
        """
        Carregue um arquivo **CSV** ou **XLSX** contendo as colunas `latitude` e
        `longitude`. Após o upload, os pontos serão exibidos em um mapa
        interativo. Utilize o zoom e clique nos agrupamentos para explorar os
        dados.
        """
    )

    arquivo = st.file_uploader(
        "Selecione um arquivo CSV ou XLSX",
        type=["csv", "xlsx"],
        help="O arquivo deve conter as colunas latitude e longitude.",
    )

    dados = carregar_dados(arquivo)
    if dados is None:
        st.info("Faça o upload de um arquivo para visualizar o mapa.")
        return

    if not validar_colunas(dados):
        return

    try:
        mapa = construir_mapa(dados)
    except ValueError as erro:
        st.warning(str(erro))
        return

    st_folium(mapa, width=1000, height=600)


if __name__ == "__main__":
    main()
