import os
from pathlib import Path

import click
from git import Repo

from launch.cli.common.options.aws import (
    aws_deployment_region,
    aws_deployment_role,
    aws_secrets_profile,
    aws_secrets_region,
)
from launch.cli.github.auth.commands import application
from launch.cli.service.generate import generate
from launch.config.aws import AWS_LAMBDA_CODEBUILD_ENV_VAR_FILE
from launch.config.common import BUILD_TEMP_DIR_PATH, PLATFORM_SRC_DIR_PATH
from launch.config.github import (
    APPLICATION_ID_PARAMETER_NAME,
    DEFAULT_TOKEN_EXPIRATION_SECONDS,
    INSTALLATION_ID_PARAMETER_NAME,
    SIGNING_CERT_SECRET_NAME,
)
from launch.config.launchconfig import SERVICE_MAIN_BRANCH
from launch.config.terragrunt import PLATFORM_ENV, TARGETENV, TERRAGRUNT_RUN_DIRS
from launch.config.webhook import WEBHOOK_GIT_REPO_URL
from launch.constants.launchconfig import LAUNCHCONFIG_NAME
from launch.enums.launchconfig import LAUNCHCONFIG_KEYS
from launch.lib.automation.common.functions import single_true
from launch.lib.automation.environment.functions import (
    install_tool_versions,
    set_netrc,
    set_vars_from_bash_Var_file,
)
from launch.lib.automation.provider.aws.functions import assume_role
from launch.lib.automation.terragrunt.functions import (
    copy_webhook,
    find_app_templates,
    terragrunt_apply,
    terragrunt_destroy,
    terragrunt_init,
    terragrunt_plan,
)
from launch.lib.common.utilities import extract_repo_name_from_url
from launch.lib.github.auth import read_github_token


@click.command()
@aws_deployment_role
@aws_deployment_region
@aws_secrets_region
@aws_secrets_profile
@click.option(
    "--url",
    help="(Optional) The URL of the repository to clone.",
)
@click.option(
    "--tag",
    default=SERVICE_MAIN_BRANCH,
    help=f"(Optional) The tag of the repository to clone. Defaults to {SERVICE_MAIN_BRANCH}",
)
@click.option(
    "--target-environment",
    default=TARGETENV,
    help=f"(Optional) The target environment to run the terragrunt command against. Defaults to {TARGETENV}.",
)
@click.option(
    "--platform-env",
    default=PLATFORM_ENV,
    help=f"(Optional) The target environment to run the terragrunt command against. Defaults to {PLATFORM_ENV}.",
)
@click.option(
    "--platform-resource",
    default="all",
    help="(Optional) If set, this will set the specified pipeline resource to run terragrunt against. Defaults to all.  accepted values are 'pipeline', 'webhooks', 'service', or 'all'",
)
@click.option(
    "--generation",
    is_flag=True,
    default=False,
    help="(Optional) If set, it will generate the terragrunt files.",
)
@click.option(
    "--check-diff",
    is_flag=True,
    default=False,
    help="(Optional) If set, it will check the diff between the pipeline and service changes.",
)
@click.option(
    "--render-app-vars",
    is_flag=True,
    default=False,
    help="(Optional) If set, it will render the app var jinja templates and injects them into the terraform tfvars for use. Defaults to False.",
)
@click.option(
    "--plan",
    is_flag=True,
    default=False,
    help="(Optional) If set, this will run terragrunt plan. Defaults to False.",
)
@click.option(
    "--apply",
    is_flag=True,
    default=False,
    help="(Optional) If set, this will run terragrunt apply. Defaults to False.",
)
@click.option(
    "--destroy",
    is_flag=True,
    default=False,
    help="(Optional) If set, this will run terragrunt destroy. Defaults to False.",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="(Optional) Perform a dry run that reports on what it would do, but does not perform any action.",
)
@click.pass_context
def terragrunt(
    context: click.Context,
    aws_deployment_role: str,
    aws_deployment_region: str,
    aws_secrets_region: str,
    aws_secrets_profile: str,
    url: str,
    tag: str,
    target_environment: str,
    platform_env: str,
    platform_resource: dict,
    generation: bool,
    check_diff: bool,
    render_app_vars: bool,
    plan: bool,
    apply: bool,
    destroy: bool,
    dry_run: bool,
) -> None:
    """
    Runs terragrunt against a git repository set up to be ran with launch-cli.

    Args:
        context (click.Context): The context object passed from click.
        aws_deployment_role (str): The AWS deployment role to assume.
        aws_deployment_region (str): The AWS deployment region to assume.
        aws_secrets_region (str): The AWS region to use for secrets retrieval.
        aws_secrets_profile (str): The AWS profile to use for secrets retrieval.
        url (str): The URL of the repository to clone.
        tag (str): The tag of the repository to clone.
        target_environment (str): The target environment to run the terragrunt command against.
        platform_env (str): The target environment to run the terragrunt command against.
        platform_resource (dict): If set, this will set the specified pipeline resource to run terragrunt against.
        generation (bool): If set, it will generate the terragrunt files.
        check_diff (bool): If set, it will check the diff between the pipeline and service changes.
        render_app_vars (bool): If set, it will render the app var jinja templates and injects them into the terraform tfvars for use.
        plan (bool): If set, this will run terragrunt plan.
        apply (bool): If set, this will run terragrunt apply.
        destroy (bool): If set, this will run terragrunt destroy.
        dry_run (bool): Perform a dry run that reports on what it would do, but does not perform

    Returns:
        None
    """

    if dry_run:
        click.secho("Performing a dry run, nothing will be ran", fg="yellow")

    if not single_true(
        [
            plan,
            apply,
            destroy,
        ]
    ):
        message = (
            "You must specify one of the following flags: --plan, --apply, --destroy"
        )
        click.secho(message, fg="red")
        raise RuntimeError(message)

    if (
        APPLICATION_ID_PARAMETER_NAME
        and INSTALLATION_ID_PARAMETER_NAME
        and SIGNING_CERT_SECRET_NAME
    ):
        token = context.invoke(
            application,
            application_id_parameter_name=APPLICATION_ID_PARAMETER_NAME,
            installation_id_parameter_name=INSTALLATION_ID_PARAMETER_NAME,
            signing_cert_secret_name=SIGNING_CERT_SECRET_NAME,
            token_expiration_seconds=DEFAULT_TOKEN_EXPIRATION_SECONDS,
        )
    else:
        token = read_github_token()

    set_netrc(
        password=token,
        dry_run=dry_run,
    )

    if not url:
        if not Path(LAUNCHCONFIG_NAME).exists():
            if not Path(AWS_LAMBDA_CODEBUILD_ENV_VAR_FILE).exists():
                click.secho(
                    f"No {LAUNCHCONFIG_NAME} found or a {AWS_LAMBDA_CODEBUILD_ENV_VAR_FILE}. Please rerun command with appropriate {LAUNCHCONFIG_NAME},{AWS_LAMBDA_CODEBUILD_ENV_VAR_FILE}, --in-file, or --url",
                    fg="red",
                )
                return
            else:
                set_vars_from_bash_Var_file(AWS_LAMBDA_CODEBUILD_ENV_VAR_FILE)
                temp_url = os.environ.get("GIT_SERVER_URL")
                temp_org = os.environ.get("GIT_ORG")
                temp_repo = os.environ.get("GIT_REPO")
                url = f"{temp_url}/{temp_org}/{temp_repo}.git"
                tag = os.environ.get("MERGE_COMMIT_ID")

    if url:
        build_path = (
            Path()
            .cwd()
            .joinpath(
                f"{extract_repo_name_from_url(url)}/{BUILD_TEMP_DIR_PATH}/{extract_repo_name_from_url(url)}"
            )
        )
    else:
        build_path = (
            Path()
            .cwd()
            .joinpath(
                f"{BUILD_TEMP_DIR_PATH}/{extract_repo_name_from_url(Repo(Path().cwd()).remotes.origin.url)}"
            )
        )

    webhooks_path = (
        Path()
        .cwd()
        .joinpath(
            f"{BUILD_TEMP_DIR_PATH}/{extract_repo_name_from_url(WEBHOOK_GIT_REPO_URL)}"
        )
    )

    if check_diff:
        os.chdir(build_path)
        # TODO: Implement this function. Requires to pass the commit_id which comes
        # from set_vars.sh. Need to implement a way to pass this value to the function.
        # is_platform_git_changes(
        #     repository= Repo(build_path),
        #     commit_id=,
        #     directory=build_path,
        # )

    if generation:
        input_data = context.invoke(
            generate,
            url=url,
            tag=tag,
            dry_run=dry_run,
        )

    install_tool_versions()

    # If the Provider is AZURE there is a prequisite requirement of logging into azure
    # i.e. az login, or service principal is already applied to the environment.
    # If the provider is AWS, we need to assume the role for deployment.
    if aws_deployment_role:
        assume_role(
            aws_deployment_role=aws_deployment_role,
            aws_deployment_region=aws_deployment_region,
            profile=input_data["accounts"][target_environment],
        )

    run_dirs = []
    if platform_resource == "all":
        run_dirs = [
            TERRAGRUNT_RUN_DIRS["service"].joinpath(target_environment),
            TERRAGRUNT_RUN_DIRS["pipeline"].joinpath(platform_env),
            TERRAGRUNT_RUN_DIRS["webhook"].joinpath(platform_env),
        ]
    elif platform_resource in TERRAGRUNT_RUN_DIRS:
        run_dirs = [TERRAGRUNT_RUN_DIRS[platform_resource].joinpath(target_environment)]

    for run_dir in run_dirs:
        if not (build_path.joinpath(run_dir)).exists():
            message = f"Error: Path {build_path.joinpath(run_dir)} does not exist."
            click.secho(message, fg="red")
            raise FileNotFoundError(message)

    if (
        render_app_vars
        and TERRAGRUNT_RUN_DIRS["service"].joinpath(target_environment) in run_dirs
    ):
        find_app_templates(
            context=context,
            base_dir=build_path.joinpath(
                TERRAGRUNT_RUN_DIRS["service"].joinpath(target_environment)
            ),
            template_dir=build_path.joinpath(
                f"{PLATFORM_SRC_DIR_PATH}/{LAUNCHCONFIG_KEYS.TEMPLATES.value}"
            ),
            aws_profile=aws_secrets_profile,
            aws_region=aws_secrets_region,
            dry_run=dry_run,
        )

    if TERRAGRUNT_RUN_DIRS["webhook"].joinpath(target_environment) in run_dirs:
        copy_webhook(
            webhooks_path=webhooks_path,
            build_path=build_path,
            target_environment=target_environment,
            dry_run=dry_run,
        )

    for run_dir in run_dirs:
        tg_dir = build_path.joinpath(run_dir)
        if not (tg_dir).exists():
            message = f"Error: Path {tg_dir} does not exist."
            click.secho(message, fg="red")
            raise FileNotFoundError(message)
        os.chdir(tg_dir)
        terragrunt_init(
            dry_run=dry_run,
        )
        if plan:
            terragrunt_plan(
                dry_run=dry_run,
            )
        elif apply:
            terragrunt_apply(
                dry_run=dry_run,
            )
        elif destroy:
            terragrunt_destroy(
                dry_run=dry_run,
            )
