"""Tests for agentshield.feedback.store.

Every test uses a pytest temporary directory - the real feedback storage is
never touched.
"""

from __future__ import annotations

import json
import threading
from datetime import datetime, timezone
from pathlib import Path

import pytest

from agentshield.feedback.models import FeedbackDecision, FeedbackRecord
from agentshield.feedback.store import (
    STORAGE_PATH_ENV_VAR,
    FeedbackStore,
    FeedbackStoreError,
    default_storage_path,
)


def make_record(feedback_id="fb-1", patch_id="patch-1", finding_id="finding-1",
                decision=FeedbackDecision.ACCEPTED, **overrides) -> FeedbackRecord:
    data = {
        "feedback_id": feedback_id,
        "patch_id": patch_id,
        "finding_id": finding_id,
        "finding_type": "s3_public_access",
        "iac_type": "terraform",
        "resource_type": "aws_s3_bucket",
        "generated_patch": "- public_access = true\n+ public_access = false",
        "decision": decision,
        "reason": "ok",
        "timestamp": datetime(2025, 1, 1, tzinfo=timezone.utc),
    }
    data.update(overrides)
    return FeedbackRecord(**data)


@pytest.fixture
def path(tmp_path: Path) -> Path:
    return tmp_path / "nested" / "dir" / "feedback.json"


@pytest.fixture
def store(path: Path) -> FeedbackStore:
    return FeedbackStore(path)


# 1 + 2 + 3. Initialisation, automatic directory + file creation
def test_initialization_creates_directory_and_empty_json_file(path):
    assert not path.parent.exists()
    store = FeedbackStore(path)
    assert path.parent.is_dir()          # 2. directory created
    assert path.is_file()                # 3. file created
    assert json.loads(path.read_text(encoding="utf-8")) == []
    assert store.storage_path == path


def test_existing_file_is_not_overwritten_on_init(path):
    FeedbackStore(path).save_feedback(make_record())
    assert len(FeedbackStore(path).get_all_feedback()) == 1


# 4 + 5. Save and retrieve by id
def test_save_and_get_feedback(store):
    record = make_record()
    assert store.save_feedback(record) == record
    assert store.get_feedback("fb-1") == record


def test_get_unknown_feedback_returns_none(store):
    assert store.get_feedback("does-not-exist") is None


def test_save_rejects_non_record(store):
    with pytest.raises(TypeError):
        store.save_feedback({"feedback_id": "x"})  # type: ignore[arg-type]


# 6 + 9. All feedback / multiple records, order preserved, nothing lost
def test_multiple_records_are_all_kept_in_order(store):
    for i in range(5):
        store.save_feedback(make_record(feedback_id=f"fb-{i}", patch_id=f"p{i}",
                                        finding_id=f"f{i}"))
    ids = [r.feedback_id for r in store.get_all_feedback()]
    assert ids == [f"fb-{i}" for i in range(5)]
    assert store.count() == 5


def test_saving_same_id_replaces_in_place(store):
    store.save_feedback(make_record("fb-1", patch_id="a"))
    store.save_feedback(make_record("fb-2", patch_id="b"))
    store.save_feedback(make_record("fb-1", patch_id="a", decision=FeedbackDecision.REJECTED))
    records = store.get_all_feedback()
    assert [r.feedback_id for r in records] == ["fb-1", "fb-2"]
    assert records[0].decision == FeedbackDecision.REJECTED


# 7. By patch id
def test_get_feedback_by_patch(store):
    store.save_feedback(make_record("fb-1", patch_id="patch-A"))
    store.save_feedback(make_record("fb-2", patch_id="patch-B"))
    store.save_feedback(make_record("fb-3", patch_id="patch-A"))
    assert [r.feedback_id for r in store.get_feedback_by_patch("patch-A")] == ["fb-1", "fb-3"]
    assert store.get_feedback_by_patch("nope") == []


# 8. By finding id
def test_get_feedback_by_finding(store):
    store.save_feedback(make_record("fb-1", finding_id="F1"))
    store.save_feedback(make_record("fb-2", finding_id="F2"))
    assert [r.feedback_id for r in store.get_feedback_by_finding("F2")] == ["fb-2"]
    assert store.get_feedback_by_finding("nope") == []


# 10. Delete
def test_delete_feedback(store):
    store.save_feedback(make_record("fb-1"))
    store.save_feedback(make_record("fb-2"))
    assert store.delete_feedback("fb-1") is True
    assert store.get_feedback("fb-1") is None
    assert store.get_feedback("fb-2") is not None
    assert store.delete_feedback("fb-1") is False


# 11. Clear
def test_clear_feedback(store, path):
    store.save_feedback(make_record("fb-1"))
    store.save_feedback(make_record("fb-2"))
    assert store.clear_feedback() == 2
    assert store.get_all_feedback() == []
    assert json.loads(path.read_text(encoding="utf-8")) == []


# 12. Persistence between store instances
def test_persistence_between_store_instances(path):
    FeedbackStore(path).save_feedback(make_record("fb-1"))
    second = FeedbackStore(path)
    second.save_feedback(make_record("fb-2"))
    third = FeedbackStore(path)
    assert [r.feedback_id for r in third.get_all_feedback()] == ["fb-1", "fb-2"]
    assert third.get_feedback("fb-1") == make_record("fb-1")


# 13. Empty store
def test_empty_store(store):
    assert store.get_all_feedback() == []
    assert store.count() == 0
    assert store.get_feedback_by_patch("x") == []
    assert store.get_feedback_by_finding("x") == []


def test_zero_byte_file_is_treated_as_empty_store(path):
    store = FeedbackStore(path)
    path.write_text("", encoding="utf-8")
    assert store.get_all_feedback() == []
    assert list(path.parent.glob("*.corrupt-*")) == []  # not treated as corruption
    store.save_feedback(make_record())
    assert store.count() == 1


# 14. Missing storage file
def test_missing_file_is_recreated(store, path):
    store.save_feedback(make_record())
    path.unlink()
    assert store.get_all_feedback() == []
    assert path.is_file()
    store.save_feedback(make_record("fb-2"))
    assert store.count() == 1


# 15. Corrupt JSON
def test_corrupt_json_is_quarantined_not_lost(store, path):
    path.write_text("{ this is not json", encoding="utf-8")
    assert store.get_all_feedback() == []          # graceful, no exception
    backups = list(path.parent.glob("feedback.json.corrupt-*"))
    assert len(backups) == 1                        # bad data preserved
    assert backups[0].read_text(encoding="utf-8") == "{ this is not json"
    assert json.loads(path.read_text(encoding="utf-8")) == []
    store.save_feedback(make_record())              # store usable again
    assert store.count() == 1


def test_wrong_top_level_type_is_quarantined(store, path):
    path.write_text('{"feedback_id": "x"}', encoding="utf-8")
    assert store.get_all_feedback() == []
    assert len(list(path.parent.glob("feedback.json.corrupt-*"))) == 1


def test_invalid_utf8_is_quarantined(store, path):
    path.write_bytes(b"\xff\xfe\x00bad")
    assert store.get_all_feedback() == []
    assert len(list(path.parent.glob("feedback.json.corrupt-*"))) == 1


def test_invalid_entries_are_skipped_but_preserved_on_write(store, path):
    good = make_record("fb-good")
    bad = {"feedback_id": "fb-bad", "decision": "MAYBE"}
    path.write_text(json.dumps([good.to_dict(), bad, "junk"]), encoding="utf-8")

    assert [r.feedback_id for r in store.get_all_feedback()] == ["fb-good"]

    store.save_feedback(make_record("fb-new"))
    raw = json.loads(path.read_text(encoding="utf-8"))
    assert len(raw) == 4                            # nothing dropped
    assert bad in raw and "junk" in raw
    assert [r.feedback_id for r in store.get_all_feedback()] == ["fb-good", "fb-new"]


# Atomic / robustness extras
def test_write_leaves_no_temporary_files(store, path):
    store.save_feedback(make_record())
    assert [p.name for p in path.parent.iterdir()] == ["feedback.json"]


def test_written_file_is_valid_json_list(store, path):
    store.save_feedback(make_record())
    data = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(data, list) and data[0]["decision"] == "ACCEPTED"


def test_unicode_is_preserved(store):
    store.save_feedback(make_record(reason="Réparation — correcte ✓"))
    assert store.get_feedback("fb-1").reason == "Réparation — correcte ✓"


def test_concurrent_saves_do_not_lose_records(store):
    def worker(n: int) -> None:
        for i in range(5):
            store.save_feedback(make_record(f"fb-{n}-{i}", patch_id=f"p{n}{i}",
                                            finding_id=f"f{n}{i}"))

    threads = [threading.Thread(target=worker, args=(n,)) for n in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert store.count() == 20


def test_unwritable_location_raises_store_error(tmp_path):
    blocker = tmp_path / "file_not_dir"
    blocker.write_text("x", encoding="utf-8")
    with pytest.raises(FeedbackStoreError):
        FeedbackStore(blocker / "sub" / "feedback.json")


# Default location
def test_default_path_uses_environment_variable(monkeypatch, tmp_path):
    target = tmp_path / "custom" / "fb.json"
    monkeypatch.setenv(STORAGE_PATH_ENV_VAR, str(target))
    assert default_storage_path() == target
    store = FeedbackStore()
    assert store.storage_path == target and target.is_file()


def test_default_path_is_outside_the_repository(monkeypatch, tmp_path):
    monkeypatch.delenv(STORAGE_PATH_ENV_VAR, raising=False)
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    assert default_storage_path() == tmp_path / ".agentshield" / "feedback" / "feedback.json"