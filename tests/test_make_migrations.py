from django.db import models

from psqlextra.backend.migrations import operations
from psqlextra.models import PostgresPartitionedModel
from psqlextra.types import PostgresPartitioningMethod

from .fake_model import define_fake_app, define_fake_partitioning_model
from .migrations import make_migration


def test_make_migration_create_partitioned_model():
    """Tests whether the right operations are generated when creating a new
    partitioned model."""

    part_options = {
        "method": PostgresPartitioningMethod.LIST,
        "key": ["category"],
    }

    app_config = define_fake_app()

    model = define_fake_partitioning_model(
        fields={"category": models.TextField()},
        partitioning_options=part_options,
        meta_options=dict(app_label=app_config.name),
    )

    migration = make_migration(model._meta.app_label)
    ops = migration.operations

    # should have one operation to create the partitioned modele
    # and one more to add a default partition
    assert len(ops) == 2
    assert isinstance(ops[0], operations.PostgresCreatePartitionedModel)
    assert isinstance(ops[1], operations.PostgresAddDefaultPartition)

    # make sure the base is set correctly
    assert len(ops[0].bases) == 1
    assert issubclass(ops[0].bases[0], PostgresPartitionedModel)

    # make sure the partitioning options got copied correctly
    assert ops[0].partitioning_options == part_options

    # make sure the default partition is named "default"
    assert ops[1].model_name == model.__name__
    assert ops[1].name == "default"