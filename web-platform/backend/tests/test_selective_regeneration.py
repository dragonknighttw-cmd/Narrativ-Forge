from app.models import Episode, Scene, Script, Series
from app.services.selective_regeneration import regenerate_scene


def test_selective_regeneration_creates_new_script_version(db_session):
    db = db_session
    series = Series(title="Test Series")
    db.add(series)
    db.flush()

    episode = Episode(
        public_id="ep-test-1",
        series_id=series.id,
        episode_number=1,
        title="Episode 1",
    )
    db.add(episode)
    db.flush()

    script = Script(
        episode_id=episode.id,
        version=1,
        title="Episode 1",
        content="Original script",
        is_current=True,
    )
    db.add(script)
    db.flush()

    db.add_all([
        Scene(
            episode_id=episode.id,
            script_id=script.id,
            scene_number=1,
            purpose="hook",
            description="Old hook",
            dialogue="Old dialogue",
            duration_seconds=5,
        ),
        Scene(
            episode_id=episode.id,
            script_id=script.id,
            scene_number=2,
            purpose="body",
            description="Body",
            dialogue="Body dialogue",
            duration_seconds=20,
        ),
    ])
    db.commit()

    new_script, scenes = regenerate_scene(db, episode, 1, "Make the hook clearer")

    assert new_script.version == 2
    assert new_script.is_current is True
    assert script.is_current is False
    assert len(scenes) == 2
    assert scenes[0].scene_number == 1
    assert scenes[0].description != "Old hook"
    assert scenes[1].description == "Body"
    assert episode.current_step == "review"
    assert episode.status == "script_review"
