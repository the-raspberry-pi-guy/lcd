# Contributing
Community help is very much appreciated and there are many ways you can help developing and maintaining this repository.  If you want to get involved, please read the following:
- [Issues](#issues)
- [Pull Requests](#pull-requests)

---

## Issues
This repository allows users to create an issue in the [issues tab][issues-tab].  Any issue must be **directly related to a file hosted in this repo**, as opposed to an issue with LCD modules, wiring, the Raspberry Pi OS, and so on.

### Types of issues
#### Bug
Bugs refer to **replicable** issues directly related to **the latest version** of one or more of the following files:
  - [`configs/*`][configs-dir]
  - [`drivers/*`][drivers-dir]
  - [`install.sh`][install.sh]
  - [`setup.sh`][setup.sh]

Before reporting a bug, make sure to double check the wiring and try different wires first, especially if the associated error is I/O related.  Also, check the [issues tab][issues-tab] for open and closed issues that might be related to your own issue.

When reporting a bug, it is crucial to add all the relevant information to allow other users, contributors, and maintainers to replicate the reported bug. At the very least, include the following information when reporting a bug:
  - A copy of the executed command and the entire error in [code blocks][gh-docs-code-blocks]. For example:
    ```sh
    python demo_clock.py
    ```
    ```python
    Traceback (most recent call last):
    File "demo_clock.py", line 14, in display = drivers.Lcd()
    File "/home/pi/lcd/drivers/i2c_dev.py", line 103, in init self.lcd_write(0x03)
    File "/home/pi/lcd/drivers/i2c_dev.py", line 126, in lcd_write self.lcd_write_four_bits(mode | (cmd & 0xF0))
    File "/home/pi/lcd/drivers/i2c_dev.py", line 121, in lcd_write_four_bits self.lcd.write_cmd(data | LCD_BACKLIGHT)
    File "/home/pi/lcd/drivers/i2c_dev.py", line 74, in write_cmd self.bus.write_byte(self.addr, cmd)
    IOError: [Errno 121] Remote I/O error
    ```
  - Python version (`python --version`)
  - Information about the host machine and OS (`hostnamectl` or `lsb_release -a`)

#### Compatibility
The LCD driver was written for and tested with **Python 2.7**, as in the original [Youtube tutorial][youtube-tutorial] and scripts.  Python 3.x may or may not work and even though you can still create an issue to describe a compatibility error, we cannot guarantee support.  However, we're happy to incorporate any changes that adds compatibility with Python 3.x **as long as they do not break Python 2.7 usage**.  Take a look at how to submit a PR in the [pull requests](#pull-requests) section if you want to help with that.

#### Demo
Demo issues are directly related to any of the hosted `demo_*.py` files. When creating such a demo issue, attach the same information as if you were creating a [bug](#bug) issue report.  In addition, ping the user who introduced the demonstration file in the first place (e.g., for the `demo_netmonit.py`, refer to [@cgomesu][cgomesu]) or one of the demo contributors.  (Of note, the maintainers and other contributors may not always be available to help with such issues because they are not always involved with the creation and maintenance of such demo files.)

#### Documentation
A documentation issue refers to typos or missing information in the [Wiki][wiki] or [README.md][readme] file.

#### Other nature
Any other issue that is directly related to this repository and was not covered before.

[top :arrow_up:](#)

---

## Pull Requests
A pull request (PR) allows you to push changes from your fork directly into [`the-raspberry-pi-guy/lcd`][lcd-repo] repository to make the changes available to other users. Multiple [types of PRs](#types-of-prs) can be submitted to this repository but regardless of the type, please observe the following:

- **Ask before submitting a PR**. If it is a bug that you want to fix, then [create an issue](#issues) first, for example, and in addition to the usual [bug related information](#bug), append your suggested solution for it. Otherwise, you might waste time on something that the maintainers and contributors do not feel like merging into the project.

- The maintainers try to keep the repo as compatible with the [original Youtube tutorial][youtube-tutorial] as possible.  That is, avoid the introduction of changes that are **incompatible with the tutorial** at all cost.  If that is not possible, it should be made explicit that the PR introduces changes incompatible with the tutorial and then it is your job to convince the maintainers that such changes are worthwhile.

- Everything (from comments to code to documentation) should be **written in English**;

- Always **fork** > **clone** your fork > configure the **remotes** > and then create a **new branch** from the latest `master` to work on the changes you want to make (e.g., `hotfix/i2c-bug`). This makes a world of difference when it is required to make additional changes to a PR and it helps keeping things organized. Here is an illustration of the standard procedure:
  1. [Create a fork][gh-docs-fork] of the project using your GitHub account (`<YOUR-USERNAME>`);

  2. Clone your fork on your host machine, move into its root directory, and configure the upstream remote:
     ```sh
     git clone git@github.com:<YOUR-USERNAME>/lcd.git
     cd lcd
     git remote add upstream https://github.com/the-raspberry-pi-guy/lcd.git
     ```
  3. If it has been a while since you last cloned, fetch the latest changes from upstream and merge them to the master branch:
     ```sh
     git checkout master
     git pull upstream master
     ```
  4. From an up-to-date master, create a new branch (`<TOPIC>`) for working on your changes:
     ```sh
     git checkout -b <TOPIC>
     ```
  5. **Do the work**.  You can always check the current branch you are on as follows:
     ```sh
     git branch
     ```

- When making changes, **stick to the point** of your PR.  That is, avoid making changes in other parts of the code if the remaining code works as intended when all is said and done;

- [Write meaningful][commit-messages] commit messages to your changes and use formal language. Those messages are what will eventually become part of the repo's commit history and they help others understand what, how, and when. For this reason, make use of [`git rebase`][gh-docs-rebase] to organize your commits before pushing them anywhere else. In addition, please try to keep the number of commits to a minimum;

- When you're done staging and committing the changes, catch up with the upstream (fetch and then merge/rebase) if you expect that there will be conflicts upon merging the changes from your PR (e.g., if someone has worked on the same file and code block as you after you branched out from master, then this will create a conflict later on when trying to merge the changes from your PR into the original repo's master):
  ```sh
  git pull --rebase upstream master
  ```
  and if there are conflicts, [resolve them][gh-docs-conflicts]:
    1. `git status` to show the conflict;
    2. Edit the conflicting file to resolve the lines between `<<< || >>>` and save the file;
    3. `git add <CONFLICTING-FILE>` to add the change (or `git rm <CONFLICTING-FILE>` if resolving the conflict means removing the file);
    4. `git rebase --continue` to continue the rebasing;
    5. Repeat the steps 2-4 until all conflicts are resolved.


- When you're done resolving any possible conflicts, push your `<TOPIC>` branch to your fork:
  ```sh
  git push origin <TOPIC>
  ```
  (If you had to resolve any conflicts before pushing your changes, you should see an error because you rewrote history. To solve this, simply append `--force-with-lease` to the previous command.)

- Navigate to your fork:`TOPIC` branch and [open a PR][gh-docs-pr] to the `the-raspberry-pi-guy/lcd:master` branch. Then, at the very least, add the following to the PR:
  - **Clear title** for the main change(s);
  - Brief description **the reason** for the PR;
  - **Summary** of the changes.


- The commit history in your PR should contain **only changes made by you**. Otherwise, do not submit the PR and instead, go back to your local `TOPIC` branch and fix the commit history before moving on with the PR.

- Be mindful that the maintainers and contributors are not always available for multiple reasons.  Therefore, it might take a few days until you get any sort of feedback on your PR.  **Please be patient**.

### Types of PRs
There are six types of PRs that can be submitted to this repository:
1. Demo submission:
   - Should introduce aspects not covered in previous demonstration files. See the `demo_*.py` files for reference.
2. Documentation:
   - Typo fix;
   - Any new (or improvement of existing) explanation of how to use the LCD driver.
3. Bug fix;
4. Compatibility improvement;
5. New feature;
6. New implementation.

Of note, PRs that **introduce new features or implementations** should be well justified and explained in detail.

### Reviews
If you have contributed to the repository before and noticed that there's a new PR without a reply from the maintainers, then you can help out by [writing a review][gh-docs-review].  The reviews do not need to be comprehensive and instead, you can focus on the aspects that you are more comfortable with but in such a case, be explicit about what part of the PR you chose to review.

Keep in mind that English is not everyone's first language but everything should be written in English.  Please be patient but do point out grammatical errors that should be fixed before merging changed files into the repo's `master` branch.

[top :arrow_up:](#)

---

Lastly, this should go without saying but **be nice** with other users.  We welcome everyone from any sort of background.  If you are an experienced user, please consider spending a few additional minutes to explain your rational and provide more information than usual.  For many, this is an opportunity to get familiar with GNU/Linux, cli, git, github, and languages like Python.

Thank you for taking the time to learn how to contribute!  This is an old repository--the [initial commit][initial-commit] was made in 2015--and it has been maintained by and received contributions from people all over the globe.  Feel free to reach out if you feel you can improve and build upon what has been done so far.

:earth_americas::rocket:


[cgomesu]: https://github.com/cgomesu
[commit-messages]: https://chris.beams.io/posts/git-commit/
[configs-dir]: https://github.com/the-raspberry-pi-guy/lcd/tree/master/configs
[drivers-dir]: https://github.com/the-raspberry-pi-guy/lcd/tree/master/drivers
[gh-docs-code-blocks]: https://docs.github.com/en/github/writing-on-github/working-with-advanced-formatting/creating-and-highlighting-code-blocks
[gh-docs-conflicts]: https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/addressing-merge-conflicts/resolving-a-merge-conflict-using-the-command-line
[gh-docs-fork]: https://docs.github.com/en/get-started/quickstart/fork-a-repo
[gh-docs-pr]: https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request
[gh-docs-rebase]: https://docs.github.com/en/get-started/using-git/about-git-rebase
[gh-docs-review]: https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/reviewing-changes-in-pull-requests/about-pull-request-reviews
[initial-commit]: https://github.com/the-raspberry-pi-guy/lcd/commit/a0100b81c403a2f1b86e87e70ca1fe6b75a983df
[install.sh]: https://github.com/the-raspberry-pi-guy/lcd/blob/master/install.sh
[issues-tab]: https://github.com/the-raspberry-pi-guy/lcd/issues
[lcd-repo]: https://github.com/the-raspberry-pi-guy/lcd
[readme]: https://github.com/the-raspberry-pi-guy/lcd/blob/master/README.md
[setup.sh]: https://github.com/the-raspberry-pi-guy/lcd/blob/master/setup.sh
[youtube-tutorial]: https://www.youtube.com/watch?v=fR5XhHYzUK0
[wiki]: https://github.com/the-raspberry-pi-guy/lcd/wiki
