from launch.lib.github import hooks


def test_hooks_create_hook(mocker):
    repo = mocker.MagicMock()

    repo.name = "launch-test-repo"
    repo.url = "https://launch-test-repo.url"

    hooks.create_hook(
        repo=repo,
        name="web",
        config={"url": "https://launch-test-webhook.url"},
        events=["push"],
        active=True,
        dry_run=False,
    )
    repo.create_hook.assert_called_once()


def test_create_hook_dry_run(mocker):
    repo = mocker.MagicMock()

    repo.name = "launch-test-repo"
    repo.url = "https://launch-test-repo.url"

    hooks.create_hook(
        repo=repo,
        name="web",
        config={"url": "https://launch-test-webhook.url"},
        events=["push"],
        active=True,
        dry_run=True,
    )
    repo.create_hook.assert_not_called()
