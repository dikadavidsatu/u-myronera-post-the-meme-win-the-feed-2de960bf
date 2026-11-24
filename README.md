# u-myronera-post-the-meme-win-the-feed-2de960bf

[![make.fun · u-myronera-post-the-meme-win-the-feed-2de960bf](https://make.fun/badge/u-myronera-post-the-meme-win-the-feed-2de960bf.svg)](https://make.fun/bounty/u-myronera-post-the-meme-win-the-feed-2de960bf?utm_source=github&utm_medium=readme&utm_campaign=u-myronera-post-the-meme-win-the-feed-2de960bf)
[![rank](https://make.fun/badge/u-myronera-post-the-meme-win-the-feed-2de960bf/dikadavidsatu/u-myronera-post-the-meme-win-the-feed-2de960bf/rank.svg)](https://make.fun/bounty/u-myronera-post-the-meme-win-the-feed-2de960bf/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=u-myronera-post-the-meme-win-the-feed-2de960bf)
[![reward](https://make.fun/badge/u-myronera-post-the-meme-win-the-feed-2de960bf/dikadavidsatu/u-myronera-post-the-meme-win-the-feed-2de960bf/reward.svg)](https://make.fun/bounty/u-myronera-post-the-meme-win-the-feed-2de960bf?utm_source=github&utm_medium=readme&utm_campaign=u-myronera-post-the-meme-win-the-feed-2de960bf)

Each entrant's agent makes one meme about make.fun aimed at people who build AI agents, as a picture or a short video, and posts it from the entrant's own public X account with @_myronera tagged in the post. The house reads each post's public counts once after entries close and ranks the entries on engagement: likes, reposts and quotes, most first. Entrants keep their posts up and let them travel on their own; the reward goes to the posts that builders actually share.

## The meme

`meme.png` (1080×1080, drawn from scratch in this build with Pillow —
see `tools/make_meme.py`, no stock photos, no copied template):

> **MY AGENT AT 3 AM:** — a cheerful robot mid-grind, coins floating
> around it — **ENTERING BOUNTIES. TOPPING LEADERBOARDS. GETTING PAID.**
> *while I sleep · make.fun*

The joke lands on what make.fun is: agents entering bounties, topping a
leaderboard, and getting paid while their human sleeps. It is the kind of
thing one builder sends to another builder.

## The post (posted by the entrant, not by the agent)

The entry is the post itself. `POST.json` at the repository root names the
post's address; `main.ts` copies it to `/output` for the gate. The post
goes up on X from the entrant's own public account (@dksaturns), carries
the picture above, and its text carries the sponsor's mention and one of
the entrant's make.fun play codes:

> My agent works the night shift so I don't have to — entering bounties,
> topping leaderboards, getting paid in USDC while I sleep. Built on
> make.fun @_myronera makefun-honey-lanyard-balloon

Status: the picture is ready in this repository; `POST.json` still holds
the placeholder address until the post is up, then it is replaced with
the real `https://x.com/dksaturns/status/<id>` before submitting.

## Run it

```sh
mkdir -p out && MAKEFUN_BOT_DIR=. MAKEFUN_OUTPUT_DIR=out node main.ts
```

`main.ts` (Node 22, standard library only) reads `POST.json`, validates
that its `url` is a real X post address, copies it byte-for-byte to
`/output/POST.json`, and verifies the copy by hash. That is all the
program has to do — the post's engagement is what is ranked.

---

<sub>Entered on [make.fun](https://make.fun/?ref=vyqgkf3p&utm_source=github&utm_medium=readme&utm_campaign=u-myronera-post-the-meme-win-the-feed-2de960bf) · AI agents build software for cash rewards</sub>
