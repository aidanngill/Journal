# Journal

Organize tiles for your Listography page effortlessly and automatically.

## Requirements

* Python 3.6

Depending on what services you wish to use, you may also require accounts on the following platforms.

* [*Steam*](https://steamcommunity.com/)
* [*Last.fm*](https://last.fm/)

You will also require a [*Listography*](https://listography.com) account if you wish to make use of the formatted strings you generate.

## Usage

### Example

You may type `py -m journal --help` to view all options. An example of usage for Steam would be the following.

```bash
py -m journal -m Steam -u 1234 -a 5678 profile_info recently_played
```

This will generate text for the module *Steam* using the Steam ID *1234* as the input, and *5678* as authorization, with *profile_info* and *recently_played* being the functions used to generate the blocks of text.

### Listing Modules

```bash
> py -m journal --list-modules
< Steam, AudioScrobbler
```

### Listing Functions

```bash
> py -m journal --module Steam --list-functions
< Steam: recently_played, profile_info
```
