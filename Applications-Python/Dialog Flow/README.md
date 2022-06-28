# Google Dialog Flow
This folder contains four projects that are used to make Pepper utilise Dialog Flow.

This project has been inspired and influenced by [this blog post](https://blogemtech.medium.com/pepper-integration-with-dialogflow-1d7f1582da1a).

## Projects
- DialogFlowService: This is a NAOqi service that runs on a laptop, it exposes some of the dialog flow API to Pepper. This is done because it is currently not possible to install the API on Pepper using pip.
- VoskClient: This is a socket client for a python 3 vosk server (see below). This has been kept in a separate project to DialogFlowService even though they have a lot of duplicated code as VoskClient isn't ready for prime use, it is still very much a prototype.
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

## Creating a new project
To create a new project with dialog flow, you'll want to follow the setup above, as well as create a new Dialog Flow Agent.
To create a new Choregraphe program, create it as you would normally, then copy and paste `DialogFlowExample/scripts` into your new project. Then add the following to your `manifest.xml`:
```xml
<services>
  <service execStart="/usr/bin/python2 scripts/ListenerService.py" name="ListenerService" autorun="false"/>
</services>
```
This tells NAOqi to install the ListenerService. Then you'll want to copy the "Start Listener" block from the graph into your own project. This just promps NAOqi to launch this service and starts it's listener. Remember to have the Dialog Flow server running on your PC before you do, otherwise it will not work.

Then add a new Python Box with the following code in it. You will also need to add an output named `onStarted`.
This is only example code and in this example it simply waits 3 seconds for the service to start and does not gracefully deal with problems such as the Dialog Flow server not being found. More robust solutions should be found. I'll do this if I have the time left.

```py
import time


class MyClass(GeneratedClass):
    def __init__(self):
        GeneratedClass.__init__(self)

    def onLoad(self):
        self.serviceMan = ALProxy('ALServiceManager')
        self.listener = None
        pass

    def onUnload(self):
        # Stop our service from running in the background once the behaviour ends.
        if self.listener is not None:
            self.listener.cleanup()
        self.serviceMan.stopService('ListenerService')
        pass

    def onInput_onStart(self):
        # Start our listener service.
        self.serviceMan.startService('ListenerService')
        time.sleep(3) # TODO: Proper way of waiting

        # TODO: Graceful error exits.

        # Get the listener service
        self.listener = ALProxy('ListenerService')

        # Start listening. Initialises dialogflow with a project id. Change this to your own.
        self.listener.start_listening('soc-pepper-summer', self.packageUid())

        # Fire any program init now.
        self.onStarted()

        pass

    def onInput_onStop(self):
        self.onUnload()
        self.onStopped()
```

## Dialog Flow Response Payloads
This implementation supports many pre-defined payloads and you can add your own too.

### Speech
Adding text responses adds to the pool of potential lines to say. One of these will be picked by dialogflow to be said.
You could add a payload to add more speech if you'd like, but that was out of scope for what this was designed for.
Multiple speech will cause large delay in execution and the custom payloads would execute before the speech.

### Show URL
```json
{
    "action": "show_url",
    "url": "<local or remote path>"
}
```

### Clear Tablet
```json
{
    "action": "clear_tablet"
}
```

### Run Behaviour
```json
{
    "action": "behavior",
    "behavior": "<behaviour id>"
}
```

### Custom Actions
Custom actions can either be implemented by adding them in the `ListenerService.py` `handle_actions` method, or they can be added in your Choregraphe (if they are "bang" type actions). This can be done by adding a switch onto the ALMemory event `DialogFlowAction` which will fire with the `action` component of the payload.