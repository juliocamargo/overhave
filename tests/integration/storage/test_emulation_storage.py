from typing import cast

import pytest
from faker import Faker

from overhave import db
from overhave.db import EmulationStatus
from overhave.storage import EmulationStorage, SystemUserModel
from overhave.storage.emulation_storage import NotFoundEmulationError


@pytest.mark.usefixtures("database", "socket_mock")
class TestEmulationStorage:
    """Integration tests for :class:`EmulationStorage`."""

    def test_raise_exception_for_not_existing_id(self, test_emulation_storage: EmulationStorage, faker: Faker) -> None:
        with pytest.raises(NotFoundEmulationError):
            test_emulation_storage.get_requested_emulation_run(cast(int, faker.random_int()))

    @pytest.mark.parametrize("test_user_role", [db.Role.admin, db.Role.user], indirect=True)
    def test_create_emulation_run(
        self, test_emulation_storage: EmulationStorage, test_system_user: SystemUserModel, test_emulation: db.Emulation
    ) -> None:
        emulation_run = test_emulation_storage.create_emulation_run(
            emulation_id=test_emulation.id, initiated_by=test_system_user.login
        )
        assert emulation_run.status == EmulationStatus.CREATED
        assert emulation_run.emulation_id == test_emulation.id
        assert emulation_run.initiated_by == test_system_user.login
        assert emulation_run.port is None

    @pytest.mark.parametrize("test_user_role", [db.Role.admin, db.Role.user], indirect=True)
    def test_get_requested_emulation_run(
        self, test_emulation_storage: EmulationStorage, test_system_user: SystemUserModel, test_emulation: db.Emulation
    ) -> None:
        emulation_run = test_emulation_storage.create_emulation_run(
            emulation_id=test_emulation.id, initiated_by=test_system_user.login
        )
        requested_emulation_run: db.EmulationRun = test_emulation_storage.get_requested_emulation_run(emulation_run.id)
        assert requested_emulation_run.status == EmulationStatus.REQUESTED
        assert requested_emulation_run.emulation_id == test_emulation.id
        assert not test_emulation_storage._is_port_in_use(requested_emulation_run.port)

    @pytest.mark.parametrize("test_user_role", [db.Role.admin, db.Role.user], indirect=True)
    def test_set_error_run_status(
        self,
        test_emulation_storage: EmulationStorage,
        test_system_user: SystemUserModel,
        test_emulation: db.Emulation,
        faker: Faker,
    ) -> None:
        emulation_run = test_emulation_storage.create_emulation_run(
            emulation_id=test_emulation.id, initiated_by=test_system_user.login
        )
        assert emulation_run.status == EmulationStatus.CREATED
        test_emulation_storage.set_error_emulation_run(
            emulation_run_id=emulation_run.id, traceback=cast(str, faker.sentence())
        )
        emulation_run = test_emulation_storage.get_emulation_run_by_id(emulation_run.id)
        assert emulation_run.status == EmulationStatus.ERROR
        assert emulation_run.port is None

    @pytest.mark.parametrize("test_user_role", [db.Role.admin, db.Role.user], indirect=True)
    @pytest.mark.parametrize(
        "emulation_status",
        [EmulationStatus.READY, EmulationStatus.REQUESTED, EmulationStatus.ERROR, EmulationStatus.CREATED],
    )
    def test_set_emulation_run_status(
        self,
        test_emulation_storage: EmulationStorage,
        test_system_user: SystemUserModel,
        test_emulation: db.Emulation,
        emulation_status: EmulationStatus,
    ) -> None:
        emulation_run = test_emulation_storage.create_emulation_run(
            emulation_id=test_emulation.id, initiated_by=test_system_user.login
        )
        test_emulation_storage.set_emulation_run_status(emulation_run.id, emulation_status)
        emulation_run = test_emulation_storage.get_emulation_run_by_id(emulation_run.id)
        assert emulation_run.status == emulation_status

    @pytest.mark.parametrize("test_user_role", [db.Role.admin, db.Role.user], indirect=True)
    def test_get_emulation_run_by_incorrect_id(
        self,
        test_emulation_storage: EmulationStorage,
        test_system_user: SystemUserModel,
        test_emulation: db.Emulation,
        faker: Faker,
    ) -> None:
        with pytest.raises(NotFoundEmulationError):
            test_emulation_storage.get_emulation_run_by_id(faker.pyint())

    @pytest.mark.parametrize("test_user_role", [db.Role.admin, db.Role.user], indirect=True)
    def test_get_emulation_run_by_id(
        self,
        test_emulation_storage: EmulationStorage,
        test_system_user: SystemUserModel,
        test_emulation: db.Emulation,
        faker: Faker,
    ) -> None:
        emulation_run = test_emulation_storage.create_emulation_run(
            emulation_id=test_emulation.id, initiated_by=test_system_user.login
        )
        assert test_emulation_storage.get_emulation_run_by_id(test_emulation.id) == emulation_run

    def test_get_emulation_run_by_test_user_id_empty(
        self,
        test_emulation_storage: EmulationStorage,
        faker: Faker,
    ) -> None:
        filtered_runs = test_emulation_storage.get_emulation_runs_by_test_user_id(test_user_id=faker.random_int())
        assert not filtered_runs

    @pytest.mark.parametrize("test_user_role", [db.Role.admin, db.Role.user], indirect=True)
    def test_get_emulation_run_by_test_user_id(
        self,
        test_emulation_storage: EmulationStorage,
        test_system_user: SystemUserModel,
        test_emulation: db.Emulation,
        faker: Faker,
    ) -> None:
        emulation_run = test_emulation_storage.create_emulation_run(
            emulation_id=test_emulation.id, initiated_by=test_system_user.login
        )
        filtered_runs = test_emulation_storage.get_emulation_runs_by_test_user_id(test_user_id=test_system_user.id)
        assert len(filtered_runs) == 1
        assert filtered_runs[0] == emulation_run
