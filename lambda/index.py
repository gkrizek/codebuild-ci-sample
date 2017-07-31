import boto3
codebuild = boto3.client('codebuild')
from github3 import login
import os
import json
import sys


def handler(event, context):
    if event:

        token = os.environ['GITHUB_TOKEN']
        gh = login(token=token)

        # Check if request is from GitHub
        elif 'body' in event:
            body = event['body']
            if type(body) is str:
                body = json.loads(body)

            repo = body['pull_request']['base']['repo']['name']
            owner = body['pull_request']['base']['repo']['owner']['login']
            head_sha = body['pull_request']['head']['sha']

            if event['headers']['X-GitHub-Event'] == 'pull_request' and body['action'] in ['synchronize', 'opened', 'reopened']:
                build = codebuild.start_build(
                    projectName=repo,
                    sourceVersion=head_sha
                )
                build_id = build['build']['id']
                repository = gh.repository(owner, repo)
                status = repository.create_status(
                  sha=head_sha,
                  state="pending",
                  target_url="https://us-west-2.console.aws.amazon.com/codebuild/home?region=us-west-2#/builds/" + build_id + "/view/new",
                  description="Build is running...",
                  context="CodeBuild"
                )
                return {
                    'statusCode': 200,
                    'body': "Created Status - ID: " + str(status.id)
                }

        # Check if request is from CloudWatch Event
        if 'detail-type' in event:
            project = body['project']
            build_id = body['id'].split('/')[1]
            status = body['status']
            state = {
                "FAILED": 'failure',
                "STOPPED": 'error',
                "SUCCEEDED": 'success'
            }
            build = codebuild.batch_get_builds(
                ids=[Id]
            )
            sha = build['builds'][0]['sourceVersion']
            owner = build['builds'][0]['source']['location'].split('/')[3]
            repository = gh.repository(owner, project)
            status = repository.create_status(
              sha=sha,
              state=state[status],
              target_url="https://us-west-2.console.aws.amazon.com/codebuild/home?region=us-west-2#/builds/" + build_id + "/view/new",
              description="Build was a " + state[status] + ".",
              context="CodeBuild"
            )
            return {
                'statusCode': 200,
                'body': status
            }

        else:
            return {
                'statusCode': 400,
                'body': 'unknown command'
            }

    else:
        return {
            'statusCode': 400,
            'body': 'missing event data'
        }
