# The Unofficial Hello Internet Relisten
This feed will be automatically updated to publish an episode of Hello Internet weekly, starting Friday, May 1st, 2026. It's picked to coincide with a new weekly discussion on the [newly liberated](https://old.reddit.com/r/HelloInternet/comments/1st33b1/new_moderation_for_the_sub_transparency_and/) Hello Internet [subreddit](https://old.reddit.com/r/HelloInternet/).

The feed URL you should put in your podcast client is: https://raw.githubusercontent.com/inahaystack/unofficial-hi-relisten/refs/heads/main/feed.xml

I was inspired by [this](https://github.com/yottalogical/hello-internet-archive) project which cleverly made an alternative feed for the podcast by simply linking to the old files which are still accessible, and also [this](https://old.reddit.com/r/HelloInternet/comments/1sukc4a/hi_episode_discussions_coming_in_1_week/) announcement to have the audience relisten on a particular schedule.

This works by purely linking to the URLs that were published with the original release of the podcast, so there is no freebooting. Out of curiosity, I've modified the links for analytics with the publicly available [op3.dev](https://op3.dev/) service. Once I have the analytics working I'll post a link for them here.

Technically, it works by a Github Action that runs every day, and updates the feed according to the schedule.csv file. This then updates the feed.xml file with information already stored in the episodes.json file, which comes from the original RSS file and yottalogical's archive file. The first (or 0th, if you prefer) episode is a test so I can see that the system is working.

My programming skills are many years old and out of practice, so I had Claude assist with writing the scripts to generate this. Any PRs or advice from humans who know what they're doing is very welcome.
