from __future__ import annotations

import streamlit as st

from app.config.settings import settings
from app.core.ai_client import AIClient, AIClientTimeoutError
from app.core.document_parser import DocumentParser
from app.core.search_engine import SearchEngine
from app.models.domain import ChatMessage
from app.repositories.document_repository import DocumentRepository
from app.repositories.vector_store_repository import VectorStoreRepository
from app.services.chat_service import ChatService
from app.services.import_service import ImportService
from app.utils.logger import get_logger


logger = get_logger(__name__)


def build_services() -> tuple[ImportService, ChatService, AIClient]:
    ai_client = AIClient(settings)
    vector_store_repository = VectorStoreRepository(settings.vector_store_dir)
    document_repository = DocumentRepository(settings.records_dir)
    document_parser = DocumentParser(settings)
    import_service = ImportService(
        document_repository=document_repository,
        document_parser=document_parser,
        vector_store_repository=vector_store_repository,
        ai_client=ai_client,
    )
    search_engine = SearchEngine(
        vector_store_repository=vector_store_repository,
        ai_client=ai_client,
        top_k=settings.search_top_k,
    )
    chat_service = ChatService(search_engine=search_engine, ai_client=ai_client)
    return import_service, chat_service, ai_client


def render_messages() -> None:
    for message in st.session_state["messages"]:
        with st.chat_message(message.role):
            st.markdown(message.content)


def process_chat_prompt(chat_service: ChatService, prompt: str):
    try:
        return chat_service.process_message(prompt)
    except AIClientTimeoutError:
        logger.warning("Chat request timed out after %s seconds.", settings.openai_timeout_seconds)
        raise
    except Exception:
        logger.exception("Chat processing failed for prompt: %s", prompt)
        raise


def main() -> None:
    st.set_page_config(page_title="Personal Fishing Assistant", page_icon="🎣", layout="wide")
    st.title("Personal Fishing Assistant")
    st.caption("釣行記録を取り込み、関連記録を参照しながら相談できます。")

    import_service, chat_service, ai_client = build_services()

    if not ai_client.has_api_key():
        st.error("OpenAI API key is not set. Please set OPENAI_API_KEY in .env file.")
        st.stop()

    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    with st.sidebar:
        st.header("インポート")
        st.write(f"対象ディレクトリ: `{settings.records_dir}`")
        if st.button("Markdown をインポート", use_container_width=True):
            with st.spinner("インポート中..."):
                result = import_service.import_documents()
            if result.imported_count > 0:
                st.success(result.message)
            else:
                st.warning(result.message)
            for warning in result.warnings:
                st.warning(f"{warning.filename}: {warning.reason}")
            for error in result.errors:
                st.error(f"{error.filename}: {error.reason}")

    render_messages()

    prompt = st.chat_input("釣りの相談を入力してください")
    if not prompt:
        return

    user_message = ChatMessage(role="user", content=prompt)
    st.session_state["messages"].append(user_message)
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        response = process_chat_prompt(chat_service, prompt)
    except AIClientTimeoutError:
        st.error("OpenAI API request timed out after 30 seconds.")
        return
    except Exception as exc:
        st.error(f"チャット処理に失敗しました: {exc}")
        return

    if not response.has_records:
        st.info("関連記録がないため、一般的な知識に基づいて回答します。")

    assistant_message = ChatMessage(role="assistant", content=response.message)
    st.session_state["messages"].append(assistant_message)
    with st.chat_message("assistant"):
        st.markdown(response.message)


if __name__ == "__main__":
    main()
