# Geodyssey: deployment brief

A condensed brief for whoever plans the full launch of the Geodyssey site. It is a plan only;
it changes nothing on the live atlases.

## What the project is

Geodyssey turns the worlds of favourite books into globes you can explore. Each one looks like a planet
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
- **No tracking:** the pages load nothing from other sites (no analytics, fonts or libraries from elsewhere).
- **The plan so far:** a combined site under its own name (not the owner's), with a gallery of worlds,
  each world on its own lazily loaded page, with a message board and a feedback channel. It is a free,
  non-commercial reference: nothing for sale, no ads, no sponsors.

## The laws (binding, from `docs/geodyssey/LAWS.md`)

- Facts from the books in our own words. No copied prose, maps, artwork, sigils or covers.
- Nothing from the film or TV adaptations, including likenesses, music and show-only material.
- Titles are used only to say which books a world follows. No logos or title fonts, and nothing that
  suggests endorsement. Every page says it is an unofficial fan project.
- **Nothing for sale.** The atlases are a free, non-commercial fan reference. An intellectual-property lawyer
  must review the project before anything could ever be sold, sponsored, advertised or promoted.

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
   timeline), and the order and timing. There is no analytics on the pages; judge results from replies and
   feedback.
3. **Costs without income:** the atlases stay free and earn nothing. Plan for hosting and a domain on a
   hobby budget, and what to do if traffic outgrows free static hosting.
4. **Community:** a place to chat and suggest improvements (for example Discord, GitHub Discussions or
   an on-site board), moderation, and how good suggestions reach the work queue.
5. **Locking down the code:** options for repo visibility (GitHub Pages on a private repo needs a paid
   plan or another host), a licence choice, keeping secrets and keys out of the client, branch
   protection, and what is realistic for code that runs in every visitor's browser.
6. **A phased roadmap:** what to do first, what waits, and what each phase costs.

## Starting prompt for the new chat

Paste this as the first message of a new session in this project:

> This chat is for planning the launch of the Geodyssey site only. Don't change the live sites. Attach
> `dustin-hoover/known-world-atlas` and `dustin-hoover/arda-atlas`. Read `docs/DEPLOYMENT_BRIEF.md`,
> `docs/HANDOFF.md`, `AGENTS.md` and everything in `docs/geodyssey/` in known-world-atlas (on `main`), and
> Arda's own handoff and notes if it has them. Tell me in a few lines what you found, then ask me any
> questions you need before we work through the six planning areas in the brief one at a time. Write the
> finished plan as `docs/LAUNCH_PLAN.md` on a work branch. Don't merge anything until I say "merge".
