## Interview Transcript

### Context
- User mostly sticks to `SPEECH_Alltech_Walkthrough.md`, not the `mini_` ver
- The interview was on Google Meet, which doesn't allow transcript saving by attendee
- User has however turned on closed captions, which shows live subtitles (much lower accuracy than zoom though)
- User did a screen recording throughout; later found out Gemini limits video file upload to 5 min or 2GB (whichever reached first) and hence split the screen recording into 16 parts by `nscpt/trim_split_video_duration.sh` (parameter: START_TRIM_MIN=19 since Elena was late for 19min)
- Rear to that, user sends 1st part to Gemini with this prompt:
```
i have just had a second-round job interview (mainly about my trial task on reworking an intentionally ambitious onboarding plan based on my perception of reality) as an interviewee on Google Meet
i wasn't able to save the transcript but i turned on CC (subtitles show the speaker name above the dialogues; "You" = me; "Elena" = employer) so it was shown on screen where i did screen recording (no sound at all)
i want you to pull that into .md format and with timestamp (HHmmss) if possible (time is ticking per second on top right corner)
i also want you to remark nuanced emotions (if any) of both me (Culous Yu) and the interviewer (Elena Mel) in `{}` if possible
note: completely disregard the "TextEdit" window (the black text on white bg) and only look at the CC (white text on black bg) + the ticking timestamp (not the video timecode) as said
attached is part 1/16; when you're done with the first one, i'll pass the second one which i'll finally merge all 16 by myself
name me as "User" and the employer as "Elena"
format e.g.:
[134023] **Elena**: Hello {subtle smiling}
[134025] **User**: Hey how're you doing {seemingly surprised}
```
- User then sends 2nd part to Gemini with this prompt: `here's the next one; do it the same way but ensure you don't mixed up me vs Elena (the last one got half the transcript swapped roles); also please use british english only (convert if needed)`
- Finally user sends the remainder parts one by one, each with just this prompt: `continue to part [no.]`
- The "Parts" seem to have overlapping content due to the .sh splitting approach

### Part 1

[121915] **Elena**: Hello. I am so sorry. {apologetic tone implied, camera off}
[121920] **User**: No problem. {casual, forgiving}
[121930] **Elena**: It's my first day back to the office since we went for a holiday. So it's been a little chaotic. {camera off}
[121931] **User**: How's the holiday? {friendly, curious}
[121937] **Elena**: Much needed. It was our first holiday in like nine months. {turns on camera, smiling brightly, adjusting hair, relaxed}
[121940] **User**: Oh, really {surprised, engaged}
[121941] **Elena**: And three years for my partner. So yeah, that's very {laughing softly, happy}
[121946] **User**: Where did you go? {interested}
[121947] **Elena**: Bali Bali. {grinning, slightly bashful}
[121955] **User**: Really? Typical one. I still haven't been there yet, but I do wish I can go sometime. That makes gun there. {teasing, conversational}
[121956] **Elena**: Yes. It's it was great. It was much needed. {smiling warmly, nodding}
[122000] **User**: Yeah, but is it a summer or winter there? I'm not so sure. It's like the middle of you know, the hemisphere. {curious, gesturing slightly}
[122007] **Elena**: Ah, they don't have winter, they only have dry season and wet season and we went in the dry season. {informative, slightly amused}
[122015] **User**: Okay. {listening intently}
[122016] **Elena**: Wet season. I think is like November to February. {explaining, thoughtful}
[122019] **User**: Really? Is it currently the the most popular season to go to Bali {inquiring}
[122027] **Elena**: Right now? {nodding}
[122028] **User**: Yeah. {agreeing}
[122030] **Elena**: No, the most popular is end of July and August. {correcting gently, informative}
[122036] **User**: um, see about just in time? Cool. {impressed}
[122038] **Elena**: Yes. Okay, because we didn't want to sit there with that many people because he gets it was a little chaotic as it was, but I can imagine in July, it gets very hectic. {smiling, expressive, gesturing with hand}
[122055] **User**: That's cool. 
[122057] **Elena**: How are you? {friendly pivot to professional}
[122101] **User**: I'm good. Just busy as always. {professional, upbeat}
[122108] **Elena**: Of course. Alright, talk me through your plan. I am very keen to hear this. {encouraging, professional}
[122114] **User**: So, I'll start to share my screen. Right. Do you see it? {focused, adjusting setup}
[122128] **Elena**: Yep.
[122130] **User**: Okay. So thanks so much again for taking the time, you know, around your break. Not sure if you're read it yet but I'm more than happy to walk you through. So you can see my thinking not only the output I've got section by section, but please stop me anywhere you want to dig in. Okay, so the first thing I wanna be clear about ... {speaking confidently, presenting}
[122147] **Elena**: Yep. {attentive, nodding slightly}
[122148] **User**: ... is that the original plan was, you know, generally well written, as I implied in my email, the task design itself, requires a certain amount of skill and I did it before. So I understand it, and I do appreciate this. The 3-phase structure, the discipline of no live posts until October, the case study, the case-study-as-sales-asset logic, the EOS cadence, etc. All these are very much appreciated and I kept them. So I focused on keeping that ambition and adjusting the few things that could quite a break in a real first quarter at 24 hours a week. You see I've boiled down to five principles here as in, you know, the rationale behind the changes I've made. And the first one is the key one, sequencing around the peak season, not against it. So I guess that's, you know, pretty much "automatic" because the original one kind of back-loads the case studies into September to December, which is exactly when the technicians and PMs are flat out. Alright so I've front-loaded the case-study interviews in the quiet July, like right now, to August window, banked the materials whilst the mates are actually around, and left the writing to run steadily afterwards. So that single move managed a major risk in the plan. For the other four, I'll go through quickly. Phase the build rather than running all six pillars at once and make the hours kind of honest. So every month carries a real hour-budget. Respect the review gate on both sides, because you know front-loading my work also front-loads your reviewing, right? And calibrate to the market, which I'll come back to on the table ... {delivering a long, continuous explanation while referencing her shared document, steady professional demeanor, making hand gestures}

### Part 2

[122353] **User**: ...the table. The remainder of P.2 just lists out the constraints I deliberately built around. Like, you know, the peak season, the 24 hour week, the organic-only for the first year, your approval gate, and the fact that this is general one person plus AI, so not a team yet. So, from P.3 onwards is the plan itself where I kept the Immerse, Build, Execute structure, IBE. So, on P.3 here, month 1 is the immersion and the 3 audits, which I have spanned across the weeks rather than dumping all 3 at the end of week 2. {focused, explaining complex structure confidently with hand gestures}

[122421] **User**: Plus starting those case-study interviews early. On P.4, month 2 is where the systems get built: the content calendars, 5 case studies, hubspot essentials, and the website proposal. And I've been honest that August is actually the heaviest month as I planned, so I've flagged exactly how I protect it here. On P.5, there goes month 3, which is, you know, where the content goes live and I would expect to be running the core 3 pillars on my own, given your approval. {maintaining professional tone, referencing the shared document}

[122453] **User**: You might notice I'm rather prudent with the word independent: I separate owning a workstream from a deliverable being finished, because, you know, the website, for instance, runs to 2027 by design, so independence there means driving it, not completing it by Month 3. P.6 is the milestones table, the original draft target against my reworked one, with the reasoning in the last column. The focus is on the case studies as mentioned. It was, you know, kind of the priority, right? {confident, explaining rationale with expressive hands}

[122527] **User**: So the original draft aimed for 20 published by December, I've tuned it down to 10 to 12, and the reason is right there on the page: 20 would mean interviewing through the peak season when the team is least reachable, whereas 1 to 2 a month is the genuinely sustainable rate. It's the same logic as the front-loading, just carried through to the number. P.7 is kind of interesting. This is, you know, the part I am most keen to talk about, because it is what makes a 24-hour week credible in the first place. {passionate, leaning into the explanation}

[122600] **User**: In a nutshell, I build systems to do the heavy lifting and keep the judgement for myself. For case studies, I would manage the interviews and run an agentic system that turns a transcript into a first draft, then I edit for your review & approval. One event becomes a week of social content, so approximately 3–5 posts through a repurposing system. Like how we repurpose those kind of content into separate posts. For video, my AI systems handle B-rolls & graphics ... {thoughtful, illustrative hand movements}

[122631] **User**: ... but the real footage of the work on site remains real, because that is the actual selling asset and AI cannot fake it. And I am deliberate about what AI should not touch, the judgement, the brand fit, the factual accuracy, all of that stays with me and with your approval gate. So finally we've come to my questions. {making a strong point, transitioning to questions}

[122643] **Elena**: Mm-hmm. {listening attentively, maintaining eye contact}

[122647] **User**: I'll go through them fairly closely, because each one is genuinely something I truly wish to know about, and you know talk about with you. And a couple of them show you how I would think about the role. The first one being, how does the current data and the system actually look, that is the social analytics, the brand-asset state, you know, the website platform. I believe you told me before that was Wix. {engaged, outlining queries}

[122726] **User**: And the curated list of past projects. Like how are they currently being managed? You know, like is there a repository to keep the past projects? That determines how deep the Month 1 audits can really go. So that's my first question, and I'll just finish all first if you don't mind. And the second one being how quickly can approvals... {takes a sip from a blue water bottle, seamlessly continuing the thought}

[122752] **User**: ... actually turn around in practice, is it hours or days? And would you be open to a set of pre-approved templates or benchmarks, so the review gate protects quality without becoming a bottleneck? The third one is how is AI currently utilised across Alltech, and is there ... {inquiring, seeking collaboration}

[122802] **Elena**: Hmm. {thoughtful, considering the proposition}

[122807] **User**: ... appetite to move from chatbot-style exchange to bespoke & agentic workflows that can run non-stop for days? This is what I'm doing right now. So I'm very keen to bring that to Alltech. This one is my most important, honestly, because it tells me how far I can take the systems I just proposed up there. And which subscriptions are currently in place? For example, Claude Team or Enterprise or Max or whatever? And would this role have access, you know, how much can be used? And would you consider API ... {projecting enthusiasm, pressing forward with ideas}

### Part 3

[122849] **User**: ... access since a fixed plans? Like the Team or Enterprise or Max plans are fixed caps which limit the volume, so I'm just curious, you know, would you consider API. And is anything deliberately off-limits to AI, say maybe emails or contracts, you know, cannot be touched by AI or something like that? I draw that line carefully, and I would like ours aligned from day 1, so no surprises. And finally, if Alltech could be known for one thing and one thing only in 18 months, what would it be? Because you know the whole content engine should ladder up to that single position. So that's pretty much it. {gesturing with hands, seeking clarity to define the technical boundaries}

[INTERNAL: Below are low-confidence transcription content, possibly with errors.]

[122936] **Elena**: Cool. {nodding slightly}

[122940] **Elena**: Well maybe I'll start by answering your questions, and then I'll move into ... {adjusting hair, composed}

[122942] **User**: Yeah. {listening intently, taking a sip from his water bottle}

[122943] **Elena**: some high level updates for you in terms of the plan that you've mapped out {using hand gestures to frame the conversation}

[122947] **User**: Yeah. {attentive, nodding}

[122949] **Elena**: and probably some information that will be useful because that will shift that plan a little bit. So, your questions {smiling slightly, informative}

[122956] **User**: Yep. {hands clasped near face, focused}

[122958] **Elena**: The current data and systems look like ... Yes, the website is on Wix in terms of brand asset state at the moment, all of the images, sorry, half of the images are in Google Drive under the projects within each client. {explaining clearly}

[123018] **Elena**: The other half is currently being put in by our project manager catching up on that last busy season because we've restructured the Google Drive. So he's just wanted that final approval on the structure before he does it. But our plan is to move all the photos and videos from Google Drive to Google Photos. I mean, it's still in the same work suite, but in Google Photos, it'll be a lot easier visually to look through all photos. {gesturing with both hands to compare the platforms, clarifying the process}

[123050] **Elena**: So that's a deliberate move for both marketing purposes and for project purposes. We can actually create folders but it's visual folders rather than, you know, in Google Drive, you have to like specifically find each project going through like 10 layers of folders to get in there. Where's it? Don't see that? {animated, illustrating the frustration of the old file system}

[123115] **Elena**: That is very useful for marketing purposes, but that is something that the project managers are going to do, not the marketing person, that migration. If there is some support that's needed, maybe it'll fall under your remit, but I'm gonna make sure that the project managers are the ones that are doing that in terms of other brand assets. {firm but supportive, explicitly delineating responsibilities}

[123143] **Elena**: There is. The logos. Like both the iconography version of it and the actual logos. So the A is like icon, I guess there is at the moment only three brand colours which is the black, a specific grey, and the white. But I think we should expand that colour palette. We also have our own fonts that are like legally ours as well. And we have obviously the domains that are registered to us, patterns of things. {listing items, adopting British English spelling effortlessly}

[123214] **Elena**: But in terms of like, a brand guideline booklet. There's not a booklet that has everything in the one place and that is something that I don't think is a number one priority, but definitely something that we should consider creating just to make our lives easier. {thoughtful, realistic about upcoming priorities}

[123247] **Elena**: And also sharing, I guess with our clients for marketing purposes of how their content will be used. There's not specific templates of what the posts need to look like. But I think we have a pretty good idea. We also have a pretty good idea of what the brand voice should sound like, but it's not written down. {hand briefly touching head, reflective and candid}

[123309] **Elena**: There is a list of past projects. The ones on the websites take us up until a year ago and then the last year of projects is being finalised in Google Drive at the moment. We have like essentially for the five years before that, it's pretty much on the website and obviously, we have the backups of that in Google Drive, but for the last year... {informative, concluding the overview of assets}

### Part 4

[123341] **Elena**: past projects. The ones on the websites. Take us up until a year ago and then the last year of projects is being finalised in Google Drive at the moment. We have like essentially for the five years before that, it's pretty much on the website. And obviously, we have the backups of that in Google Drive, but for the last year, it's just been super chaotic. So the project managers haven't had time and there's not been the structure that we've now implemented to organise it as seamlessly as it should have been organised, so. Yeah. Does that answer your question number one? {speaking clearly, finishing her explanation of the file management}

[123401] **User**: I'm, you know, for the brand assets, are they currently in vector form like .ai or .eps or .svg those kind of things or just PDF? {asking for technical clarification, gesturing with hands}

[123413] **Elena**: Various formats. Yep. {nodding affirmatively}

[123416] **Elena**: Okay. And the month one audit should be very basic. I would say mainly because it is a tool for you or whoever lands in the role to understand the business and the baseline of things. It should really be just like a basic order of the socials. Like it shouldn't be a fully in depth one because over months, two and three, you'll build on that initial audit as you're starting to get ideas as you're noticing more things, as you like, you know, sponge more and more in the business you'll build on that audit. {leaning in slightly, explaining his rationale for a simplified first step}

[123501] **Elena**: So the purpose of the order being in month, one is so that you have a baseline to start from and build on for the next two months, as you settle more into the role as you learn more about the business. Any more details that you want to know, question one or shall I move on to question two? {summarising his point to confirm understanding, polite and collaborative}

[123522] **User**: Yes. Let's move on.{nodding, ready to proceed}

[123526] **Elena**: Okay, So um, the approval turnaround time. It would really depend. So for the first one especially it will definitely take days. And the way that I can picture us doing socials, is that we do. Like quarterly, we planned for the quarter of socials, so that's starting. Mark, may not be October in the end. Maybe it's November. That's fine. But we plan all of the socials like the copy. What the images look like the videos, whatever it is, we plan the three months and then I will do the first line of approval if there's any tweaks that need to be done, they'll be done. And then several do the final line of approval. {explaining workflow, using hand gestures to outline the timeline}

[123616] **Elena**: And I feel like that will take probably a week or two in terms of like my first round of approval and then Seb obviously as well and then probably with the next quarter it'll take less time and less time in terms of what the approval will look like. But I think it's smart to do a quarter at a time in terms of preparing the socials a it means that they're all queued up and like socials are happening in the background. Rather than like sitting around waiting around for approval for post by post like that sounds like it will I, mean, not sounds like I've had the experience and I know that. {continuing her detailed explanation, emphatic about bulk processing}

[123703] **Elena**: The lines of approval when you do one or a few at a time in the end, the opportunity cost. of doing it in bulk rather than one like One at a time is just not there, like, which is why the bulk ones first. First of all, it means that I can sit down in one chunk review it properly. I can point things out that you can learn from for the next quarter and then Seb can sit down and review and like you learn from both of us, different things that should and shouldn't be done. {using hands to structure her points, logical and communicative}

[123737] **Elena**: So for the next quarter, it'll be a lot easier for you to do them as well. Yes, so that is what I think how it should be essentially in terms of Pre-approved templates. I can't, I guess that's kind of where it sits from like US. That first quarter will allow you a sort of templates that you can work from in the next quarter. You can definitely start the first quarter working from how we've done post historically and check with myself and the director to see if we like the way that they're written. Now, what we would change, how much extra detail we would want Etc, and that will be the basis for the template, I guess. Yeah. Does that answer the question? {concluding the long response on approvals and templates, asking for confirmation}

[123833] **User**: How about how about benchmarks? Like, did you have some samples of {inquiring further, shifting topic slightly}

### Part 5

[123841] **Elena**: director to see if we like the way that they're written. Now, what we would change, how much extra detail we would want Etc, and that will be the basis for the template, I guess. Yeah. Does that answer the question? {concluding her thought, checking for understanding}

[123853] **User**: How about? How about benchmarks like did you have some samples of like what's good, what's you know, acceptable, what's bad? Those kind of things. {hands clasped, leaning in slightly}

[123908] **Elena**: No, not at the moment. I feel like it lives with us with in, in our heads, essentially. {laughing softly, acknowledging the lack of formal documentation}

[123918] **User**: Yeah. So, the next one, it's my AI. So how is it? Currents are being you? utilise across {smiling, transitioning to the next agenda item}

[123927] **Elena**: Yeah. So, we have Claude Team and everyone in the business has their own account. We've only moved to Claude quite recently. Probably about a month ago in terms of Claude Team. So I've set up the basic things in there and we are slowly starting like everyone's using it for their individual role needs at the moment and then some things were slowly starting to set up co-working projects, for example, for EOS and rocks and projects that we're working through with like specific people. We're slowly starting to set that up but it's not where I would like it just yet. Um, in terms of an appetite for chat bot style exchange to bespoke. We're open to it. I'm not 100% sure if you mean like on the website or what purposes, you mean that for? So maybe if you want to explain more, I can explain. I can answer you better. {gesturing with hands, explaining the current software stack and seeking clarification}

[124021] **User**: So, for example, I think I raise our earlier for So say, for example, for the case to the in the videos, after we shot the videos, and then the transcribe that of course, that's by AI Translator and they format, and then a whole ejected system, can transform that into a ready to edit a copy So, that would kind of scripture in line the whole thing and the whole thing can be full autonomous. so no in the verses need. I just received the actual draft and just added it {using hand gestures to illustrate an automated workflow pipeline}

[124056] **Elena**: Yeah. {nodding along}

[124057] **User**: and you'll find to increase doctor's class thing. So, {continuing thought}

[124059] **Elena**: Yeah, that would definitely be expected of this role using AI to increase productivity so that you can function without within those 24 hours. {nodding firmly, confirming the expectation of efficiency}

[124119] **User**: We'll subscriptions at the next one. is this? Well subscription so you'd already have me. It's called team. So, this role we have access to that, right? I presume {scratching head briefly, relaxed, moving down his list}

[124133] **Elena**: Yeah. {confirming}

[124134] **User**: And how about API would that be possible? {direct and inquisitive}

[124138] **Elena**: Um, it will be something that we definitely look into as we go. Probably not for the first three months but if you have, like, recommendations to bring in and you're like, I want to do XYZ. This is what it needs to be, this is how much it's going to cost. I'm obviously here to listen to you and see what the opportunity cost of using it versus not using. It is {hands clasped, setting realistic expectations regarding budget and timelines}

[124206] **User**: Yeah, exactly. That's that's basically why. Because I I tend to scale the product of AI like, with, with the limited plans, like the standard plans. {gesturing to emphasize scale}

[124216] **Elena**: Yep. {listening attentively}

[124216] **User**: Of how much is it? Like 200 Bucks. I Love Dancing. How much that can do. And if we push it to API, how much further to go, how much volume can it, you know, can it provide? How many percentage those kind of? That's why there's a dog. So. moving on. How far anything? Yeah, is everything delivered to open it. Say, the policy wise {speaking passionately, using hands to weigh options}

[124243] **Elena**: Um no, I with ChatGPT there was because of their ethics and use of the information but Claude has a lot stricter, ethical codes. So no, we found that since switching there, hasn't been anything that we've made off limits. But if you know Claude better than I and you make recommendations for certain things to be off limits, like I will obviously take that into consideration. {explaining their data privacy stance with slight hand gestures, maintaining a collaborative tone}

[124316] **User**: Okay, I, I just, you know, side note, I've been using Claude for like two years now, so, {smiling, sharing personal experience}

[124323] **Elena**: Yeah. I can teach me, something's {laughing warmly}

[124325] **User**: And kills Nana, I just always like to know Share with people. how how {laughing, adjusting glasses}

### Part 6

[124330] **Elena**: can be used, How we control harness the power that so you know, As I said not just Q&A chat poster. So actually get it to work {nodding, adjusting glasses, smiling slightly}

[124407] **User**: Yeah. {listening, nodding}

[124408] **Elena**: independently autonomously for hours or days to something. That's what I enjoyed it. But Yeah. Anyway, that the final question is, You know, it's gonna say so if all that could be known for one thing in 18 months, older B. {gesturing with hands, smiling, looking down briefly}

[124424] **Elena**: um, I don't really know how to answer that to be honest. Because we're already known for the things that we want to be known for. I feel like you'll just be enhancing that, which is providing like the highest quality {touching face, thinking, looking upwards, then back at camera}

[124439] **User**: Yeah. {listening, nodding}

[124440] **Elena**: projects that a lot of other AV companies say are too hard. So that is already what we're known for. So it would just be amplifying that I feel like if I can change your question and answer that, I would change your question to like what is the highest? Value asset that the person in the role could bring in that would probably be the better question to answer and that is making sure that Hubspot is probably set up and live in the PMS are using it by the beginning of September. Now, we are actually going to use an agency to do that side of things. But the person who comes into the role, will assist the agency with eight hours a week out of their 24-hour roll. So, one of the three days that they're working, they'll assist the Hubspot onboarding and set up and that is mainly for the purposes. Because for that, that person actually owning that Hubspot function in the business and And being able to use it. And troubleshoot as we go. So I feel like it's important that we don't just pay an agency to implement all of it. Even though they'll do the bulk of it, that person, the agency will give tasks to that person and to myself as well that we will implement so that I'm actually a Hubspot certified coach and expert with over 50, certificates in what {gesturing with hands, explaining in detail, confident}

[124618] **User**: I don't, yeah. {smiling, listening}

[124623] **Elena**: there is things that I can help with, I will try my best to assist But the opportunity cost for me to actually take on the project and fall is just not there. Like I already have enough things to feel my buckets and time with but the person coming in no matter that helps what their help spot skills that will be really beneficial for their growth and their skills as well. And then, so that hubspot section being set up, that will alter your plan a bit {gesturing, explaining workload constraints}

[124653] **User**: Thank you. {nodding, hand on chin}

[124654] **Elena**: because By. The first week of September, they will fully onboard us onto Hubspot. We will have everything set up for the sales side and the sales function of the business. And they'll also do the rent man integration for us with the custom coding. And the first week of September will be used for them to train the whole team to use hubspot. so that as we go into peak season, they know exactly what to do and the rent man integration and then that is the thing that will bring probably the biggest value to the marketing side and give us the most ROI. Just for context, if Hubspot was set up a year ago. We could have not passed over or slash lost about 1 million, One million. Yeah one million dollars in revenue so that is the biggest profit margin for us, if that is set up properly and it's being used properly that will bring the most return on investment. And then the second thing is definitely the case studies. Now so you know, the case studies, all our customers, I think I said to you last time All the customers that we have currently are through word of mouth. At the moment we actually have more a surplus of enquiries coming through word of mouth, that we actually don't have capacity to handle, more than that hubspot fixes Part of the issue for that, I'm hiring a senior project manager to fix the other half of the issues of that, but the case studies are a tool to use Our existing client and customer basis so that they get inspired and know the capabilities that we have internally. So those case studies are a way of keeping {speaking earnestly, hands moving to emphasise scale of lost revenue and future potential}

### Part 7

[124741] **Elena**: them interested, and inspiring them for future projects. So that is a second highest ROI and then the third one is the website. So the website, I think we should do the website property and from the get-go and do it, right? Because before I came on board, they redid the website. So that's the redone better version of it, if you can believe it. Um, but a It's on Wix B. It's not like where it needs to be for us to start slowly scaling from an online perspective. So I would think that a 12 months face plan for the website is probably where we're at the core phase of like, the core pages that need to be changed and updated and the new pages that need to be added and live by the New Year. And then, another phase will be the additional pages sub pages that will come from that as well. And the way that I would like to do the website is through the story. Brand framework. If you don't know the framework, I would suggest looking it up. But yes, that is the way that those three Things. The biggest things that will mean success for the role. {using fingers to count off points, speaking clearly about long-term goals}

[124844] **User**: Yeah. for the story brand framework. I'm not 100% sure but in my knowledge it seems more common for you know like Consumer brands, like because all tag is like a beta bay. So, it's less common. I'm quite curious. How you see that being implemented? as for, you know, pretty Story. The whole point of story brand, is that? {asking a probing question, taking a drink of water, listening closely}

[124921] **Elena**: Yeah. {listening, preparing to answer}

[124922] **User**: You capture the clients essentially to Address their biggest pain points and how you solve them. It doesn't have to be a B2C thing. It actually the best use cases for it are in the B2B a lot more B2C user than B2B. But the whole point especially on the On the home page is that once you click the home page you know exactly. What problem that company solves from just reading the title and the subtitle on the page? so that before you even read the details of how and what you know, exactly if this is the thing for you, And yes, I guess that is the shortest way I can explain it. I can definitely go into more detail, but I think in the spirit saving. {elaborating on his understanding of the framework, speaking quickly and enthusiastically}

[124953] **Elena**: No, I guess I guess I'm very interested in that because I did do something like that before, but not in this website format like videos and like brand story video, those things. I'm very interested, but you know, I'm just curious because I and those, I did for before, we're all beat to see. So I, I not exactly how it would be done. But no, how it would come out, how it looked like when done, as a B2B brand doing like rent, story, brand, friendly, those kind of thing because I have a city before. So because you might know it's like being to be brands usually tend to be more we'll call it industrial. So let's {nodding, clarifying her past experience and expressing interest in how it applies to B2B}

[125036] **User**: Yeah. story and that's you know, client or customers scented those kind of things. I mean, if you think about the way that we work and even if you can see our case studies, the whole point is that we tell a story. So the story framework actually perfectly fits with that and it's a tools. It's a the framework is really a tool that {gesturing to emphasise the narrative aspect of their work}

[125055] **Elena**: Mm-hmm. {listening, agreeing}

[125057] **User**: Simplifies a business's message and it's a simple rule. The customer is the hero which in Whether we're because we work with obviously B2B to C or B2C, So the customer regardless of, if they're an agency, or if they're the incline, they're the hero and our business is the guide to that. And that's the point of store using story brand to do a website rebrand because it actually guides them on a story of how we elevate them to be the hero and guide them through that process. But not only just guide them. We actually support them through providing, not just like consulting services, I guess, but the actual physical deliverable as well. {explaining the core concept of the StoryBrand framework clearly, using hands to structure the explanation}

[125145] **Elena**: Another thing I was kind of, if you don't mind me asking that I noticed and most rather cures before. I'm not sure if {leaning in, asking a polite but direct question}

### Part 8

[125150] **Elena**: most rather cures before. I'm not sure if I saw that in one of the Attachment sent by your or open website, but I saw that the logistics like because all text is a nationwide company and suppose all you know, right, Australia. So, how is the logistics actually run? Is it a department or is it full-time staff or something? {asking a logistical question, gesturing slightly, adopting British English spelling}

[125221] **Elena**: Um, there is I mean product, the AV in production industries, a bit different to other industries. So the quality team is always slimmer and then there's always a lot of freelancers in the inner circle and then even more in the outer circles. So the way we function, we have a course, six of five with the new With the new sorry Five Six. Yeah, a core team of five with the new marketing person, It will be six and then the new senior project manager, it will be seven. So that is the core team And then the inner circle is for 10 to 15 like freelancers and contractors that are like operators for projects and they're hired on a project basis. And then that's the ones we go to first. And then there's the outer circle of probably like a To 150 freelancers and contractors that are the wider circle. If our inner circle is not available that we go to and offer the ability to come into projects. {explaining the company structure clearly, using hands to delineate the different 'circles' of staff}

[125330] **User**: I, I can recall those like I'm just curious. So for example you got a job from you know, let's say Perth. What would it be like a huge task? Because, you know, for the distance it are {curious, leaning in, framing the hypothetical scenario}

[125345] **Elena**: Yeah. We gonna fly there or drive there, whatever like I, the point is that I'm trying to find out if distance or like interstate jobs will be kind of a challenge. or that all {nodding, understanding the question and completing the thought}

[125357] **Elena**: um, kind of, I guess like this more planning and logistics involved. so we charge a higher fee but to say that it's challenging not really. I guess I'll like most of our jobs are within. I have a New South Wales or Lower Queensland or Upper Victoria. So that's the chunk of our work. So if we have to send out product will either do a truck that will drive there or? Yes, fly. And then the people who are relevant from Sydney to fly out or fly out but that's accounted for in the quoting phase. {explaining logistical realities calmly, gesturing to indicate locations}

[125446] **User**: Yeah. Right. That's pretty much all for me. Like I said, the questions. {nodding, satisfied with the answer}

[125451] **Elena**: Cool. All right. I guess some background for you as well. {smiling, preparing to move to the next point}

[125456] **User**: Yeah. The socials, your rework targets. three to four posts a week is not something that the director nor myself would want to go with. why is because of the B2B and B2C market that we're in. Maybe. With in a year, we could wrap up to that. But first, we'll starting with such a high volume Just does not make sense for us. It's not like we're trying to get leads through socials. This is purely to highlight brand presence and just remind people that we're on the map. {interrupting politely to explain the strategy shift regarding social media frequency, hands clasped}

[125555] **Elena**: Just trying to explain those three to five social posts that I propose were the maximum as in the capacity, the maximum capacity. It can be expanded so, to so it could be zero, it could be one, it could be less. So I'm just say it is very Yes. It will be dependent like three to four, maybe if it's split across all the platforms in total. {clarifying her previous proposal, using hands to emphasize 'maximum capacity'}

[125611] **User**: Yeah. But two to three is probably like a good starting point. Maybe look at three to five if it includes all the subplatforms. So if there's like one full LinkedIn one for Facebook, one for Instagram, or two, for Instagram. like if it's split between all and each one count, yes it can go up to that number but one two, sorry, two to three posts. Week is more like on one platform, that's the maximum. We'd want to start with two posts a week on a platform and then scale higher. um, {nodding, agreeing and refining the target numbers with hand gestures}

### Part 9

[125633] **Elena**: Yeah. {listening, acknowledging the suggested target}

[125633] **User**: platforms in total. {concluding his thought on the numbers}

[125637] **Elena**: Yeah. But two to three is probably like a good starting point. Maybe look at three to five if it includes all the subplatforms. So if there's like one full LinkedIn one for Facebook, one for Instagram, or two, for Instagram. like if it's split between all and each one count, yes it can go up to that number but one two, sorry, two to three posts. Week is more like on one platform, that's the maximum. We'd want to start with two posts a week on a platform and then scale higher. um, I was just trying to provide. {nodding, clarifying her expectation and finding common ground}

[125712] **User**: I was just trying to provide some, you know, the headroom no words about that. {smiling, taking a sip from a white mug}

[125719] **Elena**: The case studies. Yeah, I probably agree with you. It'll really depend on teams capacity. Approvals bottlenecks that will be good. Hubspot I'm giving you the background for um, Website, we've spoken about. Videos and podcasts, that will probably Be if not. Like podcasts is definitely a next year. Thing as much hours I would love to do it is definitely a next year thing In terms of videos, I think the only ones would be the case studies, if that's what we go with. But it will really depend on people's availabilities. But yes, we will need to plan that out as we're doing that first month in terms of like planning seeing people's capacities, etc. Um, and yeah partnerships is something that will probably mostly be with me. And something that I will lean on the marketing person to assist me with sometimes, it will really be a case-by-case scenario. I wanted to eventually pass over to the person who's doing the marketing but not like at the start. So probably like it'll be only bits of pieces. I mainly put it into the scope of work because I want that person to eventually scale into taking over that mark partnership. Not take over, but do more and more slowly in terms of supporting me with partnerships, but because it's kind of partnerships kind of sits in This gray area of sales versus of sales and marketing. So that will stay with myself in the director for a chunk of time until we can figure out like a good flow for it, that we can pass it over to someone else. And I feel like the rest of it is pretty spot on, I guess. The biggest change is really the hubspot in terms of like how that will progress and the website. Yeah. And the only other thing I want to do with you is go through. Just a few questions on I guess, value alignment. So looking back at the last three months, Do you feel like you've dedicated enough time to your education and development based on your own? I guess, criteria for yourself. This is a very I guess self-reflective question. It's not whether other people think so, it's whether you you are, I guess. Satisfied with yourself, in terms of the amount of learning and education and self development, that you've been doing over the last three months. {speaking extensively, detailing expectations across different channels, then smoothly transitioning into a values-based interview question}

[125923] **User**: May I expand that to six months, if that's possible. Would you mind? {asking permission to broaden the timeframe}

[125926] **Elena**: Sure. {smiling, receptive}

[125927] **User**: Okay, I have finished two master degrees in the past. Six months. In the same time. Yeah, first one is in Sydney. The University of technology under the IT faculty, it is called Master of human computer interactions. Like Something between engineering, IT, project management, psychology, and design. And the second one is my MBA. So I literally just finished. I graduated from Uts and last the samba and then I immediate a dive back in to my and be able to just in the UK. It was. All right. So I could, you know, pause every singles how things that's why it could. That's why if you look at my resume expands model, we quite a long time. I started out in like 2003 and I just finished up because of the Uts thing and I did not have did not explain why, why I have to do here, too, you guessing is obviously the visa thing. So. Yeah I've so as a result I did, Finish two master degrees in the past six months and I you know, was that aside? I also the some certificates, one of them is the McKinsey Forward program, which I earned the certificate. I'm happy to show you if you're interested. {speaking rapidly, proudly detailing his recent intensive academic achievements and explaining a gap in his resume, gesturing with hands}

### Part 10

[130006] **User**: Yeah. Basically that is not about consulting at all. It's really about professional competency. Those kind of things. So it's like how I think and and do problem solving how I managed stakeholder relationship, those kind of things that like the general soft skills, So I do find that very useful and very much transferrable to all kinds of jobs. You know, unless I become a tradie, you know. {laughters} So yeah, I, I would say I was pretty active in the past. six months, in terms of education and self improvement, and self-initiated learning those type of things, and I do a little program. And you know, I learned as I as I do say, yeah, I enjoy learning and working in the same time things. So, that was my answer to your question. {gesturing to emphasise transferable skills, expressing confidence in his self-directed learning}

[130058] **Elena**: Okay, he's really done a lot. A lot of the last six months, haven't you? {smiling, impressed and slightly amused}

[130103] **User**: Yeah. {smiling modestly}

[130105] **Elena**: Yeah, oh, and FYI that was my fault fourth degree, I did psychology and pharmacy. 10 years ago. {laughing, sharing a personal detail}

[130113] **User**: Look yeah. A lifelong learner. I love it. {smiling broadly, enthusiastic}

[130116] **Elena**: Exactly. But, you know, that's not exactly something, I'm very proud of, you know, because I The reason why I did so many degrees is not, I want to but I have to {smiling but turning slightly serious, clarifying her motivation}

[130129] **User**: Yeah. {listening, understanding}

[130131] **Elena**: Industry, the economy, the world is you know, driving me to do that because I'm my first degree was psychology. I love psychology but I could not make a living with it. I guess you couldn't understand. {shrugging slightly, explaining pragmatic career choices}

[130145] **User**: Yeah. {nodding sympathetically}

[130147] **Elena**: like, Long story song. So you kind of have to have a PhD to be like an actual psychologist and not alone could take a decade. so that's why kind of pivots to Pharmacy. I, you know, because my, my whole family is in the science. Medical does tell the industry. So they cut out expectations of me then that was like, yeah, 11 years ago and I did anyway but I didn't like it and I, I get placement in multiple hospitals drug factory, And pharmacy, that was That was in the UK called Boots. So it's like Commerce Warehouse, those kind of things. And yeah, I did all three kind of Disciplines of operation and I really hate it. So I just quit it and you know, join the market force {gesturing, recounting a lengthy career journey with a hint of resignation and humour}

[130245] **User**: Yeah, Amazing. Look at you guys. um, how have you had time to work? {smiling, genuinely impressed by the breadth of experience}

[130252] **Elena**: I love working because I I Enjoy learning, but I don't enjoy the university style learning like talk learning. I don't like, you know, {smiling, adjusting hair, distinguishing between academic and practical learning}

[130303] **User**: Yeah, another guy. {chuckling, relating to the sentiment}

[130306] **Elena**: Trial and error self initiated those kind of learning So that's why I enjoy working. Listen, the more you work, the more, you know what, you don't know. And the more you learn, those kind of things. {passionate about practical experience, using hands to emphasise points}

[130318] **User**: 100%, I very much agree with you. {nodding vigorously, strongly agreeing}

[130321] **Elena**: Yeah so, I think it's safe to say what amazed me is not the known knowns but that I know announce and I know I know you {smiling, making a philosophical point about knowledge}

[130331] **User**: Yes, I do actually. {smiling, following the thought}

[130335] **Elena**: Yes, I do. actually tell me what lessons. Have you learned in the last six months? Sorry. three months that you've been able to put in to practice since learning them. {pausing to collect thoughts, asking a targeted follow-up question}

[130352] **User**: In the past frame. um, I in the past three months, not the six months in the past few months, I have been working with my Hong Kong firm, The consultant firm about AI Implementation. So it's really mostly very technical. Very much and commentation and planning and system, wise coordination, communication, those kind of things. So, I regret to tell that there's a much like practical livelorn, lessons that I've learned, that could be practically transferable to another job because those are highly technical. And You know, not something I could directly transfer. That's my responsive. {touching head thoughtfully, explaining the highly specific nature of his recent work}

[130444] **Elena**: Fair enough. {nodding, accepting the answer}

[130446] **User**: Yeah. {smiling faintly}

[130447] **Elena**: Um, have you held back from? I guess in the last six months, have you held? {leaning in, asking a probing question}

### Part 11

[130758] **Elena**: Have you held back from? I guess in the last six months, have you held back from making someone or something better? When you look at that time? Like, whether that was something that was in sitting, well with you or sitting something was feeling off. Did you have a direct or open communication about it, Or did you bottle it up and let things slide {asking a behavioural question, serious and attentive}

[130821] **User**: It depends on how it defines holding it back. I always manage. The breath and death as in how I put it through. But I always, you know, ensure that my voice is out for whenever there is something that could be improved or rectified or optimised, those kind of things, you know, but do I have to consider the situation, not just a, the one that we're looking at, not just microscopic, but microscopic situation as in the economy is it, it's what I'm proposing feasible and Bible and is it like was I off myself, Why? And why now? So it's quite easy to answer the why like Why do it? But it's more difficult to answer Why now? So I always, you know, hold myself accountable announce myself, this question before I deliver my full message. Of course, I go into that way, but Before I actually proposed the whole implementation on change management. I do assess the feasibility and viability before that but in terms of yes, and no, yes I always do voice all Whenever anything is wrong or some you know can be better. I always do that, but I would manage how much and in what I support. {speaking thoughtfully, explaining his communication and decision-making process with hand gestures}

[130953] **User**: Yep. Yeah, that's my response. {nodding, concluding the answer}

[130955] **Elena**: Um, I have a very direct and blunt question for you. We have a very I guess casual culture here and something that is like, very banter heavy. In our company and you you seem very I guess, professional. How do you think? That that would align with you. {smiling slightly, asking a direct culture-fit question}

[131024] **User**: I lost my pharmacist. License 11 so many years ago. So legally and socially, I am not a professional. I'm professional in my work upon the social status standpoint. I am far from professional. I'm a very easy contest out. I would trust don't put it that way. And just in case you're wondering, I am a have a shift thing and btr and between INTJ and ENTJ. So my ine can shift depending on the situation. That's why I told you that I am fully confident. I am Fully comfortable to work Independence Day individually. And I can also work as a team member because of my personality of between antichromian. {laughing, using humour to defuse the "professional" label, gesturing with hands}

[131124] **Elena**: Your responses, though. I'm very professional. I guess. So, I think I'm not saying that the teams unprofessional but they're very Aussie. Like they I don't can't say they they have the same. Level of professional communication that you do. So how do you think you would go meshing with them? Like we don't wear button up shirts. It's very red. {laughing, elaborating on the Aussie culture vs his communication style}

[131152] **User**: I don't use an important enough, I just do that on but you because of the respect, you know, I don't I don't wear this one. Not the colour guy but you know, I wear the same everyday, just not today. I'm a very castle person and follow that. That's why I can. Oh, I admit, I, I took what you said earlier but was a, you know, kind of a compliment. I I can be fully presented with professional like business corporate, those kind of situations but in the everyday mana I'm a very easy going person. So I would not concern of all that. {smiling, touching his black shirt to explain he dressed up out of respect, clarifying he's easygoing}

[131226] **Elena**: Okay. {nodding}

[131227] **Elena**: Okay, how are you with banter? Because some people are not very good at making. And taking better or giving it back. {smiling broadly, testing his reaction to banter}

[131240] **User**: This is what I lack I I You know one of the reasons I moved Australia is because of the bandit. So, because of the culture that I will not immerse and learn about but I haven't had the chance yet and this is what I value almost, the most, you know, I mean. {laughing, enthusiastically agreeing that he moved to Australia specifically for the banter and culture}

### Part 12

[131252] **User**: Yeah. {smiling, agreeing enthusiastically}

[131253] **Elena**: I like it. I like it because this is And taking better or giving it back. {nodding, explaining the culture}

[131257] **User**: This is what I lack I I You know one of the reasons I moved Australia is because of the bandit. So, because of the culture that I will not immerse and learn about but I haven't had the chance yet and this is what I value almost, the most, you know, I mean. {smiling, emphasizing his desire to learn the banter culture}

[131317] **Elena**: I think empirically speaking. None of them was my weakness, but logically speaking partnership would currently be the top weakness of my because you know, I'm in Australia. I don't know what. It's a logical speaking that one but like kind of automatically become my weakness but I do intend to do everything I can to learn and you know, overcome that witness whenever any opportunity to concerns I would take that and overcome such bigness. Yeah. So do you know how to code websites then? {shifting gears, asking about technical skills after sharing a personal insight}

[131405] **User**: I know but I, I also know how to more. I can't I can even show you at but basically if you go to Colorlessview.com, you'll see the website is not a bit which were all over 90% a great. But but those are, you know, academic works. I because I don't actually Because my name plus You.com. You'll see under, I believe it's tactical and you'll see the websites that I built during my time in Uts But I have to be frank I and not like Web designer is not my social status. I can decide what but it's not a key. Selling product. You know, I mean, so I have the capability to do that, and But I don't know other I'm not exactly proud because that's not something I am. You know, that's why I didn't turn to like, what design the world and their marketing business us. That's what I do. So yeah, I fully capable of doing that. I can count in the old fashioned way and I can do it also in the so called new fashioned, why? So is guys wax or or whatever, or AI, whatever I can can do it in. And the efficient way or very detecting way. I didn't handle both. The Yep. and the last question I have is actually around salary. Now, when I looked at your application you submitted 60 K salary as your expectation. That was a typo but I know I can't put it back But anyway, I am fully open to your offer just because of how much I value this opportunity, right? So I am Okay, I was like that the salary range that I put was between 75 and 85K, open to the open. Yeah. I know. Is was like Why are you low falling yourself so much? It was like a title you know know on sick I didn't Because I prefilled that before maybe somehow but the second way and then and then it just popping. I didn't say and just that for, but yeah, but anyway, as I said I I just I'm just open to the offline. I don't know if you would brought me the opportunity to the stage free, but I do think that will be something to worry about beyond stage 3, if I have the chance. So I don't want that. so, when I had the salary range, I just want to Set clear expectations before I push you through into stage 3 is the salary range 75 to 85k That's a per annum. Salary, that would be then. At the part-time rate. So, 80 For example, if we take 85 it would be half of that or the 24-hour equivalent of 85. That you would still be. Happy with as a starting salary. As I said, I don't mind. I don't mind in a nice trust if we have the chance to work together, you will say my value quite soon. based on my exper Fyi. um, at least free of my previous employers, Rehire me as an external consultant after I left, So that's how much people what value, you know, my service. So I wouldn't I'm not right now, you know, It's hard to be humbling the whole time but I am put a confidence. My body will be seen and the whole time, but I sure I will transit to a full-time world pretty soon if everything goes {speaking at length, explaining technical skills, clearing up a typo on his application regarding salary expectations, and expressing confidence in his value with hand gestures}

### Part 13

[131700] **User**: Yeah. {listening intently}

[131700] **Elena**: media engine website, and digital presence sales, and a moment and marketing assets, and partnerships research and growth initiatives. What do you think? First, your weakest areas and what other areas that you'd want to either get assistance or outsource? {reading from a document or screen, asking about weaknesses and outsourcing needs}

[131720] **User**: I think. Empirically speaking. None of them was my weakness, but logically speaking partnership would currently be the top weakness of mine because you know, I'm in Australia. I don't know what. It's a logical speaking that one but like kind of automatically become my weakness but I do intend to do everything I can to learn and you know, overcome that weakness whenever any opportunity presents I would take that and overcome such weakness. {taking a drink from his glass, pausing to consider, then explaining that his location makes partnerships the logical weakness, gesturing to emphasise his point}

[131758] **Elena**: Yeah. {nodding along}

[131759] **User**: Yeah. So do you know how to code websites then? {leaning back, asking a direct question to the interviewer}

[131804] **Elena**: I know but I, I also know how to more. I can't I can even show you at basically if you go to Colorlessview.com, you'll see the website is not a bit which were all over 90% a great. But but those are, you know, academic works. I because I don't actually Dallas To what? What am I typing in? {laughing softly, starting to explain her skills, then getting confused by the URL he mentioned}

[131825] **User**: Because my name plus You.com. You'll see under, I believe it's tactical and you'll see the websites that I built during my time in Uts But I have to be frank I and not like Web designer is not my social status. I can decide what but it's not a key. Selling product. You know, I mean, so I have the capability to do that, and But I don't know other I'm not exactly proud because that's not something I am. You know, that's why I didn't turn to like, what design the world and their marketing business us. That's what I do. So yeah, I fully capable of doing that. I can count in the old fashioned way and I can do it also in the so called new fashioned, why? So is guys wax or or whatever, or AI, whatever I can can do it in. And the efficient way or very detecting way. I didn't handle both. {explaining the URL, clarifying that while he has web design skills (referencing Wix and AI), it's not his core professional identity or 'selling product'}

[131929] **Elena**: The Yep. and the last question I have is actually around salary. Now, when I looked at your application, you submitted 60 K salary as your expectation. That was a typo but I know I can't put it back But anyway, I am fully open to your offer just because of how much I value this opportunity, right? So I am Okay, I was like that the salary range that I put was between 75 and 85K, {referencing notes, bringing up the salary discrepancy on his application}

[131952] **User**: open to the open. Yeah. I know. Is was like Why are you low falling yourself so much? It was like a title you know know on sick I didn't Because I prefilled that before maybe somehow but the second way and then and then it just popping. I didn't say and just that for, but yeah, but anyway, as I said I I just I'm just open to the offline. I don't know if you would brought me the opportunity to the stage free, but I do think that will be something to worry about beyond stage 3, if I have the chance. So I don't want that. {laughing, explaining the 60k was an auto-fill typo and that his actual range is 75-85k, expressing flexibility and a desire to focus on the next stage}

[132036] **Elena**: so, when I had the salary range, I just want to Set clear expectations before I push you through into stage 3 is the salary range 75 to 85k That's a per annum. Salary, that would be then. At the part-time rate. So, 80 For example, if we take 85 it would be half of that or the 24-hour equivalent of 85. That you would still be. Happy with as a starting salary. {using a calculator on her screen, clarifying that the 75-85k range is pro-rated for the part-time hours, ensuring they are on the same page}

[132120] **User**: As I said, I don't mind. I don't mind in a nice trust if we have the chance to work together, you will say my value quite soon. based on my exper Fyi. um, at least free of my previous employers, Rehire me as an external consultant after I left, So that's how much people what value, you know, my service. So I wouldn't I'm not right now, you know, It's hard to be humbling the whole time but I am put a confidence. My body will be seen and the whole time, but I sure I will transit to a full-time world pretty soon if everything goes {smiling, expressing confidence that his value will be recognised quickly, sharing that previous employers rehired him as a consultant}

### Part 14

[132213] **User**: Fyi. um, at least 3 of my previous employers, Rehire me as an external consultant after I left, So that's how much people value, you know, my service. So I wouldn't I'm not right now, you know, It's hard to be humble the whole time, but I am put a confidence. My body will be seen and the whole time, but I sure I will transit to a full-time world pretty soon if everything goes smoothly there, It does. That's why I asked in our last meeting like with my performance as a limitation aside how long it will take because that's what {speaking with conviction, explaining his career trajectory and ambition to transition to full-time, leaning forward slightly}

[132306] **Elena**: Yeah. Yeah. {nodding in understanding}

[132307] **User**: answers my questions. Not not the current offering. I don't actually mind about that and, and I might have how you, you know, last time my, my wife is a chef and so we are pretty comfortable. {laughing, explaining his financial stability and lack of concern over the initial part-time offering}

[132322] **Elena**: Okay. All right. Well, some people get to Through job interviews. I know that they get through to the end and then they get a job offer and they're like actually it's too low for me. With other roles I've hired for as well. So I like to make sure before I progress people to stage three that they're absolutely radically honest with what their salary expectations are so that there's no confusion and disappointment and like silent resentments later down the track because, you know, everyone has different expectations Everyone has different. I guess. Requirements to have, I guess maintain their lifestyle as well. So I'd rather get be on the same page with people before they progress further because yes, some people do need a hundred and twenty case salary to sustain themselves. Other people don't Which to each their own right? Everyone has their own journeys. So I'd rather be on the same page, so if you're holding back anything, speak now, I'm not I'm not holding back anything and yeah, I'm fully comfortable with that thought range. {explaining her rationale for asking about salary directly, gesturing to emphasize transparency and avoiding future issues}

[132441] **Elena**: Yeah. {acknowledging his confirmation}

[132442] **User**: thought range. Yeah. {confirming his comfort with the range}

[132443] **Elena**: Yeah, okay, fantastic. All right. Well, I think you'll be good to set an in-person interview. Let me come back to you probably by end of day tomorrow for something for next week What does your schedule look like so that I can hear have it in mind as I arrange something with our director? {smiling, moving to schedule the final interview stage}

[132506] **User**: um, it's always Saturday for, you know, the physical meeting. I'm just curious is anything I had to prepare. For, for this upcoming meeting like a castle. And okay. Right. because I'm fully packed over the weekend, and That's all right. No, no, there's nothing. {rubbing his head, explaining his schedule constraints and asking about preparation}

[132525] **Elena**: Yeah. Yeah. Okay. Meet and greet with the sea, with the directory myself and just probably some follow-up questions just to make sure that everyone's on the same page. {outlining the agenda for the next interview stage}

[132537] **User**: Yeah. {nodding}

[132538] **Elena**: Yeah. I got it. I can say that I have choose them once afternoon pretty much bacon. Okay, after what time? I think after the 1pm. You know, that the lunch hour after your lunch hour, I'll be, you know, make a conven convenient for you. Yep. You're in Sydney, right? You can do in person. I yeah I mean power model so so it's pretty close. Okay. Okay, cool. All right. Well, I'll come back to you before end of day on Friday and let you know and otherwise yeah we'll keep in touch if you have any questions in the meantime feel free to reach out to me. Otherwise You have some, you have some comments for me as of this time. Mmm, I think you did a great job on your assignment. I think my biggest concern at the moment with you is literally the culture fit because you do seem very highly professional, which is great for me, because I am highly professional but the culture for the rest of the team is Not that. Like, with me, I am I can very much balance between like, switching to highly professional and like Very, very battery but the team has a huge banter culture like and the way that they speak is very Slang, casual Aussie. So that is probably where my biggest concern sits at the moment. {arranging the meeting time, confirming location, and then delivering direct feedback regarding her primary concern: culture fit, gesturing to differentiate her style from the team's style}

[132717] **User**: Let me give. {trying to interject}

[132720] **User**: Let me give you a little bit of background. I used to work in Crew house. For video production, I think that was Ah, 2017. And then I worked in multiple production house. All these guys are without a degree and my wife, of course doesn't have the grain.

### Part 15

[132738] **User**: Let me give you a little bit of background. I used to work in Crew house for video production, I think that was ah, 2017. And then I worked in multiple production house. All these guys are without a degree and my wife of course, doesn't have the grain. So I am fully comfortable with whatever people. I am very I will say bound to us. So that's not a problem. {sharing personal background, relaxed and open}

[132752] **Elena**: Let me just put it in a way that I think it will be so blunt and direct, like a lot of the guys that are on crew, like, do accents and some people will take that as an offense. But most Aussie's don't, um, we've had a lot of people of every ethnicity and culture work with us and they usually Due to the hiring process, they usually don't get offended. But all of the guys here, do accents in one shape or form. And that is one of like the banters that they do. I guess there's a lot of different banters that they do, but I want to be very, very clear and direct about it. {direct and candid, using hands to express the casual but potentially offensive office dynamic}

[132836] **User**: Yeah, if you mean the letter action I wear an awesome everyone there's an upson right? Like we're not okay. Like I'll say that. Yeah this Right now. I mean like they they will joke by putting on other accents from different cultures. I don't mind. I don't mind at all. I kind of enjoy. {laughing, receptive, showing he is unbothered by jokes}

[132853] **Elena**: Okay, I do too. But I also need to be careful as well because I'm like, you guys are literally a walking HR disaster for me. {laughing and holding her hands up, joking about HR}

[132904] **User**: Yeah, I wouldn't worry about that. I'm being honest, I wouldn't worry about that. {reassuring her, smiling}

[132912] **Elena**: Okay, okay. Well look, it's always better to take some people. Some people are very like Sensitive. There's the whole like, I mean, I feel like cancel cultures moving on finally, but there are some people That still can't take a joke, so Especially with how much they talk s*** here in English. Yeah. Like a stable. I get Yeah, the cons, they're talking s*** The you know, {explaining the practical reason she's bringing it up, gesturing}

[132943] **User**: Yeah, Norris. {nodding along}

[132946] **Elena**: Funny accents, whatever. I just need to be sure that {smiling}

[132949] **User**: Yeah. No one's going to offend anyone. {confirming confidently}

[132953] **Elena**: Yeah. {nodding}

[132958] **User**: I think over my years of working, if there's one thing that has come to my attention that's particular valuable is adaptability. I am very adaptable and that's why I guess so, yeah, I could follow that. In one of the Roman, the mother is like, super high state like those high society. Oh yeah. I used to work for luxury magazines. I, I and I am comfortable in those tenant situation. And, as I said, I worked in a cruel house. Those kind of things, and event production, video production, all those help people. So. I am fully at adaptable and, as I said, my wife, is a chef. So I have with chefs and kitchen crew, so that's how things and. {speaking confidently, citing extensive and diverse work experience, including his wife's career}

[133049] **Elena**: Yeah. It is, it is just one night. Come dressed casually for to do and say {smiling, giving practical advice for the next interview stage}

[133054] **User**: Yeah, oh, really enjoy Yes. right, I'll try that. Yeah. I think I just know that the director is one thing that he'll definitely. Take notice of. {taking mental note, pointing out a potential pitfall}

[133107] **Elena**: Oh, really. So like he particularly doesn't like people like shoot up. I've He's vetoed a lot of candidates for various roles because they were too overdressed for the interview. {sharing insider information about the director's preferences}

[133125] **User**: Oh, really, oh, that's you. Okay, right. I just were my, you know, casual outfit. {relieved, confirming his casual attire plan}

[133132] **Elena**: Absolutely. Right, basically, all black You can even if yeah, if you want to put on a funny T-shirt, even bonus points. {encouraging, nodding}

[133142] **User**: Mike. Jesus. The funny this. I just shut all my T-shirt society about some and I never wear a brand season. Oh, I love that. I love that. I feel like You got my? I can. Show you. So like this is my design, like maybe five five years ago, you see them. You see that? {excited, leaning forward to show a t-shirt design on his end}

[133206] **Elena**: Yes. Yeah, so like I love that. Actually the director, with one of the guys that works here. He they have their own like production. Company. their own like, T-shirt and Hoodies company for specifically for the production industry. So he would appreciate {impressed, confirming that his design background will be a hit with the director}

[133226] **User**: Good. Great. {smiling, satisfied}

### Part 16

[133238] **Elena**: All right, I will let you go. I have to run to meeting and I will be in touch before end of day. Tomorrow, {smiling, adjusting hair, preparing to wrap up the interview}

[133242] **User**: Yep. Okay. Yeah. {nodding respectfully, acknowledging the timeline}

[133247] **User**: Thank you, thank you so much for the time and all the fun. Thank you so much. {smiling warmly, expressing genuine appreciation for the conversation}

[133249] **Elena**: Great White Palace speak later. Okay. {smiling and waving goodbye; *note: CC likely misinterpreted a phrase like "Great, bye guys, speak later"*}

[133250] **User**: Bye. {smiling, waving goodbye as the call concludes}