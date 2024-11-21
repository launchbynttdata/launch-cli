# Launch CLI

Simple CLI utility for common Launch tasks. This is intended to be built upon as new tasks are discovered.

## Prerequisites

- Python 3.11+ and pip
- A GitHub account

## Getting Started

To use this tool, you will need to create a GitHub Personal Access Token (PAT) if you have not already done so.

The PAT must be provided to this script through the `GITHUB_TOKEN` environment variable. Alternate credential stores are planned but not yet supported.

### Generating a PAT

To generate a PAT that includes the necessary rights for `launch-cli`, follow [our instructions here](./docs/generating-a-token.md).

More information on GitHub PATs can be found [here](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens).

## Installation

There are two paths you can take to install, your choice will depend on what you intend to do with `launch-cli`. If you intend to use the tool's built-in commands as part of your normal role as a Launch engineer (this is the most common option), you should perform the **End User Installation** below. If you intend to develop additional features for `launch-cli`, please follow the **Development Installation** below.

For either case, you will need to have Python 3.11 or greater installed on your system. How you choose to install that is up to you, but the installation steps assume you have an executable called `python3.11` in your path and the `pip` module installed.

### End User Installation

1. Issue the following command to install the latest version:

```sh
python3.11 -m pip install launch-cli
```

2. You can now use the `launch` command family from your CLI. Issue `launch --help` to confirm the launch command is available in your shell.

In the unlikely event that you need to install a specific version of `launch-cli` you may specify a version found on our [releases page](https://github.com/launchbynttdata/launch-cli/releases):

```sh
python3.11 -m pip install launch-cli==0.1.0
```

### Development Installation

1. Clone this repository to your machine and enter the repository's directory.
2. Create a new virtual environment and activate it:
      windows 11 - `py -m venv .venv` and `.venv\Scripts\activate`
      other OS - `python3.11 -m venv .venv && source .venv/bin/activate`
3. Issue the command `python3.11 -m pip install -e '.[dev]'` to create an editable installation.
4. You can now use the `launch` command family from your CLI, and changes made to most code should be available the next time you run the CLI command, but changes to the entrypoint or pyproject.toml may require that you issue the pip install command again to update the generated shortcut.

## Usage

Once installed, you can use the `launch` command from your shell. The `launch` command provides integrated help text, which can be viewed by issuing the `--help` flag, like so:

```sh
$ launch --help
Usage: launch [OPTIONS] COMMAND [ARGS]...

  Launch CLI tooling to help automate common tasks performed by Launch
  engineers and their clients.

Options:
  -v, --verbose  Increase verbosity of all subcommands
  --help         Show this message and exit.

Commands:
  github  Command family for GitHub-related tasks.
  ...
```

We started with a group of commands under `github`, but you should expect the list of available commands to grow as the tooling expands to cover more of our use cases. To dig into the commands (or subgroups) available, you may issue the `--help` flag on a subcommand in the same way to explore a group of commands:

```sh
$ launch github --help
Usage: launch github [OPTIONS] COMMAND [ARGS]...

  Command family for GitHub-related tasks.

Options:
  --help  Show this message and exit.

Commands:
  access   Command family for dealing with GitHub access.
  hooks    Command family for dealing with GitHub webhooks.
  version  Command family for dealing with GitHub versioning.
```

One very important thing to keep in mind is that options correspond to the group or command and cannot be issued in arbitrary places in the command. To use the `--verbose` flag to increase the output, you must place it following the `launch` command and before any subcommands, as shown below:

```sh
launch --verbose github access ...
```

### Service Family Usage

The service family of commands represents all the automation needed for the lifecycle management of a service built and used with the Launch platform.

`launch service create`: command is used to create a new service for the launch platform. This will create a new repository to the standard needed to run on the launch platform. This will be a properties driven only repository.

Example command use:
```sh
$ launch service create --name my-service --in-file ~/workplace/data/launch_az_inputs.json
```

`launch service update`: command updates a service repository with the new supplied --in-file. This command is used if you have added new environments, pipelines resources, or other aspects outside of service configuration. Updating service configs, such as *.tfvars, should be handled through your normal SCM tool such as `git`. If for example, you want to add a new instance, this would be the correct command.

Example command use:
```sh
$ launch service update --name my-service --in-file  ~/workplace/data/launch_az_inputs.json --git-message 'adding instance 001'
```

`launch service generate`: command to generate a service from a skeleton repository in you .launch_config file. From this defined skeleton repository based on jinja2 templates, this will dynamically generate a repository with this skeleton rendered with the --name service repository properties. This will create a new directory with the prefix `<service_name>-singleRun`.

Example command use:
```sh
$ launch service generate --name my-service --service-branch feature/init
```

`launch service cleanup`: command to clean up launch platform generated files. This will remove any directories or files created from the 'launch service generate' command.

Example command use:
```sh
$ launch service cleanup --name my-service
```

### Terragrunt Family Usage

The terragrunt family of commands includes all the automation needed for the lifecycle management of a service deployed with terragrunt from a Launch platform based repository.

All terragrunt family commands accept the same command arguments:
```sh
launch terragrunt plan --help
Usage: launch terragrunt plan [OPTIONS]

  Runs terragrunt plan against a git repository and its properties repo.

Options:
  --organization TEXT        GitHub organization containing your repository.
                             Defaults to the launchbynttdata organization.
  --name TEXT                Name of the service repository to run the
                             terragrunt command against.  [required]
  --git-token TEXT           The git token to use to clone the repositories.
                             This defaults to the GIT_TOKEN environment
                             variable.  [required]
  --commit-sha TEXT          The commit SHA or branch to checkout in the
                             repository.
  --target-environment TEXT  The target environment to run the terragrunt
                             command against. Defaults to sandbox.
  --provider-config TEXT     Provider config is used for any specific config
                             needed for certain providers. For example, AWS
                             needs additional parameters to assume a
                             deployment role. e.x {'provider':'aws','aws':{'ro
                             le_arn':'arn:aws:iam::012345678912:role/myRole'}}
                             [required]
  --skip-git                 If set, it will ignore cloning and checking out
                             the git repository and it's properties.
  --skip-generation          If set, it will ignore generating the terragrunt
                             files.
  --skip-diff                If set, it will ignore checking the diff between
                             the pipeline and service changes.
  --pipeline-resource TEXT   If set, this will un terragrunt against the
                             specified pipeline resource. For example, setting
                             this to 'pipeline' will run terragrunt against
                             pipeline resources, 'webhooks' will run
                             terragrunt against webhooks if this services uses
                             them. This defaults to None, which will tell the
                             command to run the terragrunt command against the
                             service resources
  --path TEXT                Working directory path. Defaults to current
                             working directory.
  --override DICT            This is used to override the default values for
                             various parameters. These are used for various
                             use cases but you shouldn't have to change these.
                             e.x {'infrastructure_dir':'platform/pipeline','en
                             vironment_dir':'platform/service','properties_suf
                             fix':'properties','main_branch':'main','machine':
                             'github.com','login':'nobody','tool_versions_file
                             ':'.tool-versions'}
  --dry-run                  Perform a dry run that reports on what it would
                             do, but does not perform any action.
  --help                     Show this message and exit.
```

Within each of the terragrunt commands, there are a couple of arguments that help expand and customize the way terragrunt runs.

The first flag '--provider-config' accepts a string based dict. Each cloud provider is slightly different in order to deploy and manage resources through terragrunt. This flag allows to provide customized parameters to successfully deploy the service to that cloud provider. This is a required parameter.

Aws example:
```sh
'{
  "provider":"aws"
  "aws": {
    "role_arn": string [Required]
  }
}'
```

Azure Example:
```sh
'{
  "provider":"az"
  "az": {
    "container_name": string [Optional]
    "storage_account_name": string [Optional]
    "resource_group_name": string [Optional]
  }
}'
```

Another flag '--pipeline-resource' defines a pipeline resource to run terragrunt plane against. If this is not provided, it will default to run terragrunt against the service resources itself. Setting this to 'pipeline' will run terragrunt against resources to manage the pipeline. The value 'webhooks' will deploy webhook resources if needed, etc.

Example:
```sh
--pipeline-resource 'pipeline'
```

The flag '--override' provides advance functionality to modify the way terragrunt runs. It allows overriding directories, main branch names, netrc, and .tool-version file name. These options are here for unique use cases that the majority of users will not need to modify.

`launch terragrunt plan`: command to run terragrunt plan actions against a launch platform service.

Example command use:
```sh
$ launch terragrunt plan --name my-service --commit-sha "feature/init" --target-environment "sandbox" --provider-config '{"provider":"az"}' --skip-git
```

`launch terragrunt apply`: command to run terragrunt plan actions against a launch platform service.

Example command use:
```sh
$ launch terragrunt plan --name my-service --target-environment "sandbox" --provider-config '{"provider":"az"}'
```

`launch terragrunt destroy`: command to run terragrunt plan actions against a launch platform service.

Example command use:
```sh
$ launch terragrunt plan --name my-service --target-environment "sandbox" --provider-config '{"provider":"az"}'
```
