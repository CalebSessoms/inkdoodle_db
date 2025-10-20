# cli/init_mapping_template.py — writes app_field_mapping.json with placeholders
import json
from pathlib import Path

TEMPLATE = {
  "users": {
    "id": "users.id",
    "email": "users.email",
    "password_hash": "users.password_hash",
    "display_name": "users.display_name",
    "created_at": "users.created_at",
    "is_active": "users.is_active",
    "_app_model_name": "Creator",            # <-- change to your app's model name
    "_app_fields": {                         # <-- replace keys/values with the app's field names
      "creatorId": "id",
      "email": "email",
      "name": "display_name",
      "createdAt": "created_at",
      "active": "is_active"
    }
  },
  "works": {
    "id": "works.id",
    "owner_user_id": "works.owner_user_id",
    "title": "works.title",
    "slug": "works.slug",
    "summary": "works.summary",
    "created_at": "works.created_at",
    "updated_at": "works.updated_at",
    "_app_model_name": "Project",            # e.g., Project, Story, etc.
    "_app_fields": {
      "projectId": "id",
      "ownerId": "owner_user_id",
      "title": "title",
      "slug": "slug",
      "description": "summary",
      "createdAt": "created_at",
      "updatedAt": "updated_at"
    }
  },
  "chapters": {
    "id": "chapters.id",
    "work_id": "chapters.work_id",
    "number": "chapters.number",
    "title": "chapters.title",
    "content_md": "chapters.content_md",
    "status": "chapters.status",
    "created_at": "chapters.created_at",
    "updated_at": "chapters.updated_at",
    "_app_model_name": "Chapter",
    "_app_fields": {
      "chapterId": "id",
      "projectId": "work_id",
      "index": "number",
      "title": "title",
      "content": "content_md",
      "state": "status",
      "createdAt": "created_at",
      "updatedAt": "updated_at"
    }
  },
  "notes": {
    "id": "notes.id",
    "user_id": "notes.user_id",
    "work_id": "notes.work_id",
    "chapter_id": "notes.chapter_id",
    "title": "notes.title",
    "body_md": "notes.body_md",
    "tags_json": "notes.tags_json",
    "created_at": "notes.created_at",
    "updated_at": "notes.updated_at",
    "_app_model_name": "Note",
    "_app_fields": {
      "noteId": "id",
      "authorId": "user_id",
      "projectId": "work_id",
      "chapterId": "chapter_id",
      "title": "title",
      "body": "body_md",
      "tags": "tags_json",
      "createdAt": "created_at",
      "updatedAt": "updated_at"
    }
  },
  "refs": {
    "id": "refs.id",
    "work_id": "refs.work_id",
    "chapter_id": "refs.chapter_id",
    "note_id": "refs.note_id",
    "label": "refs.label",
    "url": "refs.url",
    "ref_type": "refs.ref_type",
    "created_at": "refs.created_at",
    "_app_model_name": "Reference",
    "_app_fields": {
      "referenceId": "id",
      "projectId": "work_id",
      "chapterId": "chapter_id",
      "noteId": "note_id",
      "label": "label",
      "link": "url",
      "type": "ref_type",
      "createdAt": "created_at"
    }
  }
}

out = Path("app_field_mapping.json")
if out.exists():
    print(f"{out} already exists. Open and edit it in VS Code.")
else:
    out.write_text(json.dumps(TEMPLATE, indent=2))
    print(f"Wrote {out}. Open and edit the _app_model_name and _app_fields to match the app.")
