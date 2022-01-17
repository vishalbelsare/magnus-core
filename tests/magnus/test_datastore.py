import pytest

from magnus import datastore
from magnus import exceptions
from magnus import defaults


def test_data_catalog_eq_is_equal_if_name_is_same():
    this = datastore.DataCatalog(name='test')
    that = datastore.DataCatalog(name='test')

    assert this == that
    assert len(set([this, that])) == 1


def test_data_catalog_eq_is_not_equal_if_name_is_not_same():
    this = datastore.DataCatalog(name='test')
    that = datastore.DataCatalog(name='test1')

    assert this != that
    assert len(set([this, that])) == 2


def test_data_catalog_eq_is_not_equal_if_objs_are_not_same(mocker):
    this = datastore.DataCatalog(name='test')
    that = mocker.MagicMock()

    assert this != that
    assert len(set([this, that])) == 2


# Some of the base run log store tests are not unit tests as they trust the structure of pydantic BaseModel.
# I am intentionally allowing it as we are using them as containers and no actual functions are being called.

def test_branchlog_get_data_catalogs_by_state_raises_exception_for_incorrect_stage():
    branch_log = datastore.BranchLog(internal_name='test')
    with pytest.raises(Exception):
        branch_log.get_data_catalogs_by_stage(stage='notright')


def test_branchlog_calls_step_logs_catalogs(mocker):
    mock_step = mocker.MagicMock()
    mock_get_data_catalogs_by_stage = mocker.MagicMock()

    mock_step.get_data_catalogs_by_stage = mock_get_data_catalogs_by_stage

    branch_log = datastore.BranchLog(internal_name='test')
    branch_log.steps['test_step'] = mock_step

    branch_log.get_data_catalogs_by_stage(stage='put')

    mock_get_data_catalogs_by_stage.assert_called_once_with(stage='put')


def test_steplog_get_data_catalogs_by_state_raises_exception_for_incorrect_stage():
    step_log = datastore.StepLog(name='test', internal_name='test')
    with pytest.raises(Exception):
        step_log.get_data_catalogs_by_stage(stage='notright')


def test_steplog_get_data_catalogs_filters_by_stage(mocker):
    step_log = datastore.StepLog(name='test', internal_name='test')

    mock_data_catalog_put = mocker.MagicMock()
    mock_data_catalog_put.stage = 'put'
    mock_data_catalog_get = mocker.MagicMock()
    mock_data_catalog_get.stage = 'get'

    step_log.data_catalog = [mock_data_catalog_get, mock_data_catalog_put]

    assert step_log.get_data_catalogs_by_stage() == [mock_data_catalog_put]
    assert step_log.get_data_catalogs_by_stage(stage='get') == [mock_data_catalog_get]


def test_steplog_add_data_catalogs_inits_a_new_data_catalog():
    step_log = datastore.StepLog(name='test', internal_name='test')

    step_log.add_data_catalogs(data_catalogs=[])

    assert step_log.data_catalog == []


def test_steplog_add_data_catalogs_appends_to_existing_catalog():
    step_log = datastore.StepLog(name='test', internal_name='test')
    step_log.data_catalog = ['a']

    step_log.add_data_catalogs(data_catalogs=['b'])

    assert step_log.data_catalog == ['a', 'b']


def test_runlog_get_data_catalogs_by_state_raises_exception_for_incorrect_stage():
    run_log = datastore.RunLog(run_id='run_id')
    with pytest.raises(Exception):
        run_log.get_data_catalogs_by_stage(stage='notright')


def test_runlog_search_branch_by_internal_name_returns_run_log_if_internal_name_is_none():
    run_log = datastore.RunLog(run_id='run_id')

    branch, step = run_log.search_branch_by_internal_name(i_name=None)

    assert run_log == branch
    assert step is None


def test_step_log_get_data_catalogs_by_stage_gets_catalogs_from_branches(mocker, monkeypatch):
    mock_branch_log = mocker.MagicMock()
    mock_branch_log.get_data_catalogs_by_stage.return_value = ['from_branch']

    step_log = datastore.StepLog(name='test', internal_name='for_testing')

    step_log.branches['single_branch'] = mock_branch_log

    assert ['from_branch'] == step_log.get_data_catalogs_by_stage()


def test_step_log_get_data_catalogs_by_stage_adds_catalogs_from_branches_to_current_ones(mocker, monkeypatch):
    mock_branch_log = mocker.MagicMock()
    mock_branch_log.get_data_catalogs_by_stage.return_value = ['from_branch']

    mock_data_catalog = mocker.MagicMock()
    mock_data_catalog.stage = 'put'

    step_log = datastore.StepLog(name='test', internal_name='for_testing')

    step_log.branches['single_branch'] = mock_branch_log
    step_log.data_catalog = [mock_data_catalog]

    assert [mock_data_catalog, 'from_branch'] == step_log.get_data_catalogs_by_stage()


def test_run_log_get_data_catalogs_by_stage_gets_catalogs_from_steps(mocker, monkeypatch):
    mock_step = mocker.MagicMock()

    mock_step.get_data_catalogs_by_stage.return_value = ['data catalog']

    run_log = datastore.RunLog(run_id='test')
    run_log.steps = {'first_step': mock_step}

    data_catalogs = run_log.get_data_catalogs_by_stage('get')

    assert data_catalogs == ['data catalog']


def test_base_run_log_store_assigns_config():
    config = {'key': 'value'}

    run_log_store = datastore.BaseRunLogStore(config=config)

    assert run_log_store.config == config


def test_base_run_log_store_assigns_empty_config_if_none():
    config = None

    run_log_store = datastore.BaseRunLogStore(config=config)

    assert run_log_store.config == {}


def test_base_run_log_store_create_run_log_not_implemented():
    config = {'key': 'value'}

    run_log_store = datastore.BaseRunLogStore(config=config)
    with pytest.raises(NotImplementedError):
        run_log_store.create_run_log(run_id='will fail')


def test_base_run_log_store_get_run_log_by_id_not_implemented():
    config = {'key': 'value'}

    run_log_store = datastore.BaseRunLogStore(config=config)
    with pytest.raises(NotImplementedError):
        run_log_store.get_run_log_by_id(run_id='will fail')


def test_base_run_log_store_put_run_log_not_implemented():
    config = {'key': 'value'}

    run_log_store = datastore.BaseRunLogStore(config=config)
    with pytest.raises(NotImplementedError):
        run_log_store.put_run_log(run_log='will fail')


def test_base_run_log_set_parameters_creates_parameters_if_not_present_previously(mocker, monkeypatch):
    run_log = datastore.RunLog(run_id='testing')

    mock_get_run_log_by_id = mocker.MagicMock(return_value=run_log)
    mock_put_run_log = mocker.MagicMock()

    monkeypatch.setattr(datastore.BaseRunLogStore, 'get_run_log_by_id', mock_get_run_log_by_id)
    monkeypatch.setattr(datastore.BaseRunLogStore, 'put_run_log', mock_put_run_log)
    parameters = {'a': 1}

    run_log_store = datastore.BaseRunLogStore(config=None)
    run_log_store.set_parameters(run_id='testing', parameters=parameters)

    assert run_log.parameters == parameters
    mock_put_run_log.assert_called_once_with(run_log=run_log)


def test_base_run_log_set_parameters_updatesparameters_if_present_previously(mocker, monkeypatch):
    run_log = datastore.RunLog(run_id='testing')
    run_log.parameters = {'b': 2}
    mock_get_run_log_by_id = mocker.MagicMock(return_value=run_log)
    mock_put_run_log = mocker.MagicMock()

    monkeypatch.setattr(datastore.BaseRunLogStore, 'get_run_log_by_id', mock_get_run_log_by_id)
    monkeypatch.setattr(datastore.BaseRunLogStore, 'put_run_log', mock_put_run_log)
    parameters = {'a': 1}

    run_log_store = datastore.BaseRunLogStore(config=None)
    run_log_store.set_parameters(run_id='testing', parameters=parameters)

    assert run_log.parameters == {'a': 1, 'b': 2}
    mock_put_run_log.assert_called_once_with(run_log=run_log)


def test_base_run_log_store_get_parameters_gets_from_run_log(mocker, monkeypatch):
    run_log = datastore.RunLog(run_id='testing')
    run_log.parameters = {'b': 2}

    mock_get_run_log_by_id = mocker.MagicMock(return_value=run_log)

    monkeypatch.setattr(datastore.BaseRunLogStore, 'get_run_log_by_id', mock_get_run_log_by_id)

    run_log_store = datastore.BaseRunLogStore(config=None)
    assert run_log_store.get_parameters(run_id='testing') == {'b': 2}


def test_base_run_log_store_get_run_config_returns_config_from_run_log(mocker, monkeypatch):
    run_log = datastore.RunLog(run_id='testing')
    run_config = {'executor': 'for testing'}
    run_log.run_config = run_config

    mock_get_run_log_by_id = mocker.MagicMock(return_value=run_log)

    monkeypatch.setattr(datastore.BaseRunLogStore, 'get_run_log_by_id', mock_get_run_log_by_id)
    run_log_store = datastore.BaseRunLogStore(config=None)

    assert run_config == run_log_store.get_run_config(run_id='testing')


def test_base_run_log_store_set_run_config_creates_run_log_if_not_present(mocker, monkeypatch):
    run_log = datastore.RunLog(run_id='testing')

    mock_get_run_log_by_id = mocker.MagicMock(return_value=run_log)
    mock_put_run_log = mocker.MagicMock()
    run_config = {'executor': 'for testing'}

    monkeypatch.setattr(datastore.BaseRunLogStore, 'get_run_log_by_id', mock_get_run_log_by_id)
    monkeypatch.setattr(datastore.BaseRunLogStore, 'put_run_log', mock_put_run_log)

    run_log_store = datastore.BaseRunLogStore(config=None)
    run_log_store.set_run_config(run_id='testing', run_config=run_config)

    assert run_log.run_config == run_config
    mock_put_run_log.assert_called_once_with(run_log=run_log)


def test_base_run_log_store_set_run_config_updates_run_log_if_present(mocker, monkeypatch):
    run_log = datastore.RunLog(run_id='testing', run_config={'datastore': 'for testing'})

    mock_get_run_log_by_id = mocker.MagicMock(return_value=run_log)
    mock_put_run_log = mocker.MagicMock()
    run_config = {'executor': 'for testing'}

    monkeypatch.setattr(datastore.BaseRunLogStore, 'get_run_log_by_id', mock_get_run_log_by_id)
    monkeypatch.setattr(datastore.BaseRunLogStore, 'put_run_log', mock_put_run_log)

    run_log_store = datastore.BaseRunLogStore(config=None)
    run_log_store.set_run_config(run_id='testing', run_config=run_config)

    assert run_log.run_config == {'datastore': 'for testing', 'executor': 'for testing'}


def test_base_run_log_store_create_step_log_returns_a_step_log_object():
    run_log_store = datastore.BaseRunLogStore(config=None)

    step_log = run_log_store.create_step_log(name='test', internal_name='test')

    assert isinstance(step_log, datastore.StepLog)


def test_base_run_log_store_get_step_log_raises_step_log_not_found_error_if_search_fails(monkeypatch, mocker):
    mock_run_log = mocker.MagicMock()
    mock_run_log.search_step_by_internal_name.side_effect = exceptions.StepLogNotFoundError('test', 'test')

    run_log_store = datastore.BaseRunLogStore(config=None)
    run_log_store.get_run_log_by_id = mocker.MagicMock(return_value=mock_run_log)

    with pytest.raises(exceptions.StepLogNotFoundError):
        run_log_store.get_step_log(internal_name='test', run_id='test')


def test_base_run_log_store_get_step_log_returns_from_log_search(monkeypatch, mocker):
    mock_run_log = mocker.MagicMock()
    mock_step_log = mocker.MagicMock()
    mock_run_log.search_step_by_internal_name.return_value = mock_step_log, None

    run_log_store = datastore.BaseRunLogStore(config=None)
    run_log_store.get_run_log_by_id = mocker.MagicMock(return_value=mock_run_log)

    assert mock_step_log == run_log_store.get_step_log(internal_name='test', run_id='test')


def test_base_run_log_store_create_branch_log_returns_a_branch_log_object():
    run_log_store = datastore.BaseRunLogStore(config=None)

    branch_log = run_log_store.create_branch_log(internal_branch_name='test')

    assert isinstance(branch_log, datastore.BranchLog)


def test_base_run_log_store_create_attempt_log_returns_a_attempt_log_object():
    run_log_store = datastore.BaseRunLogStore(config=None)

    attempt_log = run_log_store.create_attempt_log()

    assert isinstance(attempt_log, datastore.StepAttempt)


def test_base_run_log_store_create_code_identity_object():
    run_log_store = datastore.BaseRunLogStore(config=None)

    code_identity = run_log_store.create_code_identity()

    assert isinstance(code_identity, datastore.CodeIdentity)


def test_base_run_log_store_create_data_catalog_object():
    run_log_store = datastore.BaseRunLogStore(config=None)

    data_catalog = run_log_store.create_data_catalog(name='data')

    assert isinstance(data_catalog, datastore.DataCatalog)


def test_base_run_log_store_add_step_log_adds_log_to_run_log_if_branch_is_none(mocker, monkeypatch):
    step_log = datastore.StepLog(name='test', internal_name='test')  #  step_log at root level

    mock_run_log = mocker.MagicMock()
    mock_run_log.search_branch_by_internal_name.return_value = None, None
    mock_run_log.steps = {}

    monkeypatch.setattr(datastore.BaseRunLogStore, 'get_run_log_by_id', mocker.MagicMock(return_value=mock_run_log))
    monkeypatch.setattr(datastore.BaseRunLogStore, 'put_run_log', mocker.MagicMock())

    run_log_store = datastore.BaseRunLogStore(config=None)

    run_log_store.add_step_log(step_log=step_log, run_id='test')
    assert mock_run_log.steps['test'] == step_log


def test_base_run_log_store_add_step_log_adds_log_to_run_log_if_branch_is_none(mocker, monkeypatch):
    step_log = datastore.StepLog(name='test', internal_name='test')  #  step_log at root level

    mock_run_log = mocker.MagicMock()
    mock_run_log.search_branch_by_internal_name.return_value = None, None
    mock_run_log.steps = {}

    monkeypatch.setattr(datastore.BaseRunLogStore, 'get_run_log_by_id', mocker.MagicMock(return_value=mock_run_log))
    monkeypatch.setattr(datastore.BaseRunLogStore, 'put_run_log', mocker.MagicMock())

    run_log_store = datastore.BaseRunLogStore(config=None)

    run_log_store.add_step_log(step_log=step_log, run_id='test')
    assert mock_run_log.steps['test'] == step_log


def test_base_run_log_store_add_step_log_adds_log_to_branch_log_if_branch_is_found(mocker, monkeypatch):
    step_log = datastore.StepLog(name='test', internal_name='test.branch.step')  #  step_log at branch level

    mock_run_log = mocker.MagicMock()
    mock_branch_log = mocker.MagicMock()
    mock_run_log.search_branch_by_internal_name.return_value = mock_branch_log, None
    mock_branch_log.steps = {}

    monkeypatch.setattr(datastore.BaseRunLogStore, 'get_run_log_by_id', mocker.MagicMock(return_value=mock_run_log))
    monkeypatch.setattr(datastore.BaseRunLogStore, 'put_run_log', mocker.MagicMock())

    run_log_store = datastore.BaseRunLogStore(config=None)

    run_log_store.add_step_log(step_log=step_log, run_id='test')
    assert mock_branch_log.steps['test.branch.step'] == step_log


def test_base_run_log_store_get_branch_log_returns_run_log_if_internal_branch_name_is_none(mocker, monkeypatch):
    mock_run_log = mocker.MagicMock()

    monkeypatch.setattr(datastore.BaseRunLogStore, 'get_run_log_by_id', mocker.MagicMock(return_value=mock_run_log))

    run_log_store = datastore.BaseRunLogStore(config=None)
    assert mock_run_log == run_log_store.get_branch_log(internal_branch_name=None, run_id='test')


def test_base_run_log_store_get_branch_log_returns_branch_log_if_internal_branch_name_is_given(mocker, monkeypatch):
    mock_run_log = mocker.MagicMock()
    mock_branch_log = mocker.MagicMock()

    mock_run_log.search_branch_by_internal_name.return_value = mock_branch_log, None

    monkeypatch.setattr(datastore.BaseRunLogStore, 'get_run_log_by_id', mocker.MagicMock(return_value=mock_run_log))

    run_log_store = datastore.BaseRunLogStore(config=None)
    assert mock_branch_log == run_log_store.get_branch_log(internal_branch_name='branch', run_id='test')


def test_base_run_log_store_add_branch_log_adds_run_log_if_sent(monkeypatch, mocker):
    mock_put_run_log = mocker.MagicMock()
    monkeypatch.setattr(datastore.BaseRunLogStore, 'put_run_log', mock_put_run_log)

    run_log = datastore.RunLog(run_id='test')

    run_log_store = datastore.BaseRunLogStore(config=None)

    run_log_store.add_branch_log(branch_log=run_log, run_id='test')

    mock_put_run_log.assert_called_once_with(run_log)


def test_base_run_log_add_branch_log_adds_branch_to_the_right_step(mocker, monkeypatch):
    branch_log = datastore.BranchLog(internal_name='test.branch.step')

    mock_run_log = mocker.MagicMock()
    mock_step = mocker.MagicMock()
    mock_step.branches = {}

    mock_put_run_log = mocker.MagicMock()
    monkeypatch.setattr(datastore.BaseRunLogStore, 'put_run_log', mock_put_run_log)
    monkeypatch.setattr(datastore.BaseRunLogStore, 'get_run_log_by_id', mocker.MagicMock(return_value=mock_run_log))

    mock_run_log.search_step_by_internal_name.return_value = mock_step, None

    run_log_store = datastore.BaseRunLogStore(config=None)

    run_log_store.add_branch_log(branch_log=branch_log, run_id='test')

    assert mock_step.branches['test.branch.step'] == branch_log


def test_buffered_run_log_store_inits_run_log_as_none():
    run_log_store = datastore.BufferRunLogstore(config=None)

    assert run_log_store.run_log is None


def test_buffered_run_log_store_create_run_log_creates_a_run_log_object():
    run_log_store = datastore.BufferRunLogstore(config=None)

    run_log = run_log_store.create_run_log(run_id='test')

    assert isinstance(run_log, datastore.RunLog)
    assert run_log.status == defaults.CREATED


def test_buffered_run_log_store_get_run_log_returns_the_run_log():
    run_log_store = datastore.BufferRunLogstore(config=None)

    run_log = datastore.RunLog(run_id='test')
    run_log.status = defaults.PROCESSING
    run_log_store.run_log = run_log

    r_run_log = run_log_store.get_run_log_by_id('test')
    assert r_run_log == run_log


def test_buffered_run_log_store_put_run_log_updates_the_run_log():
    run_log_store = datastore.BufferRunLogstore(config=None)

    run_log = datastore.RunLog(run_id='test')
    run_log_store.put_run_log(run_log=run_log)

    assert run_log == run_log_store.run_log

    r_run_log = run_log_store.get_run_log_by_id('test')
    assert r_run_log == run_log


def test_file_system_run_log_store_log_folder_name_defaults_if_not_provided():
    run_log_store = datastore.FileSystemRunLogstore(config=None)

    assert run_log_store.log_folder_name == defaults.LOG_LOCATION_FOLDER


def test_file_system_run_log_store_log_folder_name_if__provided():
    run_log_store = datastore.FileSystemRunLogstore(config={'log_folder': 'test'})

    assert run_log_store.log_folder_name == 'test'


def test_file_system_run_log_store_write_to_folder_makes_dir_if_not_present(mocker, monkeypatch):
    mock_safe_make_dir = mocker.MagicMock()
    monkeypatch.setattr(datastore.utils, 'safe_make_dir', mock_safe_make_dir)

    mock_json = mocker.MagicMock()
    mock_path = mocker.MagicMock()
    monkeypatch.setattr(datastore, 'json', mock_json)
    monkeypatch.setattr(datastore, 'Path', mock_path)

    mock_run_log = mocker.MagicMock()
    mock_dict = mocker.MagicMock()
    mock_run_log.dict = mock_dict

    run_log_store = datastore.FileSystemRunLogstore(config=None)
    run_log_store.write_to_folder(run_log=mock_run_log)

    mock_safe_make_dir.assert_called_once_with(run_log_store.log_folder_name)
    assert mock_dict.call_count == 1


def test_file_system_run_log_store_get_from_folder_raises_exception_if_folder_not_present(mocker, monkeypatch):
    mock_path = mocker.MagicMock()
    monkeypatch.setattr(datastore, 'Path', mocker.MagicMock(return_value=mock_path))

    mock_path.__truediv__.return_value = mock_path

    mock_path.exists.return_value = False

    run_log_store = datastore.FileSystemRunLogstore(config=None)

    with pytest.raises(FileNotFoundError):
        run_log_store.get_from_folder(run_id='test')


def test_file_system_run_log_store_get_from_folder_returns_run_log_from_file_contents(mocker, monkeypatch):
    mock_path = mocker.MagicMock()
    monkeypatch.setattr(datastore, 'Path', mocker.MagicMock(return_value=mock_path))

    mock_path.__truediv__.return_value = mock_path
    mock_path.exists.return_value = True

    mock_json = mocker.MagicMock()
    monkeypatch.setattr(datastore, 'json', mock_json)
    mock_json.load.return_value = {'run_id': 'test'}

    run_log_store = datastore.FileSystemRunLogstore(config=None)
    run_log = run_log_store.get_from_folder(run_id='does not matter')

    assert run_log.run_id == 'test'


def test_file_system_run_log_store_create_run_log_writes_to_folder(mocker, monkeypatch):
    mock_write_to_folder = mocker.MagicMock()

    monkeypatch.setattr(datastore.FileSystemRunLogstore, 'write_to_folder', mock_write_to_folder)

    run_log_store = datastore.FileSystemRunLogstore(config=None)
    run_log = run_log_store.create_run_log(run_id='test')

    mock_write_to_folder.assert_called_once_with(run_log)

    assert run_log.run_id == 'test'


def test_file_system_run_log_store_get_run_log_by_id_raises_exception_if_get_from_folder_fails(mocker, monkeypatch):
    mock_get_from_folder = mocker.MagicMock()
    mock_get_from_folder.side_effect = FileNotFoundError()

    monkeypatch.setattr(datastore.FileSystemRunLogstore, 'get_from_folder', mock_get_from_folder)

    run_log_store = datastore.FileSystemRunLogstore(config=None)
    with pytest.raises(exceptions.RunLogNotFoundError):
        run_log_store.get_run_log_by_id(run_id='should fail')


def test_file_system_run_log_store_get_run_log_by_id_returns_run_log_from_get_from_folder(mocker, monkeypatch):
    mock_get_from_folder = mocker.MagicMock()
    mock_get_from_folder.return_value = 'I am a run log'

    monkeypatch.setattr(datastore.FileSystemRunLogstore, 'get_from_folder', mock_get_from_folder)

    run_log_store = datastore.FileSystemRunLogstore(config=None)

    run_log = run_log_store.get_run_log_by_id(run_id='test')

    assert run_log == 'I am a run log'


def test_file_system_run_log_store_put_run_log_writes_to_folder(mocker, monkeypatch):
    mock_write_to_folder = mocker.MagicMock()

    monkeypatch.setattr(datastore.FileSystemRunLogstore, 'write_to_folder', mock_write_to_folder)

    run_log_store = datastore.FileSystemRunLogstore(config=None)
    mock_run_log = mocker.MagicMock()
    run_log_store.put_run_log(run_log=mock_run_log)

    mock_write_to_folder.assert_called_once_with(mock_run_log)
