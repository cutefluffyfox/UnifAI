![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![ChatGPT](https://img.shields.io/badge/chatGPT-74aa9c?style=for-the-badge&logo=openai&logoColor=white)


# Links
* [About us](#about-us)
* [Team members](#team-members)
* [Value proposition](#value-proposition)
  * Problem statement
  * Solution description
  * User benefits
  * Differentiation from other solutions
  * User Impact
  * Use cases
* [Project vision](#vision-of-our-project)
  * Overview
  * Schematic drawings
  * Future problems
  * Knowledge gaps


# About us

**UnifAI** is a platform that cracks language barrier with Artificial Intelligence. 
We aim to create perfect speech-to-speech pipeline to recognize, translate and simulate 
speaker's voice in real-time. 

<p align="center">
    <img src="https://svgshare.com/i/uHd.svg"  width="50%">
</p>

We provide [application](TODO_INSERT_LINK_WHEN_DONE) that could recognize users 
speech (voice-to-text), transmit it to server that translates it (text-to-text), and 
parse messages from other people and generating their voices in your own language 
(text-to-speech). If you want to know more about program workflow, you can check 
_Schematic Drawings_ in [Vision for our project](UnifAI#defining-the-vision-for-your-project).

If you want to collaborate with us, or just interested in project, message 
Polina Zelenskaya at [Telegram](t.me/cutefluffyfox) or 
[Email](mailto:p.zelenskaya@innopolis.university)!


# Team Members


| Team Member              | Telegram ID                          | Email Address                       |
|--------------------------|--------------------------------------|-------------------------------------|
| Polina Zelenskaya (Lead) | [@cutefluffyfox](t.me/cutefluffyfox) | p.zelenskaya@innopolis.university   |
| Ekaterina Maksimova      | [@n0m1nd](t.me/n0m1nd)               | e.maximova@innopolis.university     |
| Ekaterina Urmanova       | [@aleremus](t.me/aleremus)           | e.urmanova@innopolis.university     |
| Evsey Antonovich         | [@aiden1983](t.me/aiden1983)         | e.antonovich@innopolis.university   |
| Daniyar Cherekbashev     | [@wrekin](t.me/wrekin)               | d.cherekbashev@innopolis.university |


# Value Proposition

**Problem statement**: 
The language barrier is becoming more and more noticeable. 
Digitization of the world brings people from different cultures and countries closer together. 
Because of all this, knowledge of foreign languages has become a necessary skill for modern 
society. Unfortunately, not all people have the resources to learn a new languages, 
adapt to unique accents and be able to understand language specific grammar.

**Solution description**:
We aim to utilize a combination of several Machine Learning tools to recognize and 
translate speech in (near) real time. Those tools may include: a voice recognition 
model (i.e Whisper), a translation model (i.e Opus) and a TTS model (to be determined). 
Ideally, voice processing would be done client-side, providing independence and privacy to our users. 

**Benefits to Users**:
Our project offers an array of benefits to users looking to utilize it. By using our 
software, users will not have to worry about any language barriers, as the app will 
seamlessly translate anything they speak in real-time and let others hear it in their 
language of choosing. Less time will have to be spent on choosing what language to speak to 
accommodate everyone, and fewer problems will arise from the no longer existing problem of 
not understanding someone’s accent. Additionally, no money will need to be spent on hiring 
professional translators to translate speeches during public events - saving money for 
everyone. Lastly, hearing everything in one’s native language will greatly increase 
productivity, as people generally comprehend speech faster in the language they are the 
most proficient at.

**Differentiation from existing solutions**:
There exists several solutions to this problem.
Google-based speech-to-speech models. Their downfall is use-case. 
They aimed to be used in offline dialogues as a more convenient way to interact with your interlocutor. 
We want to make translation as parallel as possible, and not require any 
additional action from the user. We aim to make this app integrable into other apps 
such as online games and video streaming services.

**User Impact**:
With our app, users can engage in conversations and use apps that were previously 
inaccessible due to language limitations. They can communicate without having to worry 
about manually translating each sentence. Additionally, the scope of use of this project 
is incredibly large: people will find this solution useful for gaming, for regular 
conversations, and maybe even for industries by allowing businesses to expand their 
worldwide reach and client base.

**User Testimonials / Use Cases**:
We imagine many possible use cases for our product, for example:
* Improving meetings in nationally diverse workplaces, especially those where many people work remote. Frequently, language barrier is one of the biggest challenges in workplaces that employ workers of different nationalities, and we feel as if our project could eliminate that issue completely, letting people communicate easier than ever in such scenarios.
* Allowing gamers of different nationalities to communicate in games easier. Very frequently people that speak different languages may get matched up in games where teamwork is important, and in such cases it may be quite frustrating to play! Our software would solve this issue, and allow gamers from all over the world to enjoy playing together and forming great teams.

# Vision of our Project

**Overview**: 
Our project utilizes a combination of several Machine Learning tools 
to recognize and translate speech in (near) real time. Those tools may include: 
a voice recognition model (i.e Whisper), a translation model (i.e Opus) and a TTS model 
(to be determined). Ideally, voice processing would be done client-side, providing independence 
and privacy to our users. 

**Schematic Drawings**:

![Workflow design](https://i.imgur.com/o3tiph5.png)

One user(Hans) speaks his native language. UnifAI Captures his voice and turns it into text.
Text is sent to Server that translates the text into requested languages, 
for example, user Alsu has set the language that she wants to receive to tatar, and server 
generates tatar text. When text is delivered to another user, let’s consider Alsu again, 
UnifAI synthesizes voice from text.


**Anticipating Future Problems**: 
Resources required to maintain 3 ML models might not be enough for an average user 
(a decent GPU is needed to smoothly run the app). Also, STT model has delay (depending on 
a scale of chosen model of whisper AI), and if model with the lower size is chosen then 
accuracy will be also lower on average.

**Identifying Knowledge Gaps**:
Right now we are developing product that is not implemented by anyone yet. 
This field of speech-to-speech translation requires research that could dramatically 
improve performance of models, resulting in a various of questions that we should 
investigate:
* How TTS models perform when 'clone' and 'output' audio languages differs?
* Are there any 'perfect sentences' that would simulate majority of sounds that humans use for communication?
* Is there any 'paths' to increase quality of translation, or directly translating from input language, to target one, performs the best?
* Will idea of separating all parts (speech recondition, translation, and voice cloning) create a bottleneck situation?
* Is real-time translations much more valuable, than delayed with better performance? 
* Due to different language structures it may be impossible not to delay tts output, what could be done about it?
* And many more! Q~Q

We are not yet sure about the exact knowledge gaps that will appear in the 
process of the application (backend) development of our application, but if we do 
find out that we have some, we will have no trouble in dealing with them through 
the use of brainstorming solutions as a team and effective information searching online.
