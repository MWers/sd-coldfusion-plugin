import os
import platform
import subprocess

pythonVersion = platform.python_version_tuple()
python24 = platform.python_version().startswith('2.4')

class ColdFusion:
	def __init__(self, agentConfig, checksLogger, rawConfig):
		self.agentConfig = agentConfig
		self.checksLogger = checksLogger
		self.rawConfig = rawConfig
		
	def run(self):
		# Determine location of cfstat and make sure it's executable
		self.checksLogger.debug('ColdFusion: Checking for cfstat path in config')
		if 'Main' not in self.rawConfig and 'coldfusion_cfstat_path' not in self.rawConfig.Main:
			self.checksLogger.debug('ColdFusion: cfstat path not in config, checking usual locations')
			if os.access('/opt/ColdFusion9/bin/cfstat',os.X_OK):
				cfstat = '/opt/ColdFusion9/bin/cfstat'
			elif os.access('/opt/coldfusion8/bin/cfstat',os.X_OK):
				cfstat = '/opt/coldfusion8/bin/cfstat'
			elif os.access('/opt/coldfusionmx7/bin/cfstat',os.X_OK):
				cfstat = '/opt/coldfusionmx7/bin/cfstat'
			else:
				self.checksLogger.error('ColdFusion: Could not find cfstat')
				return False
		else:
			cfstat = self.rawConfig['Main']['coldfusion_cfstat_path']
			if not os.access(cfstat,os.X_OK):
				self.checksLogger.error('ColdFusion: The location of cfstat given in config either does not exist or is not executable')
				return False

		# Run cfstat and collect its data
		self.checksLogger.debug('ColdFusion: Getting stats from ColdFusion')
		proc = subprocess.Popen([cfstat, '-x', '-n', '-s'], stdout=subprocess.PIPE, close_fds=True)
		stats = proc.communicate()[0]

		if int(pythonVersion[1]) >= 6:
			try:
				proc.kill()
			except Exception, e:
				self.checksLogger.debug('ColdFusion: cfstat process already terminated')

		stats = stats.split()
		if len(stats) == 26:
			keys = ["Pg/s Now", "Pg/s Hi", "DB/s Now", "DB/s Hi", "CP/s Now", "CP/s Hi", "Reqs Q'ed", "Reqs Run'g", "Reqs TO'ed", "Tpl Q'ed", "Tpl Run'g", "Tpl TO'ed", "Flash Q'ed", "Flash Run'g", "Flash TO'ed", "CFC Q'ed", "CFC Run'g", "CFC TO'ed", "WebSvc Q'ed", "WebSvc Run'g", "WebSvc TO'ed", "Avg Q Time", "Avg Req Time", "Avg DB Time", "Bytes In/s", "Bytes Out/s"]
		elif len(stats) == 14:
			keys = ["Pg/s Now", "Pg/s Hi", "DB/s Now", "DB/s Hi", "CP/s Now", "CP/s Hi", "Reqs Q'ed", "Reqs Run'g", "Reqs TO'ed", "Avg Q Time", "Avg Req Time", "Avg DB Time", "Bytes In/s", "Bytes Out/s"]
		else:
			self.checksLogger.error('ColdFusion: Received unexpected response from cfstat: ' + str(stats))
			return False

		data = dict(zip(keys, stats))
		return data
