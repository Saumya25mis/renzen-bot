# Renzen

Renzen is a combination Chrome Extension and Discord Bot that allows you to save snippets from the internet and archive them in Discord.

The intended purpose for the BOT is for making it easier to find specific information when researching something and having 1000 tabs open at a time (for example when trying to fix a bug). The rationale is that when researching, you don't often need the whole webpage, but just the part you found that you need to reference without it getting lost in the other tabs (and also keeping that info when your browsers are closed). And that it's better to search for information through that text than entire webpages.

The intended purpose for the PROJECT as a whole is to create a continuously deployed codebase that can be contributed to by anyone who wants to join an Open Source Project that functions somewhat as a Product. This allows experience in seeing how everything works as a whole, for example at a company.

The project is a combination of a lot of different parts you'd see at many companies. Such as

- Production and staging CI/CD infrastructure on Amazon Web Services
- Use of Docker and Docker Compose for local development
- Linter and test checks to monitor the quality of submitted code (Pre-Commit, Pytest)
- Integration with a third party API (Discord)
- Handling web requests (aiohttp)
- Working with Database and Messages (Postgres, AWS SQS, RabbitMQ)

## Roadmap

The goal of the project is to expand into covering as many technologies you'd encounter at a start-up or major company. To give a well-rounded exposure, it sometimes makes sense to do portions of the project in different ways. For example, though right now all infrastructure is done in Cloudformation, new capabilities might be done in terraform. Some integrations that are being looked into being added are

- Datadog
- Sentry
- Kubernetes
- Terraform

A huge milestone for the project would be securing everything down into tightly controlled and limited roles so that local dev work could also be done on the cloud on dev branches and not just the Production or Staging branches.

Some features to be added are

- Running Batch jobs for ML model processing on data that users have opted-in to sharing. For purposes such as to see what type of information users are mostly to save or what websites etc. These could also lead in to a Recommendations engine that show up when users save specific data.

## Setup

The project was designed to take advantage of some of the features of VS code. One of the main featues are `dev containers` which spin up an environment in a Docker container. The advantage of this is that the container is pre-configured to work with the repository, and doesn't affect the environment of your computer. Hopefully this makes it simpler to contribute. There are other ways to run the project, but this is the recommended method.

- Download [VS code](https://code.visualstudio.com/)
- Download [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- Follow these instructions to create a bot Create bot [here](https://github.com/reactiflux/discord-irc/wiki/Creating-a-discord-bot-&-getting-a-token)
- Add your bot to the Renzen server
- Clone the [repository](https://github.com/renadvent/renzen-bot)
- Open the repository in VS code, and then re-open in a [dev container](https://code.visualstudio.com/docs/devcontainers/containers#_quick-start-open-an-existing-folder-in-a-container)
- Run `make create-env-template` and fill in your Bot token in the VS Code terminal
- NOTE to actually run the local environment, you need to open another terminal OUTSIDE of VS Code, navigate to the repository on your computer, and run `docker compose up --build`. (This is due to the VS Code terminal now being inside the Docker dev container, which may not have access to Docker itself)
- To use the chrome Extension, follow the instruction for Step 2 [here](https://support.google.com/chrome/a/answer/2714278?hl=en) and load the extension from the cloned repository

## Deploy Process

Upon a push to the Github repository onto a development branch, `pre-commit` tests are run that are defined in the `.github` folder. Upon merging the development branch to the `staging` branch, AWS receives notification of the merge and runs through the CodePipeline for that branch, builds all the necessary docker images, pushes them to ECR, and deploys them.

There are currently 3 docker images that are built and deployed: the [bot image](./renzen/src/bot/Dockerfile), the [backend image](./renzen/src/site/Dockerfile) and the [website image](./renzen-app/Dockerfile).

The build process is defined in in the [buildspec](./buildspecs/deploy_buildspec.yml), and the overall CI/CD process is defined in the CodePipeline portion of the [bot_stack.yml](./cloudformation/bot_stack.yml). Using `bot_stack.yml` allows us to create our staging and production branches using different resources and make them independent of each other. It also allows us to create an arbitrary amount of bots. Each bot deployed on AWS also receives a subdomain on `renzen.io` where requests can be sent. The valid subdomain requests are defined [here](./renzen/src/site/site.py). Valid discord bot commands are defined [here](./renzen/src/bot/bot.py).

![Deploy Process](./readme_images/Screenshot%202022-12-28%20105111.jpg)

## How To Use

![User Flow](./readme_images/Renzen%20Process.jpeg)

## bot_stack.yml Resources

Each bot_stack creates the following resources to set up a bot

![resources 1](./readme_images/Screenshot%202022-12-28%20110259.jpg)
![resources 2](./readme_images/Screenshot%202022-12-28%20110326.jpg)
![resources 3](./readme_images/Screenshot%202022-12-28%20110351.jpg)

# File Documentation

The purpose of this section is to give a brief overview of the files and in the project and their purpose. This can change as the project develops.

- .devcontainer
  - [**devcontainer.json**](.devcontainer/devcontainer.json)
    - configures the vs code environment with extensions, and specifies the Dockefile on in which to create the Dev Container we will be developing in
  - [**Dockerfile**](.devcontainer/Dockefile)
    - This is the Dockerfile that is run to create our Dev Environment
- .github
  - [**CODEOWNERS**](.github/CODEOWNERS)
    - Specifies files that need special approval from specific developers.
  - workflows
    - [**pre-commit.yml**](.github/workflows//pre-commit.yml)
      - This is a check that is run on all branches when pushed to github. Ths verifies that the code submitted meets certain standards. These standards are specified in `.pre-commit-config.yaml`
    - [**requirements.txt**](.github/workflows/requirements.txt)
      - These are python libraries that must be installed in the Github environment order for our pre-commit check to run correctly.
- buildspecs
  - [**deploy_builldspec.yml**](buildspecs/deploy_buildspec.yml)
    - This is the file that Amazon Web Services uses to actually build all of our code into something that is deployable on the cloud. This file is referenced in `bot_stack.yml` which tells AWS to use it as a part of our `CodePipelines` which manage our Continuous Deployment process.
- chrome_extension
  - [**background.js**](chrome_extension/background.js)
    - This is code that runs in the background when our extension is installed. It allows us to add the `send to discord` option on right-click, and to send the information to our backend.
  - [**index.html**](chrome_extension/index.html)
    - This file specifies how our pop-up will look when we click on our extension in the browser
  - [**index.js**](chrome_extension/index.js)
    - This is the javascript code that manages how to interact with our extension pop-up. For example, saving our login codes and the bot version we want to send our snippets to.
  - [**manifest.json**](chrome_extension/manifest.json)
    - This is a required file for Chrome Extensions that explain how the extension works and what it does.
- cloudformation
  - [**bot_stack.yml**](cloudformation/bot_stack.yml)
    - This is the file that defines the [Stack](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/stacks.html) that we use to run our Bot. The Production and Staging version of the Bot use this file to explain to AWS how to create it. For local Development, this information is contained in `docker-compose.yml`
  - [**export_parameters.py**](cloudformation/export_parameters.py)
    - This file is used to grab our original parameters for a Bot Stack when we are updating it. This file is used during our `build_spec.yml` and its output is used during another `CodePipeline` step to apply changes to Cloudformation.
  - [**github_connect.yml**](cloudformation/github_connect.yml)
    - This is used to create a connection to Github, so that when changes are merged into our `main` or `staging` branches, they are automatically deployed on the cloud.
  - [**service_roles.yml**](cloudformation/service_roles.yml)
    - This file is used to make sure that certain roles exist in the AWS account.
- renzen
  - src
    - bot
      - [**batch_update_cog.py**](renzen/src/bot/batch_update_cog.py)
        - This file is used by our Bot to catch the snippets forwarded from the Site, processes them, and forwards them in a Direct Message to the user
      - [**bot_health_check.py**](renzen/src/bot/bot_health_check.py)
        - Makes sure the bot is receiving messages (This health check is not actually currently verfied)
      - [**bot_utils.py**](renzen/src/bot/bot_utils.py)
        - This is code that the Bot uses to process messages before sending them to the user.
      - [**bot_wrapper_script.sh**](renzen/src/bot/bot_wrapper_script.sh)
        - Code to start bot the bot and the healtch check at the same time (This health check is not actually currently verfied)
      - [**bot.py**](renzen/src/bot/bot.py)
        - This file is what is used to actually interface with Discord. it creates the commands that Discord uses can use to interact with the Bot. It uses `discord.py`.
      - [**Dockerfile**](renzen/src/bot/Dockerfile)
        - This file is used to containerize our Bot and turn it into a deployable instance.
    - common
      - [**db_utils.py**](renzen/src/common/db_utils.py)
        - Functions in this file can be used by both the bot and the site to interface with our database which stores our snippets and other data. It also creates our dataclasses, and if the Database has not been set up yet, creates it.
      - [**queue_utils.py**](renzen/src/common/queue_utils.py)
        - Functions in this file can be used by both the bot and the site to interface with our queue. Which allows the passing of information from our Site API to our bot. (We use AWS SQS for Production and Staging, and we use RabbitMQ for local development)
      - [**secret_utils.py**](renzen/src/common/secret_utils.py)
        - This file is used to retrieve login information for our Database and Queue.
    - site
      - [**Dockerfile**](renzen/src/site/Dockerfile)
        - This file is used to containerize our Site and turn it into a deployable instance.
      - [**site.py**](renzen/src/site/site.py)
        - This file is our simple API that our Chrome Extension forwards snippet data to. This adds it to our Queue for our Bot to pick up later.
  - [**global-requirements.txt**](renzen/global-requirements.txt)
    - These are python libraries we install to be able to run our code
  - [**requirements-dev.txt**](renzen/requirements-dev.txt)
    - These are python libraries we need to be able to run our pre-commit checks.
  - [**setup.py**](renzen/setup.py)
    - This file allows us to install our code as a libary in our Docker Containers.
- renzen-app
  - TODO: Currently placeholder dummy app for blank website that is deployed at [renzen.io](renzen.io)
- scripts
  - [**create_env.template.py**](scripts/create_env_template.py)
    - Generates a template to input bot credentials. Do NOT commit this file to your branch.
  - [**deregister_tasks.py**](scripts/deregister_tasks.py)
    - Currently unused.
- tests
  - [**bot_test.py**](tests/bot_test.py)
    - The tests we run on our code to make sure certain functionality isn't broken when updating code.
- .gitattributes
- [**.gitignore**](.gitignore)
  - Files we explicitly tell git to ignore in version control.
- [**.pre-commit-config.yaml**](.pre-commit-config.yaml)
  - Configures the hooks we want to run when trying to commit and validate our code.
- [**.pylintrc**](.pylintrc)
  - Configures the checks we want to use for our `pylint` pre-commit.
- [**docker-compose.yml**](docker-compose.yml)
  - This file is used to run our bot locally, without any cloud resources.
- [**Makefile**](Makefile)
  - Shortcuts to some commands. Except for `create-env-template` and `run-local`, these can only be run by those with access to the Renzen AWS account
- [**mypy.ini**](mypy.ini)
  - Configures the checks we want to use for our `mypy` pre-commit.
