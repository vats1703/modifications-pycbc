""" Utilities for handling waveform plugins
"""


def add_custom_waveform(approximant, function, domain,
                        sequence=False, force=False):
    """ Make custom waveform available to pycbc

    Parameters
    ----------
    approximant : str
        The name of the waveform
    function : function
        The function to generate the waveform
    domain : str
        Either 'frequency' or 'time' to indicate the domain of the waveform.
    sequence : bool, False
        Function evaluates waveform at only chosen points (instead of a
        equal-spaced grid).
    """
    from pycbc.waveform.waveform import cpu_fd, cpu_td, fd_sequence

    used = RuntimeError("Can't load plugin waveform {}, the name is"
                        " already in use.".format(approximant))

    if domain == 'time':
        if not force and (approximant in cpu_td):
            raise used
        cpu_td[approximant] = function
    elif domain == 'frequency':
        if sequence:
            if not force and (approximant in fd_sequence):
                raise used
            fd_sequence[approximant] = function
        else:
            if not force and (approximant in cpu_fd):
                raise used
            cpu_fd[approximant] = function
    else:
        raise ValueError("Invalid domain ({}), should be "
                         "'time' or 'frequency'".format(domain))


def add_length_estimator(approximant, function):
    """ Add length estimator for an approximant

    Parameters
    ----------
    approximant : str
        Name of approximant
    function : function
        A function which takes kwargs and returns the waveform length
    """
    from pycbc.waveform.waveform import _filter_time_lengths
    if approximant in _filter_time_lengths:
        raise RuntimeError("Can't load length estimator {}, the name is"
                           " already in use.".format(approximant))
    _filter_time_lengths[approximant] = function


def retrieve_waveform_plugins():
    """ Process external waveform plugins
    """
    import pkg_resources

    # Check for fd waveforms
    for plugin in pkg_resources.iter_entry_points('pycbc.waveform.fd'):
        add_custom_waveform(plugin.name, plugin.resolve(), 'frequency')

    # Check for fd sequence waveforms
    for plugin in pkg_resources.iter_entry_points('pycbc.waveform.fd_sequence'):
        add_custom_waveform(plugin.name, plugin.resolve(), 'frequency',
                            sequence=True)

    # Check for td waveforms
    for plugin in pkg_resources.iter_entry_points('pycbc.waveform.td'):
        add_custom_waveform(plugin.name, plugin.resolve(), 'time')

    # Check for waveform length estimates
    for plugin in pkg_resources.iter_entry_points('pycbc.waveform.length'):
        add_length_estimator(plugin.name, plugin.resolve())
