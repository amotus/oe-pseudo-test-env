Readme
======

A reproducible environment for experiments and automated tests
on [open embedded *pseudo*].

Includes:

 -  a nix package for open-embedded *pseudo*.
 -  a set python tests tool allowing to properly test *pseudo*.
 -  a set of pytest tests for testing edges *pseudo* cases.


[open embedded *pseudo*]: http://git.yoctoproject.org/cgit/cgit.cgi/pseudo/about/?h=oe-core


Pre-requisites
--------------


 -  A posix system (e.g: Linux, Unix)
 -  [nix]
 -  [gnumake]


[nix]: https://nixos.org/download.html
[gnumake]: https://www.gnu.org/software/make/


Usage
-----

### Enter the pure reproducible environment

With this option, the `oe-pseudo` nix package will be automatically installed in
`PATH`:

```bash
$ cd /path/to/this/repo
$ make shell-installed-pure
# ..
$ pseudo -h
Usage: pseudo [-dflv] # ..
# ..
```

Note that in this *pure* environment, none of your system dependencies will be
available as all envs have been reset.

A more relaxed / impure version is available:

```bash
$ cd /path/to/this/repo
$ make shell-installed
# ..
```

### Enter a dev environment

```bash
$ cd /path/to/this/repo
$ nix-shell  # or alternatively '$ make shell-dev'.
$ pseudo -h
pseudo: command not found
```

With this option, the `oe-pseudo` nix package has first to be manually built in
order for it to be available in path:

```bash
$ make release
# Result now available under './result', the './result/bin'
# directory already in 'PATH':
$ pseudo -h
Usage: pseudo [-dflv] # ..
# ..
```

The preceding used a **pinned** version of `pseudo`'s sources. In case you want
to work with a **local git repository**, just clone you `pseudo` repository
beside this repository and launch the following build task instead:

```bash
# This overrides the 'oe-peudo' package's sources with
# those in the directory at '../pseudo'.
$ make release-local
# ..
$ pseudo -h
# ..
```

This is a great way to work with a modified `pseudo` version.


### Launch automated tests

From one of the above environment:

```bash
$ pytest
# ..
```

It is possible to run a single test case. Simply add its full test case path
to your `pytest` invocation:

```bash
$ pytest ./tests/test_600_pseudo_cmd_case.py::test_pseudo_cmd_case[rename/existing_target.sh]
# ..
```


### Lauching pseudo from the cli

We also provide a little script your can source in order to set the environment
variables required by `pseudo` similarly to how our test utilities do. This
might be helpful for quick cli experiments. This effectively reproduce manually
what our python test utility at `test_lib/pseudo.py` does for you when launching
test cases.

Open a first terminal, and launch the `pseudo` server in the foreground:

```bash
$ . ./contrib/pseudo-test-env.sh
$ pseudo -f
# ..
```

From another terminal, launch the `pseudo` client:

```bash
$ . pseudo-test-env.sh
$ pseudo ./test_lib/data/cmd_cases/rename/existing_target.sh
# ..
```

Everything will be in your current directory under `./pseudo-test-fs`.

You can then query the state of the `files.db` and
see if it properly matches the `rootfs`:

```bash
$ sqlite3 ./pseudo-test-fs/state/files.db 'select * from files order by id'
# ..
$ ls -li ./pseudo-test-fs/rootfs
# ..
```

Note that you can also active various debug logs via the `PSEUDO_DEBUG`
environment variable. This should be set for both the server and client
invocation. A little example:

```bash
$ PSEUDO_DEBUG=fd pseudo -f
# ..
# You should get both files and db logs here.
```

```bash
$ PSEUDO_DEBUG=of pseudo ./test_lib/data/cmd_cases/rename/existing_target.sh
# ..
# You should get both files and operations logs here.
```

A listing of available debug types is available at:

 -  [enum/debug_type.in](http://git.yoctoproject.org/cgit/cgit.cgi/pseudo/tree/enums/debug_type.in?h=oe-core)

    The first column whet set in uppercase match `${X}` in the
    `pseudo_debug(PDBGF_${X}` debug trace from the code base.

    The second column is the flag to use in the `PSEUDO_DEBUG` value.


### Enter the `oe-pseudo` package reproducible build env

Advanced users only. This should only be required in case the `oe-pseudo` nix
package require modifications / is no longer suitable to build you version of
the `pseudo` source code.

```bash
$ make shell-build
# ..
```

From there, you will be able to manually build the
package in the exact same environment as nix:

```bash
$ genericBuild
# ..
$ pwd
/path/to/this/repo/pseudo-b988b0a
$ ./bin/pseudo -h
Usage: pseudo [-dflv] # ..
# ..
```

`pseudo-b988b0a` is the source dir + the build outputs.

This is a great way to iterate on a patch.

You should be able to control the executed build phases using the `phases`
environment variable and the build output dir using the `out` variable. See
[Using nix-shell for package development] for more details.

A quick example:

```bash
$ out="$PWD/build" phases="unpackPhase patchPhase configurePhase" genericBuild
# ..
$ make
# ..
```

[Using nix-shell for package development]: https://nixos.wiki/wiki/Nixpkgs/Create_and_debug_packages#Using_nix-shell_for_package_development


Maintainers
-----------

### Adding a new test case

 1. Add a new executable shell script under `./test_lib/data/cmd_cases` (e.g.
    `my_operation/my_case_script.sh`).

 2. In `./tests/test_600_pseudo_cmd_case.py`, just over the `test_pseudo_cmd_case`
    test function, add the relative path to you test case to the listing
    (e.g.: `my_operation/my_case_script.sh`).

 3. Run your test case:

    ```bash
    $ pytest tests/test_600_pseudo_cmd_case.py::test_pseudo_cmd_case[my_operation/my_case_script.sh]
    # ..
    ```

### Update pinned `pseudo` sources

 1. In `./default.nix`, in the attribute set passed as argument to the
    `fetchFromGitHub` function, change the `rev` attribute the the new
    git revision.

 2. Introduce a slight change to the `sha256` attribute.

 3. Launch a new build or attempt to enter the nix env again,
    you will be provided with the proper `sha256` value (value immediatly after
    `got` from the output of the command):

    ```bash
    $ nix release
    # ..
    hash mismatch in fixed-output derivation # ..:
    wanted: sha256:10qx9i1y8ddqhbsj9677920wqfgqpjmg2q6zzjm6yrqkf6bbd363
    got:    sha256:10qx9i1y8ddqhbsj9777920wqfgqpjmg2q6zzjm6yrqkf6bbd363
    # ..
    ```

    Note that it is also possible to use the `nix-prefetch-*` tools to retrieve
    the proper hash but the above is a much simpler mean.


Contributing
------------

Contributing implies licensing those contributions under the terms of
[LICENSE](./LICENSE), which is an *Apache 2.0* license.

Note that in case the open-embedded core team were to take this project
under its umbrella so that these tests are run regularly under its CI,
the author is more than open to relicense this or part of this work
under a different license.
