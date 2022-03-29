# SoC - Pepper

#### Getting Started
**DO NOT CONNECT PEPPER TO EDUROAM**

First you need to connect pepper to wifi to be able to send new programs. 
The best way to do this is to connect your Laptop/Desktop to the internet via Ethernet and then share this ethernet via wifi. 

[windows instructions](https://support.microsoft.com/en-us/windows/use-your-windows-pc-as-a-mobile-hotspot-c89b0fad-72d5-41e8-f7ea-406ad9036b85)
[mac instructions](https://support.apple.com/en-gb/guide/mac-help/mchlp1540/mac)

Once set up you need to connect pepper to the wifi network you have created.
1. To open peppers setting say "launch settings" while looking at pepper
2. The tablet screen will eventually display the info screen
3. Click on the world symbol to set the wifi settings
4. **DO NOT CONNECT PEPPER TO EDUROAM**

--
### Info
The version of NAOqi installed on pepper is 2.5.10, this is the latest version designed for research & development. It allows full, low-level access to all pepper's systems. 

Some documentation refers to NAQqi 2.9 and QiSDK, these are the newer, but highly restricted OS & SDK. They are designed for end-users. QiSDK And NAOqi are not installed on our pepper (and can't be)

### Resources to get started with Pepper:

[NAOqi Developer guide](http://doc.aldebaran.com/2-5/index_dev_guide.html)
[Working Store and manage for Nao -2.5](https://cloud.aldebaran-robotics.com/application/dialog_meta/)
[Latest Downloads](https://www.softbankrobotics.com/emea/en/support/pepper-naoqi-2-9/downloads-softwares)
[All Downloads](https://www.softbankrobotics.com/emea/en/support/pepper-naoqi-2-9/downloads-softwares/former-versions?os=47&category=108 )

 

 

 

How to fix the choreography lib not allowed sudo xattr -r -d com.apple.quarantine ./choregraphe-suite-2.5.10.7-mac64 

sudo xattr -r -d com.apple.quarantine ./choregraphe-suite-2.5.10.7-mac64 

 

 

Face detectiuon and recognition tut  

https://www.stsa.net.au/single-post/2017/05/05/pepper-tutorial-7-image-recognition 



#### How to use this repository

1. `git clone git@github.com:lillypiri/pepper.git`
2. Open Choregraphe
3. File --> Open Project --> RecognisingNAOMarks --> RecognisingNAOMarks.pml

(Select folder names and .pml according to the program you want to open.)

This will open the project in Choregraphe for you, and it should be ready to run on your Pepper.

Make sure you are connected to your Pepper, and run the program.

Note that for some exercises, it's best if Autonomous Life (the heart icon) is turned off.


#### Recognising NAOMarks

For this exercise you will need NAOMarks 64 & 68, downloadable from the Aldebaran Documentation [here](http://doc.aldebaran.com/2-1/_downloads/NAOmark.pdf).

After you run this program in Choregraphe, hold up NAOMark 64 or 68 in front of Pepper's camera. Pepper will perform the corresponding action.


#### Finite State Machine using Bumpers and LEDS 💡

This exercise uses Pepper's feet bumpers, eye LEDs and ear LEDs. There are four states stored.

When you run the program, press Pepper's left or right bumpers. The state will change. For example, if you press Pepper's left foot bumper once, the eye LEDs will change to Pink, and the ear LEDs will stay lit up. If you press the left foot bumper again, the eye LEDs will stay pink, but the ear LEDs will turn off.

To edit the colours or intensity of the LEDs or to program it so the colours only show in one eye, double click on, for example, Ears on & Eyes A box in root. In here, you can click on the Eye LEDs box's wrench and change Side to Both, Left or Right. On Ear LEDs box, click the wrench and adjust the intensity 0% is no light 100% is full light. On Eye LEDs, you can also double click, then click on the colour box to adjust the colour to your liking. Click OK and click back to root to test your code.


#### Rainbow Eyes 🌈👀

Simple program that makes the LEDs in Pepper's eyes display rainbow.


#### Engagement Zones

Uses Pepper's engagement zones to recognise a person entering and leaving zones 1 & 2, and trigger a response.
