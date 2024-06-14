import json
import os
import subprocess

from database import Database

from ..src.bundle_generator import BundleGenerator


def test_generate_bundle(tmp_path, database: Database):
    with database.Session() as session:
        with BundleGenerator(
            session=session, platform_id=1, bundle_name="trino"
        ) as bundle:
            subprocess.run(["tar", "-xf", bundle.path], cwd=tmp_path)
        bundle_files: list[str] = os.listdir(tmp_path)
        assert bundle_files == ["trino.rego", "trino/data.json", ".manifest"]


def test_generate_data_object(database: Database):
    with open(
        "permitta/src/opa/bundle_generator/test/bundle_generator_test_data.json"
    ) as f:
        expected: dict = json.load(f)

    with database.Session() as session:
        actual = BundleGenerator.generate_data_object(session=session, platform_id=1)
        assert list(actual.keys()) == ["data_objects", "principals"]

        # data objects
        assert sorted(
            actual.get("data_objects"), key=lambda e: e.get("object").get("table")
        ) == sorted(
            expected.get("data_objects"), key=lambda e: e.get("object").get("table")
        )

        # principals
        assert sorted(actual.get("principals"), key=lambda e: e["name"]) == sorted(
            expected.get("principals"), key=lambda e: e["name"]
        )


def test_generate_principals_in_data_object(database: Database):
    with open(
        "permitta/src/opa/bundle_generator/test/bundle_generator_test_data.json"
    ) as f:
        expected: dict = json.load(f).get("principals")

    with database.Session() as session:
        actual = BundleGenerator._generate_principals_in_data_object(session=session)

    assert sorted(actual, key=lambda e: e["name"]) == sorted(
        expected, key=lambda e: e["name"]
    )


def test_generate_data_objects_in_data_object(database: Database):
    with open(
        "permitta/src/opa/bundle_generator/test/bundle_generator_test_data.json"
    ) as f:
        expected: dict = json.load(f).get("data_objects")

    with database.Session() as session:
        actual = BundleGenerator._generate_data_objects_in_data_object(
            session=session, platform_id=1
        )

    assert sorted(actual, key=lambda e: e.get("object").get("table")) == sorted(
        expected, key=lambda e: e.get("object").get("table")
    )
