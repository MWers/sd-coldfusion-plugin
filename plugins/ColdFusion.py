"""
  Server Density Plugin
  ColdFusion stats
  https://github.com/MWers/sd-coldfusion-plugin/
  Version: 1.0.1
"""
import os
import platform
import subprocess


class ColdFusion:
    sd_cfstat_opt = 'coldfusion_cfstat_path'
    cfstat_locations = ['/opt/coldfusion11/bin/cfstat',
                        '/opt/coldfusion10/bin/cfstat',
                        '/opt/ColdFusion9/bin/cfstat',
                        '/opt/coldfusion8/bin/cfstat',
                        '/opt/coldfusionmx7/bin/cfstat']
    cfstat_keys_long = ['Pg/s Now', 'Pg/s Hi', 'DB/s Now', 'DB/s Hi',
                        'CP/s Now', 'CP/s Hi', 'Reqs Q''ed', 'Reqs Run''g',
                        'Reqs TO''ed', 'Tpl Q''ed', 'Tpl Run''g', 'Tpl TO''ed',
                        'Flash Q''ed', 'Flash Run''g', 'Flash TO''ed',
                        'CFC Q''ed', 'CFC Run''g', 'CFC TO''ed',
                        'WebSvc Q''ed', 'WebSvc Run''g', 'WebSvc TO''ed',
                        'Avg Q Time', 'Avg Req Time', 'Avg DB Time',
                        'Bytes In/s', 'Bytes Out/s']
    cfstat_keys_short = ['Pg/s Now', 'Pg/s Hi', 'DB/s Now', 'DB/s Hi',
                         'CP/s Now', 'CP/s Hi', 'Reqs Q''ed', 'Reqs Run''g',
                         'Reqs TO''ed', 'Avg Q Time', 'Avg Req Time',
                         'Avg DB Time', 'Bytes In/s', 'Bytes Out/s']
    python_version = platform.python_version_tuple()

    def __init__(self, agent_config, checks_logger, raw_config):
        self.agent_config = agent_config
        self.checks_logger = checks_logger
        self.raw_config = raw_config

    def run(self):
        # Determine location of cfstat and make sure it's executable
        cfstat = None
        if 'Main' in self.raw_config and \
                        self.sd_cfstat_opt in self.raw_config['Main']:
            cfstat = self.raw_config['Main'][self.sd_cfstat_opt]
            if not os.access(cfstat, os.X_OK):
                self.checks_logger.error('ColdFusion: The location of cfstat '
                                         'given in config (%s) either does '
                                         'not exist or is not executable'
                                         % cfstat)
                return False
            else:
                self.checks_logger.debug('ColdFusion: Using cfstat defined in '
                                         'config: %s' % cfstat)

        else:
            self.checks_logger.debug('ColdFusion: cfstat path not in config, '
                                     'checking standard locations')
            for location in self.cfstat_locations:
                if os.access(location, os.X_OK):
                    cfstat = location
                    self.checks_logger.debug('ColdFusion: Using cfstat found '
                                             'here: %s' % cfstat)
                    break
            if not cfstat:
                self.checks_logger.error('ColdFusion: Could not find cfstat')
                return False

        # Run cfstat and collect its data
        self.checks_logger.debug('ColdFusion: Getting stats from ColdFusion')
        proc = subprocess.Popen([cfstat, '-x', '-n', '-s'],
                                stdout=subprocess.PIPE, close_fds=True)
        stats = proc.communicate()[0]

        if int(self.python_version[1]) >= 6:
            try:
                proc.kill()
            except Exception, e:
                self.checks_logger.debug('ColdFusion: cfstat process already '
                                         'terminated')

        stats = stats.split()
        if len(stats) == 26:
            keys = self.cfstat_keys_long
        elif len(stats) == 14:
            keys = self.cfstat_keys_short
        else:
            self.checks_logger.error('ColdFusion: Received unexpected '
                                     'response from cfstat: %s' % str(stats))
            return False

        data = dict(zip(keys, stats))
        return data
