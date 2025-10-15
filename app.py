"""
Aplicativo Streamlit para visualização de pontos geoespaciais a partir de arquivos CSV ou XLSX.
"""

from __future__ import annotations

import io
from typing import Optional

import pandas as pd
import streamlit as st
from folium import Map, Marker
from folium.plugins import MarkerCluster
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
        if arquivo_subido.type in ("text/csv", "application/vnd.ms-excel", "application/octet-stream"):
            # Alguns navegadores enviam XLSX como application/octet-stream
            return pd.read_csv(arquivo_subido)

        if arquivo_subido.type in (
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ):
            return pd.read_excel(arquivo_subido, engine="openpyxl")

        # Caso a extensão não seja conhecida, tentamos ler como CSV.
        return pd.read_csv(arquivo_subido)

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
    dados = dados.dropna(subset=["latitude", "longitude"])

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

    mapa = construir_mapa(dados)

    st_folium(mapa, width=1000, height=600)


if __name__ == "__main__":
    main()
