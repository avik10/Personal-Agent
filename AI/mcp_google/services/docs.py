"""Google Docs API Tools for MCP."""

from typing import Any, Dict, List, Optional

from ..auth import get_service


def _extract_text_from_elements(elements: List[Dict[str, Any]]) -> str:
    """Helper to parse text out of structural elements from Google Docs API."""
    text_chunks: List[str] = []
    for elem in elements:
        if "paragraph" in elem:
            for p_elem in elem["paragraph"].get("elements", []):
                if "textRun" in p_elem:
                    text_chunks.append(p_elem["textRun"].get("content", ""))
        elif "table" in elem:
            table = elem["table"]
            for row in table.get("tableRows", []):
                row_texts = []
                for cell in row.get("tableCells", []):
                    cell_text = _extract_text_from_elements(cell.get("content", []))
                    row_texts.append(cell_text.strip())
                text_chunks.append(" | ".join(row_texts) + "\n")
    return "".join(text_chunks)


def docs_get_document(document_id: str) -> Dict[str, Any]:
    """Retrieve full text content and metadata of a Google Doc.

    Args:
        document_id: Google Document ID.
    """
    service = get_service("docs", "v1")
    doc = service.documents().get(documentId=document_id).execute()

    body = doc.get("body", {})
    content_elements = body.get("content", [])
    extracted_text = _extract_text_from_elements(content_elements)

    return {
        "documentId": doc.get("documentId"),
        "title": doc.get("title"),
        "revisionId": doc.get("revisionId"),
        "text": extracted_text,
    }


def docs_create_document(
    title: str, initial_content: Optional[str] = None
) -> Dict[str, Any]:
    """Create a new Google Document with an optional initial body text.

    Args:
        title: Title of the new Google Doc.
        initial_content: Optional body text to insert into the created document.
    """
    service = get_service("docs", "v1")
    created = service.documents().create(body={"title": title}).execute()
    doc_id = created.get("documentId")

    if initial_content and doc_id:
        requests = [
            {
                "insertText": {
                    "location": {"index": 1},
                    "text": initial_content,
                }
            }
        ]
        service.documents().batchUpdate(
            documentId=doc_id, body={"requests": requests}
        ).execute()

    return {
        "status": "created",
        "documentId": doc_id,
        "title": created.get("title"),
        "url": f"https://docs.google.com/document/d/{doc_id}/edit",
    }


def docs_append_text(document_id: str, text: str) -> Dict[str, Any]:
    """Append text to the end of an existing Google Document.

    Args:
        document_id: Target Google Document ID.
        text: Text string to append.
    """
    service = get_service("docs", "v1")
    doc = service.documents().get(documentId=document_id).execute()

    # The end index is right before the document's final trailing newline
    content = doc.get("body", {}).get("content", [])
    if content:
        end_index = content[-1].get("endIndex", 1) - 1
    else:
        end_index = 1

    end_index = max(1, end_index)

    requests = [
        {
            "insertText": {
                "location": {"index": end_index},
                "text": ("\n" if not text.startswith("\n") else "") + text,
            }
        }
    ]

    res = (
        service.documents()
        .batchUpdate(documentId=document_id, body={"requests": requests})
        .execute()
    )

    return {
        "status": "appended",
        "documentId": document_id,
        "replies": res.get("replies", []),
    }
