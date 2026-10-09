# Otherworldly: deployment and business brief

A condensed brief for a new chat that plans the full launch of the Otherworldly site. It is a plan only;
it changes nothing on the live atlases.

## What the project is

Otherworldly turns the worlds of favourite books into globes you can explore. Each one looks like a planet
seen from orbit. You zoom from orbit to standing on the ground and scrub a timeline to watch the story
happen: seasons change, characters travel, battles are fought, rulers rise and fall.

| World | Books | Live | Repo |
|---|---|---|---|
| Arda | The Hobbit, The Lord of the Rings | https://dustin-hoover.github.io/arda-atlas/ | `dustin-hoover/arda-atlas` |
| The Known World | A Song of Ice and Fire | https://dustin-hoover.github.io/known-world-atlas/ | `dustin-hoover/known-world-atlas` |
| Dungeon Crawler Carl | | announced | |
| Harry Potter | | announced | |

- **Tech:** plain JavaScript and MapLibre. All terrain and imagery are generated in the visitor's browser,
  so hosting is static files with almost no server cost. Each world is served by GitHub Pages from its
  repo's `main` branch.
- **Already in place:** a GoatCounter visit counter (account `otherworldly`) on both atlases.
- **The plan so far:** a combined site under its own name (not the owner's), with a gallery of worlds,
  each world on its own lazily loaded page, funded by ads, with a message board and a feedback channel.

## The laws (binding, from `docs/otherworldly/LAWS.md`)

- Facts from the books in our own words. No copied prose, maps, artwork, sigils or covers.
- Nothing from the film or TV adaptations, including likenesses, music and show-only material.
- Titles are used only to say which books a world follows. No logos or title fonts, and nothing that
  suggests endorsement. Every page says it is an unofficial fan project.
- **An intellectual-property lawyer must review the project before anything is sold, sponsored or
  earns money.** Ads and a store both fall under this rule, so the plan must schedule that review first.

## How the owner works

- Changes go to a work branch. The owner sees screenshots, and nothing merges to `main` or goes live
  until they say "merge".
- Keep each world's repo separate. The owner wants the Arda link kept "pure".
- Plain-language updates. The owner often reads on a phone.

## What the new chat should plan

1. **Deployment and scaling:** a domain and name for the combined site, hosting and CDN beyond GitHub
   Pages, the landing-page gallery, performance on phones, and a way to add worlds without breaking live
   ones.
2. **Sharing and launch:** which communities and social platforms to launch on (book fandom forums,
   Reddit, YouTube, TikTok, Instagram, X, Bluesky), what to show (short clips of the globe and the
   timeline), the order and timing, and how to measure results with GoatCounter.
3. **A free-to-play money model:** everything fun stays free. Options to weigh: ads (which networks
   accept fan sites, and how to keep them from slowing the globe), voluntary support (Patreon, Ko-fi,
   GitHub Sponsors), and a store selling only original art and merchandise. Every option must pass the
   laws and the lawyer review above, and the plan should estimate costs and income.
4. **Community:** a place to chat and suggest improvements (for example Discord, GitHub Discussions or
   an on-site board), moderation, and how good suggestions reach the work queue.
5. **Locking down the code:** options for repo visibility (GitHub Pages on a private repo needs a paid
   plan or another host), a licence choice, keeping secrets and keys out of the client, branch
   protection, and what is realistic for code that runs in every visitor's browser.
6. **A phased roadmap:** what to do first, what waits, and what each phase costs.

## Starting prompt for the new chat

Paste this as the first message of a new session in this project:

> This chat is for planning the launch and business of the Otherworldly site only. Don't change the
> live sites. Attach `dustin-hoover/known-world-atlas` and `dustin-hoover/arda-atlas`. Read
> `docs/DEPLOYMENT_BRIEF.md`, `docs/HANDOFF.md`, `CLAUDE.md` and everything in `docs/otherworldly/` in
> known-world-atlas, and Arda's own handoff and `CLAUDE.md` if it has them. Then use the session tools
> (`list_sessions` and `list_events`) to read my earlier sessions on these projects, including the Arda
> chat and session `session_0123Mi8FZ1iTXRJo5i25n56A`, for any decisions about the combined site, ads,
> the visit counter or the community. Tell me in a few lines what you found, then ask me any questions
> you need before we work through the six planning areas in the brief one at a time. Write the
> finished plan as `docs/LAUNCH_PLAN.md` on a work branch. Don't merge anything until I say "merge".
