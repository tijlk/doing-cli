import os
import click

from rich.console import Console
from rich.table import Table

from doing.commands import cmd_list, cmd_workon
from doing.utils import get_config, get_repo_name, run_command, get_az_devop_user_email
from doing.devops import get_iterations


console = Console()

@click.group()
def cli():
    pass

def common_options(function):
    """
    Custom decorator to avoid repeating commonly used options.
    """
    function = click.option('--team', required=True, type=str, default=lambda: get_config('team'), help="The code of the team in azure")(function)
    function = click.option('--area', required=True, type=str, default=lambda: get_config('area'), help="The area code")(function)
    function = click.option('--iteration', required=True, type=str, default=lambda: get_config('iteration'), help="The current iteration (sprint)")(function)
    function = click.option('--organization', required=True, type=str, default=lambda: get_config('organization'), help="The organization in azure")(function)
    function = click.option('--project', required=True, type=str, default=lambda: get_config('project'), help="The project in azure")(function)
    return function


@cli.command()
@common_options
def list(team, area, iteration, organization, project):
    """
    List issues related to the project.
    """
    cmd_list(team, area, iteration, organization, project)


@cli.group()
def open():
    """
    Quickly open certain links
    """
    pass

@open.command()
@common_options
def board(team, area, iteration, organization, project):
    """
    Open board view
    """
    console.print(f"Opening the Azure board. Make sure to filter on:")

    iteration_short = os.path.basename(iteration.replace('\\','/'))
    area_short = os.path.basename(area.replace('\\','/')) 
    console.print(f"\titeration = '{iteration_short}'")
    console.print(f"\tarea = '{area_short}'")
    
    click.launch(f"{organization}/{project}/_boards/board/t/{team}")

@open.command()
@common_options
def sprint(team, area, iteration, organization, project):
    """
    Open current sprint view
    """
    iteration = os.path.basename(iteration.replace('\\','/'))
    click.launch(f"{organization}/{project}/_sprints/taskboard/{team}/{iteration}")

@open.command()
@common_options
def repo(team, area, iteration, organization, project):
    """
    Open repo view
    """
    click.launch(f"{organization}/{project}/_git/{get_repo_name()}")

@open.command()
@common_options
def prs(team, area, iteration, organization, project):
    """
    Open active PRs for repository view
    """
    click.launch(f"{organization}/{project}/_git/{get_repo_name()}/pullrequests?_a=active")

@open.command()
@common_options
def pipe(team, area, iteration, organization, project):
    """
    Open latest pipeline runs for repository view
    """

    repo_pipes = run_command(f"az pipelines list --repository {get_repo_name()}")
    if len(repo_pipes) == 0:
        console.print(f"{get_repo_name()} has no pipelines defined currently")
        return None
    
    pipeline_id = repo_pipes[0].get('id')    
    click.launch(f"{organization}/{project}/_build?definitionId={pipeline_id}")


@open.command()
@common_options
@click.argument('issue_id')
def issue(team, area, iteration, organization, project, issue_id):
    """
    Open a specific ISSUE_ID.
    
    ISSUE_ID is the ID number of a work item.
    """
    click.launch(f"{organization}/{project}/_workitems/edit/{issue_id}")


@open.command()
@common_options
@click.argument('pullrequest_id')
def pr(team, area, iteration, organization, project, pullrequest_id):
    """
    Open a specific PULLREQUEST_ID.
    """
    click.launch(f"{organization}/{project}/_git/{get_repo_name()}/pullrequest/{pullrequest_id}")


@open.command()
@common_options
@click.argument('branch_name')
def branch(team, area, iteration, organization, project, branch_name):
    """
    Open a specific BRANCH_NAME.
    """
    click.launch(f"{organization}/{project}/_git/{get_repo_name()}?version=GB{branch_name}")








@cli.command()
@click.argument('issue', required=True, type=str)
@click.option('--type', required=True, default="User Story", type=click.Choice(['Bug','Epic','Feature','Issue','Task','Test Case','User Story']), help="Type of work item. Defaults to 'User Story'")
@click.option('--assigned_to', required=True, default=lambda: get_az_devop_user_email(), help="Emailadres of person to assign the issue to. Defaults to yourself.")
@common_options
def workon(
        issue, type, assigned_to,
        team, area, iteration, organization, project
    ):
    """
    Work on a new work item. Creates a new work item on Azure DevOps.
    
    ISSUE is the title to be used for the new work item.
    """
    cmd_workon(issue, type, assigned_to, team, area, iteration, organization, project)


# @cli.command()
# @click.option('--vpn', required=False, default=False, type=bool, help="Use when connected to ING's VPN, sets REQUESTS_CA_BUNDLE env var.")
# def check(vpn):
#     """Checks config and connection."""
#     # TODO: check organization
#     # TODO: check project
#     # TODO: check inside a git repo
#     # TODO: determine team is set
#     # TODO: determine area path is set, otherwise show options
#     # TODO: determine iteration is set, otherwise show options
#     repos = run_command("az repos list")
#     console.print(f":white_check_mark: Connection to dev.azure.com is OK! You have access to [white]{len(repos)}[/white] repos.")
    


@cli.command()
def nothing():
    """Take a break."""
    console.print(":pile_of_poo:")

# @cli.command()
# def create_pr():
#     """
#     Create a new pull request for the current branch
#     """
#     pass
    # TODO: assert not on master branch
    # TODO: get issue number from branch namem, otherwise request.
    # ado create_pr --reviewer="daniel.timbrell@ing.com"
    # > created pull request to merge origin/12341-make-an-update-to-the-readme into master
    # > Added your own approval
    # > Added daniel.timbrell@ing.com as a reviewer



# az boards work-item create --title "Test from tim's command line" --type "User Story"
# az boards work-item show --id 37222 --organization https://dev.azure.com/IngEurCDaaS01
