# IITBHackathon
A repository for version control of Team G3 for the IITBHackathon

Team SIP has created a modular smart water bottle system which can clip onto any water bottle to convert it into a smart water bottle.

The main function of SIP is to solve the pressing issue of dehydration without using expensive, complex technologies. By informing the user and alerting them when it has been too long since they have taken a sip, it ensures that they are hydrated in a simple, cost effective manner.

The main alert system is composed of 3 LEDs and a buzzer. The green LED shines when the user has just taken a sip, the yellow shines when the user _should_ take a sip, and finally the red LED shines when its been too long and the user must take a sip. Along with the red LED, the buzzer too beeps alternatively for a set duration to act as an alarm but not to be too obnoxious.

The way of detecting if the user has taken a sip consists of two sensors acting in unision - a hall effect or magnetic field sesnor, and a Gyro or a "tilt" sensor. By ensuring that both the cap is off with a magnet, and the user has tilted the bottle to drink it, only then does it count as a sip and the alarm system resets back to green.

Hence, SIP obsseses over the **problem**, and not the technology itself, by solving a prevalent issue with a simple solution.
