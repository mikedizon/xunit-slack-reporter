import os
import sys
import pathlib
import app.constants as constants
import app.utils.xunit_utils as xunit_utils
import app.utils.slack_utils as slack_utils


def main():
    # Check input values.
    if constants.XUNIT_PATH_ENV_VAR not in os.environ:
        raise Exception(f"xunit file not found!  Please make sure to set the {constants.XUNIT_PATH_ENV_VAR} env variable!")

    if constants.SLACK_CHANNEL_ENV_VAR not in os.environ:
        raise Exception(f"Slack channel!  Please make sure to set the {constants.SLACK_CHANNEL_ENV_VAR} env variable!")

    if constants.SLACK_TOKEN_ENV_VAR not in os.environ:
        raise Exception(f"Slack channel!  Please make sure to set the {constants.SLACK_TOKEN_ENV_VAR} env variable!")

    if constants.SLACK_ATTACHMENT_AUTHOR_NAME_ENV_VAR not in os.environ:
        raise Exception(f"Slack channel!  Please make sure to set the {constants.SLACK_ATTACHMENT_AUTHOR_NAME_ENV_VAR} env variable!")

    # Load XUnit report
    try:
        xunit_path = os.getenv(constants.XUNIT_PATH_ENV_VAR)
        xunit_report = xunit_utils.read_xunit(pathlib.Path(xunit_path))
    except Exception as excep:
        raise Exception(f"Error loading xunit file!  Error: {excep}")

    # Slack results
    slack_attachment = {
        "color": constants.PASS_COLOR,
        "author_name": os.getenv(constants.SLACK_ATTACHMENT_AUTHOR_NAME_ENV_VAR),
        "author_link": f"https://github.com/{os.getenv('GITHUB_REPOSITORY')}/actions/runs/{os.getenv('GITHUB_RUN_ID')}",
        "title": f"XUnit test results for {os.getenv('GITHUB_WORKFLOW')} on {os.getenv('GITHUB_REF')}",
        "fields": []
    }

    if xunit_report.errors or xunit_report.failures:
        slack_attachment['color'] = constants.FAIL_COLOR

    slack_attachment['fields'].append({
        "title": "Total # of tests",
        "value": f"{xunit_report.tests}",
        "short": True
    })

    slack_attachment['fields'].append({
        "title": "Tests passed:",
        "value": f"{xunit_report.tests - xunit_report.errors - xunit_report.failures}",
        "short": True
    })

    slack_attachment['fields'].append({
        "title": "Tests errored:",
        "value": f"{xunit_report.errors}",
        "short": True
    })

    slack_attachment['fields'].append({
        "title": "Tests failed:",
        "value": f"{xunit_report.failures}",
        "short": True
    })

    slack_attachment['fields'].append({
        "title": "Time elapsed:",
        "value": f"{xunit_report.time} seconds",
        "short": True
    })

    slack_utils.send_slack_msg(
        os.getenv(constants.SLACK_CHANNEL_ENV_VAR),
        attachments=[slack_attachment]
    )

    # Return appropriate status code.
    if os.getenv("EXIT_CODE_FROM_REPORT"):
        if xunit_report.errors or xunit_report.failures:
            sys.exit(1)


if __name__ == "__main__":
    main()
