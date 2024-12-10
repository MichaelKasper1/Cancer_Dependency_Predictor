# Django/Vue Web Application for Cancer Gene Dependency Prediction

### Introduction

This web application is open source. It is designed to predict, prioritize, analyze, and interpret cancer genetic dependencies through the two main tools:
- Cancer Gene Dependency Predictor which allows users to select from modern machine learning algorithms to predict and analyze predictions of cancer gene dependencies.
- TCGA Dependency Explorer which provides an exploration tool for identifying significantly intensified gene dependencies in tumors from The Cancer Genome Atlas dataset with specific alterations.

### Deploy

This app is containerized in a docker image. The easiest deploy the app, you will need to have docker installed within your environment. You can download docker [here](https://www.docker.com/products/docker-desktop). You can also easily deploy the app on the CRC. To build and run the docker image, you can use the following commands within a bash terminal:

```bash
docker build -t myapp .
docker run -p 8000:8000 myapp
```

This will start the app and make it accessible at http://localhost:8000.

### Develop

To set up your development environment,

Install make for command line automation:

    ```bash
    brew install make
    ```

Download and install all necessary dependencies for the app:

    ```bash
    make install
    ```

Run django and vue development servers concurrently:

    ```bash
    make start
    ```

Follow link http://localhost:5173/ to access web application. 
As you save changes to files, the app will reload automatically.

### Learn

This section is meant to help Chiu lab developers understand the languages/frameworks/tools used in the app.

I recommend using Visual Studio code as your IDE for development. You can download it [here](https://code.visualstudio.com/).

Below are links to useful tutorials:
- [Django Tutorial from VSCode Documentation](https://code.visualstudio.com/docs/python/tutorial-django) Django is the python framework for the backend of the application. It performs the data processing and interacts with the database. This tutorial gives you Django basics and you can learn about the directory structure and important files.
- [Typescript] (https://www.typescriptlang.org/docs/handbook/intro.html) Similar to javascript, but lets you manage data types and enables nice development features in your IDE.
- [Vue](https://vuejs.org/) Vue is the frontend framework for the web server. Vue files will be comprised of HTML, typescript, and css.
- [MongoDB] (https://www.mongodb.com/docs/manual/tutorial/getting-started/). The database for the application. Please see the readme in the database directory for more information.
- [Using Docker and Python in VScode](https://learn.microsoft.com/en-us/visualstudio/docker/tutorials/docker-tutorial) This tutorial helps you understand how and why to use Docker for containerization.
- [Make](https://makefiletutorial.com/) tutorial for understanding Make and how makefile helps to build app. There are also official tutorials on their website but I liked this one.

Below are some helpful VScode extensions I recommend installing for development:
- [Copilot](https://code.visualstudio.com/docs/copilot/overview) is an AI pair programmer that helps you write code faster and understand others code more easily. It's a LLM that watches you code and recommends code.
- [Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python) extension provides Python language support.
- [Django](https://marketplace.visualstudio.com/items?itemName=batisteo.vscode-django) extension provides rich language support for the Django framework.
- [Vue](https://marketplace.visualstudio.com/items?itemName=Vue.volar) extension provides support for view framework.
- [Docker](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-docker) extension makes it easy to build, manage, and deploy containerized applications from Visual Studio Code.
- [Remote Explorer](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.vscode-remote-extensionpack) extension let's you connect to Pitt CRC or other servers.

### License

This project is free to access. It is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.