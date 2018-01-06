# tfs-unbind
This repo has some scripts that unbind TFS(TFVC) project for Microsoft Visual Studio.

# Caution

I'm japanese. so some script include Japanese comments.

# Conda Environment

```sh
$ cd PROJECT_ROOT
$ conda env create -f conda-env.yml
$ source activate tfsunbind
```

# Unit Test

```sh
$ cd PROJECT_ROOT
$ py.test
```

# Run script

```sh
$ cd PROJECT_ROOT
$ source activate tfsunbind
$ python -m tfs.unbinder src-dir dest-dir
```
