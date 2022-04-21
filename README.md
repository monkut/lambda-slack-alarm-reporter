# marvin README

Process Lambda Alarms incoming via SNS, retrieve related logs defined for settings.FUNCTION_NAMES (may be separated by commas) 


Required Policies (sam):
```yaml
      Policies:

        - SNSCrudPolicy:
            TopicName:
              Fn::ImportValue: !Sub 'artsub-alarms-${StageName}-ErrorNotificationSNSTopicName'

        - Statement:
            Sid: "AllowArtSubBackendGetLogEvents"
            Effect: "Allow"
            Action:
              - "logs:GetLogEvents"
            Resource:
              - !Sub "arn:aws:logs:${AWS::Region}:${AWS::AccountId}:log-group:/aws/lambda/functionname-${StageName}:log-stream:*"

        - Statement:
            Sid: "AllowArtSubBackendDescribeLogStreams"
            Effect: "Allow"
            Action:
              - "logs:DescribeLogGroups"
              - "logs:DescribeLogStreams"
            Resource:
              - !Sub "arn:aws:logs:${AWS::Region}:${AWS::AccountId}:log-group:/aws/lambda/functionname-${StageName}:*"
```


## Local Development

Python: 3.8

> Requires [pipenv](https://pipenv.readthedocs.io/en/latest/) for dependency management
> Install with `pip install pipenv --user`

### Create `.env` for development

```bash
SNS_SERVICE_ENDPOINT=http://127.0.0.1:4566
LOGS_SERVICE_ENDPOINT=http://127.0.0.1:4566
```


### Install the local development environment

1. Setup `pre-commit` hooks (_black_, _isort_):

    ```bash
    # assumes pre-commit is installed on system via: `pip install pre-commit`
    pre-commit install
    ```

2. The following command installs project and development dependencies:

    ```bash
    pipenv sync --dev
    ```

### Add new packages

From the project root directory run the following:
```
pipenv install {PACKAGE TO INSTALL}
```

 ## Run code checks

 To run linters:
 ```
 # runs flake8, pydocstyle
 make check
 ```

To run type checker:
```
make mypy
```

## Running tests

This project uses [pytest](https://docs.pytest.org/en/latest/contents.html) for running testcases.

Tests cases are written and placed in the `tests` directory.

To run the tests use the following command:
```
pytest -v
```

> In addition the following `make` command is available:

```
make test
```

