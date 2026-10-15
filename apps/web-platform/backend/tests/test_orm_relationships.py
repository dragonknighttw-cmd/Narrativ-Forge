import pytest
from sqlalchemy.orm import Session, selectinload

from app.db import Base, create_database_engine
from app.models import (
    Asset,
    Episode,
    ExportRecord,
    ManualProductionLog,
    ProcessingJob,
    ReviewRecord,
    Scene,
    Script,
    Season,
    Series,
    SocialAnalyticsRecord,
    SocialPublication,
    Subtitle,
)


pytestmark = pytest.mark.integration


def test_domain_relationships_traverse_and_support_targeted_eager_loading():
    engine = create_database_engine("sqlite://")
    Base.metadata.create_all(bind=engine)
    try:
        with Session(engine) as db:
            series = Series(title="Relationship series")
            season = Season(series=series, season_number=1, title="Season 1")
            episode = Episode(
                public_id="NF-RELATIONSHIP",
                series=series,
                season=season,
                episode_number=1,
                title="Relationship episode",
            )
            script = Script(episode=episode, version=1, content="Story")
            scene = Scene(episode=episode, script=script, scene_number=1, purpose="Opening")
            asset = Asset(
                episode=episode,
                scene=scene,
                asset_type="video",
                original_filename="source.mp4",
                mime_type="video/mp4",
                file_size_bytes=10,
                version=1,
            )
            job = ProcessingJob(episode=episode, input_asset=asset, output_asset=asset, job_type="mock")
            subtitle = Subtitle(episode=episode, version=1)
            export = ExportRecord(episode=episode, provider="mock_drive")
            review = ReviewRecord(episode=episode)
            production_log = ManualProductionLog(episode=episode, topic="Topic")
            publication = SocialPublication(episode=episode, platform="tiktok")
            analytics = SocialAnalyticsRecord(publication=publication)
            db.add_all([
                series, season, episode, script, scene, asset, job, subtitle,
                export, review, production_log, publication, analytics,
            ])
            db.commit()
            episode_id = episode.id
            db.expire_all()

            loaded_episode = (
                db.query(Episode)
                .options(
                    selectinload(Episode.scripts).selectinload(Script.scenes),
                    selectinload(Episode.assets),
                    selectinload(Episode.processing_jobs).selectinload(ProcessingJob.input_asset),
                    selectinload(Episode.processing_jobs).selectinload(ProcessingJob.output_asset),
                    selectinload(Episode.subtitles),
                    selectinload(Episode.export_records),
                    selectinload(Episode.review_record),
                    selectinload(Episode.manual_production_logs),
                    selectinload(Episode.social_publications).selectinload(
                        SocialPublication.analytics_records
                    ),
                )
                .filter(Episode.id == episode_id)
                .one()
            )

            assert loaded_episode.series.title == "Relationship series"
            assert loaded_episode in loaded_episode.series.episodes
            assert loaded_episode.season.series.id == loaded_episode.series.id
            assert loaded_episode.season.title == "Season 1"
            assert loaded_episode in loaded_episode.season.episodes
            assert loaded_episode.season in loaded_episode.series.seasons
            assert loaded_episode.scripts[0].episode.id == episode_id
            assert loaded_episode.scripts[0].scenes[0].script.version == 1
            assert loaded_episode.scenes[0].episode.id == episode_id
            assert loaded_episode.scenes[0].assets[0].original_filename == "source.mp4"
            assert loaded_episode.assets[0].episode.id == episode_id
            assert loaded_episode.assets[0].scene.id == loaded_episode.scenes[0].id
            assert loaded_episode.processing_jobs[0].input_asset.id == loaded_episode.assets[0].id
            assert loaded_episode.processing_jobs[0].output_asset.id == loaded_episode.assets[0].id
            assert loaded_episode.assets[0].input_jobs[0].id == loaded_episode.processing_jobs[0].id
            assert loaded_episode.assets[0].output_jobs[0].id == loaded_episode.processing_jobs[0].id
            assert loaded_episode.processing_jobs[0].episode.id == episode_id
            assert loaded_episode.subtitles[0].episode.id == episode_id
            assert loaded_episode.export_records[0].episode.id == episode_id
            assert loaded_episode.review_record.episode.id == episode_id
            assert loaded_episode.manual_production_logs[0].episode.id == episode_id
            assert loaded_episode.social_publications[0].analytics_records[0].publication.id == (
                loaded_episode.social_publications[0].id
            )
    finally:
        engine.dispose()
