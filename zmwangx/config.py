#!/usr/bin/env python3

"""Reading and writing configuration file."""

# pylint: disable=too-few-public-methods,invalid-name

import configparser
import json
import os

import yaml


class Config(object):
    """Class for reading and writing config file.

    The config file is either in a subdirectory of $XDG_CONFIG_HOME, if
    it is set, or $HOME/.config.

    This class is meant to be inherited. Configuration file path is
    stored in the ``_config_file`` attribute, and the configuration is
    stored in the ``_conf`` attribute. A subclass should implement
    ``_get_configs`` for initializing ``_conf`` from ``_config_file,
    ``rewrite_configs`` for updating the config file, and optionally
    override ``__getitem__``, ``__setitem__``, which currently just
    retrieves or assigns to ``self._conf[key]``. Delete
    ``rewrite_configs`` and ``__setitem__`` if the config file is meant
    to be read-only.

    Note that the attributes and methods of ``_conf`` are exposed
    through ``self`` in case it is neither already an instance attribute
    of ``self`` nor implemented in the class tree of ``self``.

    Parameters
    ----------
    config_path : str
        The path of config file relative to $XDG_CONFIG_HOME, or
        $HOME/.config, if $XDG_CONFIG_HOME is not defined.
    allow_missing : bool, optional
        When the config file cannot be found, if ``allow_missing`` is
        ``True``, then silently make the directories and create an empty
        config file; otherwise, raise ``OSError`` and the ``Config``
        object won't be initiliazed.

    Raises
    ------
    OSError
        If ``allow_missing`` is ``False`` and the config file is not
        found.

    """

    def __init__(self, config_path, allow_missing=False):
        """Init."""
        self._get_config_file(config_path, allow_missing)
        self._get_configs()

    def _get_config_file(self, config_path, allow_missing):
        """Locate the config file."""
        if "XDG_CONFIG_HOME" in os.environ:
            config_file = os.path.join(os.environ["XDG_CONFIG_HOME"],
                                       config_path)
        else:
            config_file = os.path.expanduser("~/.config/%s" % config_path)
        if not os.path.exists(config_file):
            if not allow_missing:
                raise OSError("config file '%s' not found" % config_file)
            else:
                os.makedirs(os.path.dirname(config_file), mode=0o700, exist_ok=True)
                with open(config_file, "w"):
                    pass  # write empty file
        self._config_file = config_file
        return config_file

    def _get_configs(self):
        """Read user configurations.

        This method should be overrided.

        """
        self._conf = None
        raise NotImplementedError

    def rewrite_configs(self):
        """Rewrite config file with current configs.

        This method should be overrided.

        """
        raise NotImplementedError

    def __getitem__(self, key):
        """self[key]."""
        return self._conf[key]

    def __setitem__(self, key, value):
        """Assignment to self[key]."""
        self._conf[key] = value

    def __getattr__(self, name):
        """Access to self._conf attributes."""
        try:
            if name == "_conf":
                raise AttributeError
            return getattr(self._conf, name)
        except AttributeError:
            raise

class INIConfig(Config):
    """Class for reading and writing INI config file.

    For basic information, see the docs of `zmwangx.config.Config`.

    In addition to `zmwangx.config.Config` constructor arguments, this
    class also supports ``**kwargs`` which will be passed directly to
    the standard library ``configparser.ConfigParser`` constructor.

    An instance of this class supports access and assignment via
    subscripts just like a standard library
    ``configparser.ConfigParser`` object. Other methods of
    ``configparser.ConfigParser`` are also supported (e.g.,
    ``has_section``). See
    https://docs.python.org/3/library/configparser.html#configparser-objects
    for details.

    Attributes
    ----------
    config : configparser.ConfigParser

    """

    def __init__(self, config_path, allow_missing=False, **kwargs):
        """Init."""
        self._conf = configparser.ConfigParser(**kwargs)
        self.conf = self._conf
        super().__init__(config_path, allow_missing)

    def _get_configs(self):
        """Read user configurations."""
        self._conf.read(self._config_file)

    def rewrite_configs(self):
        """Rewrite config file with current configs."""
        with open(self._config_file, "w", encoding="utf-8") as fp:
            self._conf.write(fp)


class JSONConfig(Config):
    """Class for reading and writing JSON config file.

    For basic information, see the docs of `zmwangx.config.Config`.

    An instance of this class can be treated like an object returned by
    ``json.load``, supporting both subscripts and item assignment.

    """

    def _get_configs(self):
        """Read user configurations."""
        with open(self._config_file, encoding="utf-8") as fp:
            self._conf = json.load(fp)

    def rewrite_configs(self):
        """Rewrite config file with current configs."""
        with open(self._config_file, "w", encoding="utf-8") as fp:
            json.dump(self._conf, fp, indent=4)


class YAMLConfig(Config):
    """Class for reading and writing YAML config file.

    For basic information, see the docs of `zmwangx.config.Config`.

    An instance of this class can be treated like an object returned by
    ``yaml.safe_load``, supporting both subscripts and item assignment.

    """

    def _get_configs(self):
        """Read user configurations."""
        with open(self._config_file, encoding="utf-8") as fp:
            self._conf = yaml.safe_load(fp.read())

    def rewrite_configs(self):
        """Rewrite config file with current configs."""
        with open(self._config_file, "w", encoding="utf-8") as fp:
            fp.write(yaml.dump(self._conf, default_flow_style=False))
