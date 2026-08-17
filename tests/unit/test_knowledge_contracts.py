from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from gps.domain.contracts import (
    CanonicalBlock,
    CorpusVersion,
    DocumentChunk,
    SourceDocument,
    SourceDocumentVersion,
    SourceLink,
)
from gps.domain.enums import CanonicalBlockType, CorpusPublicationStatus, SourceDocumentStatus


def test_source_and_corpus_contracts_preserve_versioned_provenance() -> None:
    fetched_at = datetime(2026, 1, 1, tzinfo=UTC)
    link = SourceLink(label="Next step", url="https://example.invalid/next")
    block = CanonicalBlock(
        block_id="blk-1",
        block_type=CanonicalBlockType.ORDERED_STEPS,
        heading_path=("Registration", "Complete setup"),
        ordinal=1,
        text="Complete the documented setup steps.",
        links=(link,),
        source_locator="article > section:nth-of-type(2)",
    )
    document = SourceDocument(
        tenant_id="tenant-a",
        application_id="mohid-support",
        document_id="doc-1",
        canonical_url="https://example.invalid/article/1",
        title="Complete setup",
        product="mohid",
        category="registration",
        language="en",
        owner="knowledge-owner",
        status=SourceDocumentStatus.APPROVED,
        effective_from=fetched_at,
        current_version_id="docv-1",
    )
    version = SourceDocumentVersion(
        tenant_id="tenant-a",
        application_id="mohid-support",
        version_id="docv-1",
        document_id=document.document_id,
        content_hash="sha256:source",
        raw_snapshot_ref="raw/doc-1/docv-1",
        blocks=(block,),
        generated_markdown_ref="review/doc-1/docv-1.md",
        structural_diff_ref="diff/doc-1/docv-1.json",
        links=(link,),
        fetched_at=fetched_at,
        published_at=fetched_at,
        parser_version="parser-1",
    )
    chunk = DocumentChunk(
        tenant_id="tenant-a",
        application_id="mohid-support",
        chunk_id="chunk-1",
        document_version_id=version.version_id,
        ordinal=1,
        heading_path=block.heading_path,
        block_ids=(block.block_id,),
        block_types=(block.block_type,),
        text=block.text,
        locator=block.source_locator,
        canonical_url=document.canonical_url,
        chunk_hash="sha256:chunk",
        embedding_version="embedding-1",
    )
    corpus = CorpusVersion(
        tenant_id="tenant-a",
        application_id="mohid-support",
        corpus_version="corpus-1",
        document_version_ids=(version.version_id,),
        parser_version="parser-1",
        chunker_version="chunker-1",
        embedding_version="embedding-1",
        validation_report_ref="validation/corpus-1.json",
        structural_diff_ref="diff/corpus-1.json",
        approval_actor="knowledge-owner",
        approved_at=fetched_at,
        publication_status=CorpusPublicationStatus.APPROVED,
    )

    for contract in (document, version, chunk, corpus):
        assert contract.__class__.model_validate_json(contract.model_dump_json()) == contract
    assert version.document_id == document.document_id
    assert chunk.document_version_id in corpus.document_version_ids
    assert chunk.block_ids == (block.block_id,)


def test_approved_source_document_requires_a_current_version() -> None:
    with pytest.raises(ValidationError, match="current version"):
        SourceDocument(
            tenant_id="tenant-a",
            application_id="mohid-support",
            document_id="doc-1",
            canonical_url="https://example.invalid/article/1",
            title="Complete setup",
            product="mohid",
            category="registration",
            language="en",
            owner="knowledge-owner",
            status=SourceDocumentStatus.APPROVED,
        )


def test_approved_corpus_requires_recorded_approval() -> None:
    with pytest.raises(ValidationError, match="approval actor and timestamp"):
        CorpusVersion(
            tenant_id="tenant-a",
            application_id="mohid-support",
            corpus_version="corpus-1",
            document_version_ids=("docv-1",),
            parser_version="parser-1",
            chunker_version="chunker-1",
            embedding_version="embedding-1",
            validation_report_ref="validation/corpus-1.json",
            structural_diff_ref="diff/corpus-1.json",
            publication_status=CorpusPublicationStatus.APPROVED,
        )
