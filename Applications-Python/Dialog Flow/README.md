# Pepper Google Dialog Flow Integration
This folder contains four projects that are used to make Pepper utilise Dialog Flow. The dialog flow API has been optimised to ensure near-realtime responses.

This project has been inspired and influenced by [this blog post](https://blogemtech.medium.com/pepper-integration-with-dialogflow-1d7f1582da1a).

## Project Structure
- DialogFlowService: This is a NAOqi service that runs on a laptop, it exposes some of the dialog flow API to Pepper. This is done because it is currently not possible to install the API on Pepper using pip.
- DialogFlowExample: This Choregraphe project ties all of the above services together to create a basic dialog flow program. It contains the barebones and can be used as a template to create further applications.
- VoskClient: This is a socket client for a python 3 vosk server (see below). This has been kept in a separate project to DialogFlowService even though they have a lot of duplicated code as VoskClient isn't ready for primetime, it is still very much a prototype.
- VoskServer: This is a Python 3 server hosting access to the Vosk Speech Recognition API. It was used during an experiment and can be optionally toggled in DialogFlowExample's demonstration listener service. Remember that both this and the VoskClient must be running in addition to the DialogFlowService for this to be available.

## Setup/Configuration
You must install the NAOqi Python 2.7 SDK from [here](http://doc.aldebaran.com/2-5/dev/python/install_guide.html).
[Python 2.7](https://www.python.org/downloads/release/python-2718/) is required for the services however Python 3 is required for the Vosk Server.

`requirements.txt` files have been provided where necessary to pin dependencies to the correct versions. Entire pip dumps weren't provided as they may have been polluted however the important libraries are in these files.

Both services that can be run on the laptop (DialogFlowService and VoskClient) accept command line arguments to configure the target robot:
```shell
python service.py --ip <ROBOT IP> --port <ROBOT PORT>
```

In addition, to authorise to Google Cloud for Dialog Flow, you must set GOOGLE_APPLICATION_CREDENTIALS in the environment variables to the correct path to your JSON token. I'd recommend reading the setup steps for Dialog Flow [here](https://cloud.google.com/dialogflow/es/docs/quick/setup).

During testing if you would like to run the `ListenerService` on its own (for example the one included in the example project), you can simply run it with `python ListenerService.py` and it will prompt you for the connection details for the robot. Note that you'll need to make modifications to your initial python block (as discussed below) to support an already-running service.

To run the example, you must set up the dialog flow service correctly, configure an agent on Google Dialog Flow and setup its intents. Then you must change the Google project ID in the same place as disclosed below.

## Creating a new project
To create a new project with dialog flow, you'll want to follow the setup above, as well as create a new Dialog Flow Agent.
To create a new Choregraphe program, create it as you would normally, then copy and paste `DialogFlowExample/scripts` into your new project. Then add the following to your `manifest.xml`:
```xml
<services>
  <service execStart="/usr/bin/python2 scripts/ListenerService.py" name="ListenerService" autorun="false"/>
</services>
```
This tells NAOqi to install the ListenerService. Then you'll want to copy the "Start Listener" block from the graph into your own project. This just promps NAOqi to launch this service and starts it's listener. Remember to have the Dialog Flow server running on your PC before you do, otherwise the program will stop immediately.

Then add a new Python Box with the following code in it. You will also need to add a `"bang"` input named `listenerStarted` and a `"bang"` output named `onStarted`. Then add a memory event on the left of the graph attached to the event `ListenerServiceStarted`, you'll likely have to use the `Create new key` button. Plug this into `listenerStarted`. This lets the script know we're about ready to begin. We then wait a couple of seconds for the service manager to keep up then start our program.

```py
import time


class MyClass(GeneratedClass):
    def __init__(self):
        GeneratedClass.__init__(self)

    def onLoad(self):
        # Initialize our fields
        self.serviceMan = ALProxy('ALServiceManager')
        self.listener = None

        # Store the service name. We use the packageUid to make sure we don't collide.
        self.serviceName = self.packageUid() + ".ListenerService"
        pass

    def onUnload(self):
        # Stop our service from running in the background once the behaviour ends.
        if self.listener is not None:
            self.listener.cleanup()
        self.logger.info('Stopping listener service.')
        
        if self.serviceMan.isServiceRunning(self.serviceName):
            self.serviceMan.stopService(self.serviceName)
        pass

    def onInput_onStart(self):
        # Try to get Dialog Flow.
        try:
            ALProxy('DialogFlowAPI')
        except RuntimeError:
            # Server isn't loaded!
            self.logger.error('Dialog Flow Server must be started first!')
            self.onStopped()
            return
    
        # Start our listener service.
        self.logger.info('Starting listener service.')
        self.serviceMan.startService(self.serviceName)
        pass


    def onInput_listenerStarted(self, *_args):
        # Wait for the service manager to catch up.
        time.sleep(2)

        # Grab the listener and start our program.
        self.listener = ALProxy('ListenerService')
        self.logger.info('Starting listener.')
        self.listener.start_listening('<YOUR GOOGLE PROJECT ID HERE>', self.packageUid())  # TODO: Set your project ID here.
        self.onStarted()

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

## Future Steps
As part of further development of this system, the following could be investigated:
- Adapting the system that detects speech to be more sensitive and to account for background noise, allowing for single-word responses to be captured easier. Maybe integrating some kind of voice activity detection API.
- The Vosk API could be promising, however this same approach could be used to support virtually any speech recognition system.
- Look into using a higher sample rate from the microphones, that could lend itself to better clarity and therefore better recognition.
