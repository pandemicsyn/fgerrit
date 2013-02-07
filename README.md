fgerrit
=======

Why ? Because fark the gerrit web ui thats why. :goberserk:

## Wtf is this ?

A simple git extension that makes interacting with gerrit less painful by
wrapping the gerrit ssh api. Use it to:

-1 :sparkles:ALL:sparkles: the reviews!

...or you know, list review's, approve them, whatever floats your boat.

## Configuration
fgerrit will try to pull gerrit information automagically via your git config. To do so it checks to see if you have a gerrit remote branch by running a `git config --get remote.gerrit.url`. If you don't have gerrit a remote you can pass in the options at the cli. Or better yet, set the env variable:

`export GERRIT_URL=ssh://username@gerrit.host.com:29418/yourproject`

## Usage
It's just a git extension, just give it a try in a repo that uses gerrit. Heres a few quick examples to get you started.

List all open reviews:

	fhines@ubuntu:~/omgmonkeys(master)$ git fgerrit -l`
	====================================================
	= Open reviews for unicorns/meatgrinder       	   =
	====================================================
	id    	(date ) [V|C|A] "commit subject" - submitter
	----------------------------------------------------
	9kl1V	(02:31) [1|-2|0] "Fix bug: #121 snakes on plane" - sammyj
	7b251	(08/21) [1|1|0] "Implements a basic unicorn grinder" - pandemicsyn

Wanna see info on the review with the shortid 7b251 from above?

	git fgerrit -r 7b251

Is id 7b251 an abomination, wanna -1 that crap?

	git fgerrit -1 7b251

Need to drop some knowledge on a patch set?

	git fgerrit -m "switches love packets" 7b251

Here's all the options:

    Usage:
            git-fgerrit: [-l] [-r <review>] [-2|1|0|p|P|a <sha1>] [--verified=-1|0|+2]
                [-m message] [--abandon|--delete|--publish|--restore|--submit]
                [--user=gerrituser] [--host=gerrithost] [--port=gerritport]
                [--project <project>]

                Gerrit information defaults to gerrit remote url in git config or
                the GERRIT_URL env. The options --host, --user, --port, --project
                will override these defaults.

                Examples:
                List all pending reviews: git-fgerrit -l
                To -1 a patchset: git-fgerrit -1 7b251
                Submit a change: git-fgerrit --submit 7b251
                View review number 10101: git-fgerrit -r 10101
                View review with sha1 7b251: git-fgerrit -r 7b251

    Options:
      -h, --help            show this help message and exit
      -l, --list-all        list pending reviews
      -r, --review          display review
      -2, --set-2           score a patchset -2 on code review
      -1, --set-1           score a patchset -1 on a code review
      -0, --set-0           score a patchset 0 on a code review
      -p, --set-plus-1      score a patchset +1 on a code review
      -P, --set-plus-2      score a patchset +2 on a code review
      --verified=-1|0|+2    Set a verified score.
      -a, --approve         Approve a patch set
      -m "Message", --message="Message"
                            post message
      --abandon             Abandon a patch set
      --delete              Delete a draft patch
      --publish             Publish a draft patch
      --restore             Restore an abandoned patch set
      --submit              Submit a patch set
      --host=HOST           Gerrit hostname or ip
      --port=PORT           Gerrit port
      --user=USER           Gerrit user
      --project=PROJECT     Gerrit project

## Installation

- `git clone http://github.com/pandemicsyn/fgerrit fgerrit`
- `cd fgerrit`

Now either install via setup.py or build a debian package with [stdeb](https://github.com/astraw/stdeb)

- via setup.py
	- `sudo python setup.py install`
- via stdeb
	- `python setup.py --command-packages=stdeb.command bdist_deb`
	- `sudo dpkg -i deb_dist/python-statsdpy_0.0.X-1_all.deb`

This will drop the git-fgerrit command into /usr/local/bin so it'll get picked up by git.

