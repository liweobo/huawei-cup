import pytest
import operational_simulation as op


@pytest.mark.parametrize("handling,expected",[(0,13),(12,25)])
def test_six_node_precedence_oracle(tmp_path,monkeypatch,handling,expected):
    monkeypatch.setattr(op,"RUN",tmp_path)
    (tmp_path/"results").mkdir()
    d={"nodes":[{"id":str(i)} for i in range(6)],"edges":[
        {"u":"4","v":"5","length_km":.81,"vehicle_tonnes":5},
        {"u":"5","v":"0","length_km":.81,"vehicle_tonnes":10}],
        "station_local_t_day":0,"original_diagonal_surface_t_day":0}
    r=op.simulate(d,[{"path":[4,5,0],"tonnes_day":40}],handling)
    assert r["delivered_t"]==40
    assert r["mean_delivery_time_delivered_min"]==expected
    assert r["train_departures"]==2
    assert r["daily_clearing"]=="FULL_UNDER_SCENARIO"
