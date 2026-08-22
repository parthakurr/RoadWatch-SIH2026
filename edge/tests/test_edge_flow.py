"""
Tests for the RoadWatch edge daemon (mock camera, offline storage, sync).
"""
import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

EDGE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(EDGE_DIR))

from duplicate_filter import DuplicateFilter
from network import NetworkMonitor
from storage import IncidentStorage, SYNC_STATUS_PENDING, SYNC_STATUS_SYNCED
from sync import IncidentSync, OfflineBufferSync


@pytest.fixture
def temp_db(tmp_path):
    return tmp_path / "test_buffer.db"


@pytest.fixture
def sample_gps():
    return {
        "latitude": 28.6139,
        "longitude": 77.2090,
        "speed_kmh": 20.0,
        "valid": True,
    }


@pytest.fixture
def sample_detection():
    return {
        "class_name": "Pothole",
        "confidence": 0.91,
        "severity": "HIGH",
        "bbox": [240, 200, 160, 110],
        "bbox_normalized": [0.375, 0.4167, 0.625, 0.6458],
    }


def test_storage_creates_parent_directory(tmp_path):
    """SQLite parent directory is created automatically."""
    temp_db = tmp_path / "nested" / "dir" / "test_buffer.db"
    assert not temp_db.parent.exists()
    storage = IncidentStorage(db_path=temp_db)
    assert temp_db.exists()
    assert storage.count_pending() == 0


def test_1_mock_detection_online_upload(temp_db, sample_gps, sample_detection):
    """TEST 1: mock detection -> GPS -> online -> upload."""
    storage = IncidentStorage(db_path=temp_db)
    network = NetworkMonitor(backend_url="http://localhost:8000", mock_offline=False)
    sync = IncidentSync(storage, network, backend_url="http://localhost:8000")

    storage.save_incident("VEH-01", sample_gps, sample_detection, image_base64="abc")

    mock_response = MagicMock()
    mock_response.status_code = 201

    with patch("sync.requests.post", return_value=mock_response) as post_mock:
        with patch.object(network, "is_backend_reachable", return_value=True):
            synced = sync.sync_pending()

    assert synced == 1
    assert storage.count_pending() == 0
    post_mock.assert_called_once()
    payload = post_mock.call_args.kwargs["json"]
    assert payload["vehicle_id"] == "VEH-01"
    assert payload["confidence"] == 0.91


def test_2_mock_detection_offline_sqlite(temp_db, sample_gps, sample_detection):
    """TEST 2: mock detection -> GPS -> offline -> SQLite."""
    buffer = OfflineBufferSync(db_path=str(temp_db), mock_offline=True)
    incident_id = buffer.storage.save_incident("VEH-02", sample_gps, sample_detection)

    assert buffer.pending_count == 1
    assert buffer.sync_pending() == 0

    row = buffer.storage.get_incident_by_id(incident_id)
    assert row["sync_status"] == SYNC_STATUS_PENDING
    assert row["vehicle_id"] == "VEH-02"


def test_3_offline_then_sync_when_network_restored(temp_db, sample_gps, sample_detection):
    """TEST 3: offline incident -> network restored -> synchronization."""
    storage = IncidentStorage(db_path=temp_db)
    network = NetworkMonitor(backend_url="http://localhost:8000")
    sync = IncidentSync(storage, network, backend_url="http://localhost:8000")

    storage.save_incident("VEH-03", sample_gps, sample_detection)

    with patch.object(network, "is_backend_reachable", return_value=False):
        assert sync.sync_pending() == 0
    assert storage.count_pending() == 1

    mock_response = MagicMock()
    mock_response.status_code = 200
    with patch("sync.requests.post", return_value=mock_response):
        with patch.object(network, "is_backend_reachable", return_value=True):
            synced = sync.sync_pending()

    assert synced == 1
    assert storage.count_pending() == 0


def test_4_upload_failure_keeps_pending(temp_db, sample_gps, sample_detection):
    """TEST 4: upload fails -> incident remains PENDING."""
    storage = IncidentStorage(db_path=temp_db)
    network = NetworkMonitor(backend_url="http://localhost:8000")
    sync = IncidentSync(storage, network, backend_url="http://localhost:8000")

    storage.save_incident("VEH-04", sample_gps, sample_detection)

    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"

    with patch("sync.requests.post", return_value=mock_response):
        with patch.object(network, "is_backend_reachable", return_value=True):
            synced = sync.sync_pending()

    assert synced == 0
    assert storage.count_pending() == 1


def test_5_duplicate_detection_suppressed(sample_gps):
    """TEST 5: repeated detection of same pothole -> only one incident."""
    duplicate_filter = DuplicateFilter(cooldown_sec=60, radius_meters=15)

    assert duplicate_filter.should_create_incident(sample_gps) is True
    assert duplicate_filter.should_create_incident(sample_gps) is False

    far_gps = {
        **sample_gps,
        "latitude": sample_gps["latitude"] + 0.01,
        "longitude": sample_gps["longitude"] + 0.01,
    }
    assert duplicate_filter.should_create_incident(far_gps) is True


def test_6_pending_incidents_survive_restart(temp_db, sample_gps, sample_detection):
    """TEST 6: application restart while pending -> incidents still present."""
    storage = IncidentStorage(db_path=temp_db)
    incident_id = storage.save_incident("VEH-06", sample_gps, sample_detection)
    assert storage.count_pending() == 1

    storage_after_restart = IncidentStorage(db_path=temp_db)
    assert storage_after_restart.count_pending() == 1
    row = storage_after_restart.get_incident_by_id(incident_id)
    assert row["sync_status"] == SYNC_STATUS_PENDING
    assert json.loads(row["bbox_json"])[0] == pytest.approx(0.375)


def test_offline_buffer_sync_from_edge_directory(temp_db):
    """Regression: running from inside edge/ must not break SQLite paths."""
    buffer = OfflineBufferSync(db_path=str(temp_db))
    assert buffer.storage.db_path == temp_db
    buffer.storage.save_incident(
        "VEH-EDGE",
        {"latitude": 1.0, "longitude": 2.0, "speed_kmh": 0, "valid": True},
        {"class_name": "Pothole", "confidence": 0.8, "severity": "LOW", "bbox_normalized": [0, 0, 1, 1]},
    )
    assert buffer.pending_count == 1


def test_mark_synced_updates_status(temp_db, sample_gps, sample_detection):
    storage = IncidentStorage(db_path=temp_db)
    incident_id = storage.save_incident("VEH-07", sample_gps, sample_detection)
    row = storage.get_incident_by_id(incident_id)
    storage.mark_synced(row["id"])
    updated = storage.get_incident_by_id(incident_id)
    assert updated["sync_status"] == SYNC_STATUS_SYNCED
    assert updated["synced"] == 1
