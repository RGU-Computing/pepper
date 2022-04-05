# SoC - Pepper

## RULES
1. Pepper is a sophisticated piece of hardware but does have security vulnerabilities. While it may be fun to demonstrate these, bricking pepper will be an expensive excercise, please don't. There are much less sophistacated (re expensive) hardware examples we can use to demonstrate these. 

2. Same goes for inappropriate actions etc. If you are wondering if something is inappropriate, it probably is. (Basically variations of don't tiktoc pepper swearing)

3. If you do break something while running your code, make a note of what you were doing. If you can't fix it by turing pepper on and off again let Colin/John/Kyle know asap (this list may grow). 

4. Use descriptive names for your applications & behaviours. Don't install anything called untitled, test or similar. Check the installed applications list in Choreography and make sure you use a unique name for your new behaviour. 

5. Check your trigger words and environmental triggers, multiple behaviousl acting on the smae trigger word is a bad idea. 

6. You have chosen wisely. But pepper cannot pass beyond the great seal. That is the boundary, and the price of development. (Really bad things will happen if Pepper leaves the office without letting someone know)

7. If you do anything cool or find out some new info, add it to the wiki.

---

### The Wiki
Please build up the wiki as you go. Add a link to any programs you make and describe what they do. 
Add info about anything that you have found that isn't already there. 
#### [wiki](https://github.com/wildfireone/pepper/wiki)

---

### Getting Started
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

---
### Info
The version of NAOqi installed on pepper is 2.5.10, this is the latest version designed for research & development. It allows full, low-level access to all pepper's systems. 
Some documentation refers to NAQqi 2.9 and QiSDK, these are the newer, but highly restricted OS & SDK. They are designed for end-users. QiSDK And NAOqi 2.9 are not installed on our pepper (and can't be at the minute)

---
### Resources to get started with Pepper:

[NAOqi Developer guide](http://doc.aldebaran.com/2-5/index_dev_guide.html)

[Working Store and manage for Nao -2.5](https://cloud.aldebaran-robotics.com/application/dialog_meta/)

[Latest Downloads](https://www.softbankrobotics.com/emea/en/support/pepper-naoqi-2-9/downloads-softwares)

[All Downloads](https://www.softbankrobotics.com/emea/en/support/pepper-naoqi-2-9/downloads-softwares/former-versions?os=47&category=108 )

[Soft Robotics Training Github](https://github.com/SoftBankRoboticsTraining)

Choregraphe - licence Key - 654e-4564-153c-6518-2f44-7562-206e-4c60-5f47-5f45

#### Security Fix for Mac OS Monteray

How to fix the choreography lib not allowed

''sudo xattr -r -d com.apple.quarantine ./choregraphe-suite-2.5.10.7-mac64''

---
### Where to start

Read the [User Guide](https://github.com/wildfireone/pepper/blob/master/PEPPER_UserGuide_EN_2019%2007%2005_1.pdf)
Download [Choregraphe](https://www.softbankrobotics.com/emea/en/support/pepper-naoqi-2-9/downloads-softwares) and follow the guide [here](https://developer.softbankrobotics.com/pepper-naoqi-25/naoqi-developer-guide/choregraphe-suite)
 
