# Google Dialog Flow
This folder contains four projects that are used to make Pepper utilise Dialog Flow.

This project has been inspired and influenced by [this blog post](https://blogemtech.medium.com/pepper-integration-with-dialogflow-1d7f1582da1a).

## TODOs
- Maybe merge VoskClient and DialogFlowService into one bundle with a flag to enable vosk? That way they could also utilise stk and simplify their code? Not urgent however

## Projects
- DialogFlowService: This is a NAOqi service that runs on a laptop, it exposes some of the dialog flow API to Pepper. This is done because it is currently not possible to install the API on Pepper using pip.
- VoskClient: This is a socket client for a python 3 vosk server (see below).
- VoskServer: This is a Python 3 server hosting access to the Vosk Speech Recognition API. It was used during an experiment and can be optionally toggled in DialogFlowExample's demonstration listener service.
- DialogFlowExample: This Choregraphe project ties all of the above services together to create a basic dialog flow program. It contains the barebones and can be used as a template to create further applications.

## Setup/Configuration
You must install the NAOqi Python 2.7 SDK from [here](http://doc.aldebaran.com/2-5/dev/python/install_guide.html).
[Python 2.7](https://www.python.org/downloads/release/python-2718/) is required for the services however Python 3 is required for the Vosk Server.

`requirements.txt` files have been provided where necessary to pin dependencies to the correct versions. Entire pip dumps weren't provided as they may have been polluted however the important libraries are in these files.

Both services that can be run on the laptop (DialogFlowService and VoskClient) accept command line arguments to configure the target robot:
```
service.py --ip <ROBOT IP> --port <ROBOT PORT>
```

In addition, to authorise to Google Cloud for Dialog Flow, you must set GOOGLE_APPLICATION_CREDENTIALS in the environment variables to the correct path to your JSON token. I'd recommend reading the setup steps for Dialog Flow [here](https://cloud.google.com/dialogflow/es/docs/quick/setup).

## Customisation
You can customise the listener's respones to actions by editing `handle_actions` in `ListenerService.py`.
By default it can open urls, display local assets, clear the tablet and speak. It can also fire events to ALMemory if you haven't hard-coded a custom response for it. Hardcoding a response or custom action is only really necessary for when you need parameters to be returned via your action.