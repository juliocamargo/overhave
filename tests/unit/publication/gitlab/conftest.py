from typing import Callable, List, Mapping, Optional, Sequence, cast

import pytest
from faker import Faker
from pytest_mock import MockFixture

from overhave import OverhaveFileSettings, OverhaveProjectSettings
from overhave.entities import GitRepositoryInitializer
from overhave.publication.gitlab import GitlabVersionPublisher, OverhaveGitlabPublisherSettings
from overhave.publication.gitlab.tokenizer import TokenizerClient, TokenizerClientSettings
from overhave.scenario import FileManager
from overhave.storage import FeatureTypeName, IDraftStorage, IFeatureStorage, IScenarioStorage, ITestRunStorage
from overhave.transport import GitlabHttpClient


@pytest.fixture()
def test_gitlab_publisher_settings_with_default_reviewers(
    test_repository_id_or_name: str,
    test_project_key: str,
    test_target_branch: str,
    test_default_reviewers: Sequence[str],
) -> OverhaveGitlabPublisherSettings:
    return OverhaveGitlabPublisherSettings(
        repository_id=test_repository_id_or_name,
        default_target_branch_name=test_target_branch,
        default_reviewers=test_default_reviewers,
    )


@pytest.fixture()
def test_gitlab_project_settings_with_reviewers_mapping(
    test_repository_id_or_name: str,
    test_target_branch: str,
    test_reviewers_mapping: Mapping[FeatureTypeName, List[str]],
) -> OverhaveGitlabPublisherSettings:
    return OverhaveGitlabPublisherSettings(
        repository_id=test_repository_id_or_name,
        default_target_branch_name=test_target_branch,
        feature_type_to_reviewers_mapping=test_reviewers_mapping,
    )


@pytest.fixture()
def mocked_gitlab_client(mocker: MockFixture) -> GitlabHttpClient:
    return cast(GitlabHttpClient, mocker.create_autospec(GitlabHttpClient))


@pytest.fixture()
def mocked_tokenizer_client(mocker: MockFixture) -> TokenizerClient:
    return cast(TokenizerClient, mocker.create_autospec(TokenizerClient))


@pytest.fixture()
def test_tokenizer_client_settings_factory(
    initiator: Optional[str], remote_key: Optional[str], remote_key_name: Optional[str], faker: Faker
) -> Callable[[], TokenizerClientSettings]:
    def get_tokenizer_settings():
        return TokenizerClientSettings(
            enabled=True,
            url=f"http://{faker.word()}.com",
            initiator=initiator,
            remote_key=remote_key,
            remote_key_name=remote_key_name,
        )

    return get_tokenizer_settings


@pytest.fixture()
def test_gitlab_publisher_with_default_reviewers(
    test_file_settings: OverhaveFileSettings,
    test_project_settings: OverhaveProjectSettings,
    test_gitlab_publisher_settings_with_default_reviewers: OverhaveGitlabPublisherSettings,
    mocked_file_manager: FileManager,
    mocked_git_initializer: GitRepositoryInitializer,
    mocked_gitlab_client: GitlabHttpClient,
    mocked_tokenizer_client: TokenizerClient,
    mocker: MockFixture,
) -> GitlabVersionPublisher:
    return GitlabVersionPublisher(
        file_settings=test_file_settings,
        project_settings=test_project_settings,
        feature_storage=mocker.create_autospec(IFeatureStorage),
        scenario_storage=mocker.create_autospec(IScenarioStorage),
        test_run_storage=mocker.create_autospec(ITestRunStorage),
        draft_storage=mocker.create_autospec(IDraftStorage),
        file_manager=mocked_file_manager,
        git_initializer=mocked_git_initializer,
        gitlab_publisher_settings=test_gitlab_publisher_settings_with_default_reviewers,
        gitlab_client=mocked_gitlab_client,
        tokenizer_client=mocked_tokenizer_client,
    )


@pytest.fixture()
def test_gitlab_publisher_with_reviewers_mapping(
    test_file_settings: OverhaveFileSettings,
    test_project_settings: OverhaveProjectSettings,
    test_gitlab_project_settings_with_reviewers_mapping: OverhaveGitlabPublisherSettings,
    mocked_file_manager: FileManager,
    mocked_git_initializer: GitRepositoryInitializer,
    mocked_gitlab_client: GitlabHttpClient,
    mocked_tokenizer_client: TokenizerClient,
    mocker: MockFixture,
) -> GitlabVersionPublisher:
    return GitlabVersionPublisher(
        file_settings=test_file_settings,
        project_settings=test_project_settings,
        feature_storage=mocker.create_autospec(IFeatureStorage),
        scenario_storage=mocker.create_autospec(IScenarioStorage),
        test_run_storage=mocker.create_autospec(ITestRunStorage),
        draft_storage=mocker.create_autospec(IDraftStorage),
        file_manager=mocked_file_manager,
        git_initializer=mocked_git_initializer,
        gitlab_publisher_settings=test_gitlab_project_settings_with_reviewers_mapping,
        gitlab_client=mocked_gitlab_client,
        tokenizer_client=mocked_tokenizer_client,
    )
