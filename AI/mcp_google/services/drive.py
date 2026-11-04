"""Google Drive API Tools for MCP."""

import io
from typing import Any, Dict, List, Optional

from googleapiclient.http import MediaInMemoryUpload, MediaIoBaseDownload

from ..auth import get_service


def drive_search_files(
    query: str = "",
    folder_id: Optional[str] = None,
    page_size: int = 15,
) -> List[Dict[str, Any]]:
    """Search files and folders in Google Drive.

    Args:
        query: Drive search filter (e.g., "name contains 'Report'", "mimeType = 'application/pdf'").
        folder_id: Optional folder ID to restrict the search to a specific directory.
        page_size: Maximum files to return (default 15, max 50).
    """
    service = get_service("drive", "v3")

    q_parts = ["trashed = false"]
    if query:
        q_parts.append(f"({query})")
    if folder_id:
        q_parts.append(f"'{folder_id}' in parents")

    q_string = " and ".join(q_parts)

    res = (
        service.files()
        .list(
            q=q_string,
            pageSize=max(1, min(page_size, 50)),
            fields="files(id, name, mimeType, modifiedTime, size, webViewLink, shared)",
        )
        .execute()
    )
    return res.get("files", [])


def drive_get_file_metadata(file_id: str) -> Dict[str, Any]:
    """Retrieve metadata and sharing details for a Google Drive file.

    Args:
        file_id: Google Drive file ID.
    """
    service = get_service("drive", "v3")
    return (
        service.files()
        .get(
            fileId=file_id,
            fields="id, name, mimeType, description, star, trashed, parents, webViewLink, webContentLink, createdTime, modifiedTime, size, owners",
        )
        .execute()
    )


def drive_read_file(file_id: str) -> Dict[str, Any]:
    """Read the content of a Google Drive file.

    Automatically handles Google Docs (exported to plain text) and Google Sheets
    (exported to CSV), as well as standard text and markdown files.

    Args:
        file_id: Google Drive file ID.
    """
    service = get_service("drive", "v3")
    meta = service.files().get(fileId=file_id, fields="id, name, mimeType").execute()
    mime_type = meta.get("mimeType", "")

    # Handle Google Workspace documents by exporting
    if mime_type == "application/vnd.google-apps.document":
        content_bytes = (
            service.files()
            .export(fileId=file_id, mimeType="text/plain")
            .execute()
        )
        return {
            "id": file_id,
            "name": meta.get("name"),
            "mimeType": mime_type,
            "exportedAs": "text/plain",
            "content": content_bytes.decode("utf-8", errors="replace"),
        }

    if mime_type == "application/vnd.google-apps.spreadsheet":
        content_bytes = (
            service.files()
            .export(fileId=file_id, mimeType="text/csv")
            .execute()
        )
        return {
            "id": file_id,
            "name": meta.get("name"),
            "mimeType": mime_type,
            "exportedAs": "text/csv",
            "content": content_bytes.decode("utf-8", errors="replace"),
        }

    # Standard file download
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()

    fh.seek(0)
    data = fh.read()

    try:
        text_content = data.decode("utf-8")
        return {
            "id": file_id,
            "name": meta.get("name"),
            "mimeType": mime_type,
            "content": text_content,
        }
    except UnicodeDecodeError:
        return {
            "id": file_id,
            "name": meta.get("name"),
            "mimeType": mime_type,
            "sizeBytes": len(data),
            "content": f"[Binary file of size {len(data)} bytes - cannot display as text]",
        }


def drive_upload_file(
    name: str,
    content: str,
    folder_id: Optional[str] = None,
    mime_type: str = "text/plain",
) -> Dict[str, Any]:
    """Upload or create a new text file or markdown note in Google Drive.

    Args:
        name: Desired filename (e.g., 'meeting_notes.md', 'summary.txt').
        content: Text content to save.
        folder_id: Optional parent folder ID in Google Drive.
        mime_type: MIME type of the file (default 'text/plain').
    """
    service = get_service("drive", "v3")

    file_metadata: Dict[str, Any] = {"name": name}
    if folder_id:
        file_metadata["parents"] = [folder_id]

    media = MediaInMemoryUpload(content.encode("utf-8"), mimetype=mime_type, resumable=False)
    created = (
        service.files()
        .create(
            body=file_metadata,
            media_body=media,
            fields="id, name, mimeType, webViewLink",
        )
        .execute()
    )

    return {
        "status": "created",
        "id": created.get("id"),
        "name": created.get("name"),
        "mimeType": created.get("mimeType"),
        "webViewLink": created.get("webViewLink"),
    }


def drive_create_folder(
    name: str, parent_folder_id: Optional[str] = None
) -> Dict[str, Any]:
    """Create a new folder in Google Drive.

    Args:
        name: Name of the new folder.
        parent_folder_id: Optional parent folder ID.
    """
    service = get_service("drive", "v3")

    meta: Dict[str, Any] = {
        "name": name,
        "mimeType": "application/vnd.google-apps.folder",
    }
    if parent_folder_id:
        meta["parents"] = [parent_folder_id]

    folder = service.files().create(body=meta, fields="id, name, webViewLink").execute()
    return {
        "status": "created",
        "id": folder.get("id"),
        "name": folder.get("name"),
        "webViewLink": folder.get("webViewLink"),
    }


def drive_delete_file(file_id: str, permanent: bool = False) -> Dict[str, Any]:
    """Delete a file or move it to trash in Google Drive.

    Args:
        file_id: File ID to delete or trash.
        permanent: If True, permanently removes the file. If False (default), moves to trash.
    """
    service = get_service("drive", "v3")
    if permanent:
        service.files().delete(fileId=file_id).execute()
        return {"status": "permanently_deleted", "id": file_id}
    else:
        service.files().update(fileId=file_id, body={"trashed": True}).execute()
        return {"status": "trashed", "id": file_id}
