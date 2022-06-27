# Google Dialog Flow
This folder contains four projects that are used to make Pepper utilise Dialog Flow.

This project has been inspired and influenced by [this blog post](https://blogemtech.medium.com/pepper-integration-with-dialogflow-1d7f1582da1a).

## Projects
- DialogFlowService: This is a NAOqi service that runs on a laptop, it exposes some of the dialog flow API to Pepper. This is done because it is currently not possible to install the API on Pepper using pip.
- VoskClient: This is a socket client for a python 3 vosk server (see below).
- VoskServer: This is a Python 3 server hosting access to the Vosk Speech Recognition API. It was used during an experiment and can be optionally toggled in DialogFlowExample's demonstration listener service.
- DialogFlowExample: This Choregraphe project ties all of the above services together to create a basic dialog flow program. It contains the barebones and can be used as a template to create further applications.

## Setup/Configuration
`requirements.txt` files have been provided where necessary to pin dependencies to the correct versions. Entire pip dumps weren't provided as they may have been polluted however the important libraries are in these files.

Both services that can be run on the laptop (DialogFlowService and VoskClient) accept command line arguments to configure the target robot:
```
service.py --ip <ROBOT IP> --port <ROBOT PORT>
```

In addition, to authorise to Google Cloud for Dialog Flow, you must set GOOGLE_APPLICATION_CREDENTIALS in the environment variables to the correct path to your JSON token. I'd recommend reading the setup steps for Dialog Flow [here](https://cloud.google.com/dialogflow/es/docs/quick/setup)

TODO:
- Configuring the behaviour

## Customisation
TODO: Customising the listener.