import click
import os
from pathlib import Path
from git import Repo

from launch.config.common import IS_PIPELINE
from launch.cli.common.options import (
    deployment_region,
)
from launch.cli.common.options.aws import (
    aws_deployment_role,
    aws_secrets_profile,
    aws_secrets_region,
)
from launch.cli.github.auth.commands import application
from launch.cli.service.generate import generate
from launch.config.aws import AWS_LAMBDA_CODEBUILD_ENV_VAR_FILE
from launch.config.common import BUILD_TEMP_DIR_PATH, PLATFORM_SRC_DIR_PATH
from launch.config.container import (
    CONTAINER_IMAGE_NAME,
    CONTAINER_IMAGE_VERSION,
    CONTAINER_REGISTRY,
)
from launch.config.github import (
    DEFAULT_TOKEN_EXPIRATION_SECONDS,
    GITHUB_APPLICATION_ID,
    GITHUB_INSTALLATION_ID,
    GITHUB_SIGNING_CERT_SECRET_NAME,
)
from launch.config.launchconfig import SERVICE_MAIN_BRANCH
from launch.config.terragrunt import TARGETENV, TERRAGRUNT_RUN_DIRS
from launch.config.webhook import WEBHOOK_GIT_REPO_URL
from launch.constants.launchconfig import LAUNCHCONFIG_NAME
from launch.enums.launchconfig import LAUNCHCONFIG_KEYS
from launch.lib.automation.common.functions import is_platform_git_changes, single_true
from launch.lib.automation.environment.functions import (
    install_tool_versions,
    readFile,
    set_netrc,
)
from launch.lib.automation.processes.functions import git_config
from launch.lib.automation.provider.aws.functions import assume_role
from launch.lib.automation.provider.az.functions import deploy_remote_state
from launch.lib.automation.terragrunt.functions import (
    copy_webhook,
    create_tf_auto_file,
    find_app_templates,
    terragrunt_apply,
    terragrunt_destroy,
    terragrunt_init,
    terragrunt_plan,
)
from launch.lib.common.utilities import (
    extract_repo_name_from_url,
)
from launch.lib.github.auth import read_github_token
from launch.lib.service.common import load_launchconfig
from launch.lib.service.template.launchconfig import LaunchConfigTemplate


@click.command()
@aws_deployment_role
@deployment_region
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
    "--platform-resource",
    default="service",
    help="(Optional) If set, this will set the specified pipeline resource to run terragrunt against. Defaults to service.  accepted values are 'pipeline', 'webhook', or 'service'",
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
    deployment_region: str,
    aws_secrets_region: str,
    aws_secrets_profile: str,
    url: str,
    tag: str,
    target_environment: str,
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
        deployment_region (str): The deployment region to deploy to.
        aws_secrets_region (str): The AWS region to use for secrets retrieval.
        aws_secrets_profile (str): The AWS profile to use for secrets retrieval.
        url (str): The URL of the repository to clone.
        tag (str): The tag of the repository to clone.
        target_environment (str): The target environment to run the terragrunt command against.
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
        GITHUB_APPLICATION_ID
        and GITHUB_INSTALLATION_ID
        and GITHUB_SIGNING_CERT_SECRET_NAME
    ):
        token = context.invoke(
            application,
            application_id_parameter_name=GITHUB_APPLICATION_ID,
            installation_id_parameter_name=GITHUB_INSTALLATION_ID,
            signing_cert_secret_name=GITHUB_SIGNING_CERT_SECRET_NAME,
            token_expiration_seconds=DEFAULT_TOKEN_EXPIRATION_SECONDS,
        )
    else:
        token = read_github_token()

    set_netrc(
        password=token,
        dry_run=dry_run,
    )

    app_image_version = CONTAINER_IMAGE_VERSION
    if not url:
        if not Path(LAUNCHCONFIG_NAME).exists():
            if not Path(AWS_LAMBDA_CODEBUILD_ENV_VAR_FILE).exists():
                click.secho(
                    f"No {LAUNCHCONFIG_NAME} found or a {AWS_LAMBDA_CODEBUILD_ENV_VAR_FILE}. Please rerun command with appropriate {LAUNCHCONFIG_NAME},{AWS_LAMBDA_CODEBUILD_ENV_VAR_FILE}, --in-file, or --url",
                    fg="red",
                )
                return
            else:
                temp_server_url = readFile("GIT_SERVER_URL")
                temp_org = readFile("GIT_ORG")
                temp_repo = readFile("GIT_REPO")
                if not app_image_version:
                    app_image_version = readFile("CONTAINER_IMAGE_VERSION")
                url = f"{temp_server_url}/{temp_org}/{temp_repo}"
                tag = readFile("MERGE_COMMIT_ID")

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
        is_platform_git_changes(
            repository=Repo(build_path),
            commit_id=tag,
            directory=build_path,
        )

    if generation:
        input_data = context.invoke(
            generate,
            url=url,
            tag=tag,
            dry_run=dry_run,
        )
    else:
        input_data=load_launchconfig()

    install_tool_versions()
    if IS_PIPELINE:
        git_config(
            dry_run=dry_run
        )

    # If the Provider is AZURE there is a prequisite requirement of logging into azure 
    # i.e. az login, or service principal is already applied to the environment: az login; az account get-access-token
    # If the provider is AWS, we need to assume the role for deployment.
    
    provider = LaunchConfigTemplate(dry_run).get_provider(platform_resource, input_data)
    if provider == "aws":
        if aws_deployment_role:
            assume_role(
                aws_deployment_role=aws_deployment_role,
                aws_deployment_region=deployment_region,
                profile=input_data["accounts"][target_environment],
            )

    run_dirs = []
    if platform_resource in TERRAGRUNT_RUN_DIRS:
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
        tg_dir = build_path.joinpath(run_dir, deployment_region)
        if not (tg_dir).exists():
            message = f"Error: Path {tg_dir} does not exist."
            click.secho(message, fg="red")
            raise FileNotFoundError(message)
        os.chdir(tg_dir)
        for instance in os.scandir(tg_dir):
            if instance.is_dir():
                # If the Provider is AZURE we need to deploy the remote state
                if provider == "az" or provider == "ado":
                    if platform_resource == "service":
                        uuid_value = input_data["platform"][platform_resource][target_environment][deployment_region][instance.name][LAUNCHCONFIG_KEYS.UUID.value]
                    else:
                        uuid_value = input_data["platform"]["pipeline"][f"{platform_resource}-provider"][target_environment][deployment_region][instance.name][LAUNCHCONFIG_KEYS.UUID.value]
                    deploy_remote_state(
                        uuid_value = uuid_value,
                        naming_prefix = input_data["naming_prefix"],
                        target_environment = target_environment,
                        region = deployment_region,
                        instance = instance.name,
                        build_path = build_path,
                        dry_run = dry_run,
                    )
                if render_app_vars:
                    create_tf_auto_file(
                        data={
                            "app_image": f'"{CONTAINER_REGISTRY}/{CONTAINER_IMAGE_NAME}:{app_image_version}"',
                            "redeploy_on_apply": "true",
                            "force_new_deployment": "true",
                        },
                        out_file=tg_dir.joinpath(instance, "app_image.auto.tfvars"),
                        dry_run=dry_run,
                        )
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
