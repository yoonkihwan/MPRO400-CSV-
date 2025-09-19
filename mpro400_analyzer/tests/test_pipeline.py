from pathlib import Path

from data.data_manager import DataManager


def test_manager_loads_and_corrects_angles():
    manager = DataManager()
    sample = Path(__file__).resolve().parent / "data" / "sample.csv"

    warnings = manager.load([sample])
    assert warnings == []
    assert len(manager.datasets()) == 1

    payloads = manager.plot_payloads()
    assert len(payloads) == 1
    payload = payloads[0]
    assert payload.label == sample.name
    assert payload.x[0] == 0.0

    manager.update_reference(1.5)
    payload = manager.plot_payloads()[0]
    assert payload.reference_hit
    assert payload.x[-1] == 0.0  # 마지막 점이 기준에 맞춰짐
    assert payload.x[0] < 0.0

    manager.update_ranges((0.5, 2.5), (-10, 10))
    filtered = manager.plot_payloads()[0]
    assert filtered.y[0] >= 0.5

    dataset_id = manager.datasets()[0].identifier
    manager.remove(dataset_id)
    assert manager.datasets() == []
    assert manager.selected_dataset() is None

    manager.load([sample])
    manager.clear()
    assert manager.datasets() == []
