import configparser
import logging
import sys
import os
import uuid

log = logging.getLogger(__name__)

FILENAME_DEFAULT = 'default.cfg'
FILENAME_LOCAL = 'local.cfg'
FILENAME_DYNAMIC = 'dynamic.cfg' #need to add in dynamic.cfg in conf folder 
FILENAME_UUID = 'uuid.cfg' #need to add in uuid.cfg in conf folder 
CONF_DIR = os.path.join(sys.path[0], 'conf')

PATH_DEFAULT = os.path.join(CONF_DIR, FILENAME_DEFAULT)
PATH_LOCAL = os.path.join(CONF_DIR, FILENAME_LOCAL)
PATH_DYNAMIC = os.path.join(CONF_DIR, FILENAME_DYNAMIC)
PATH_UUID = os.path.join(CONF_DIR, FILENAME_UUID)


class Configurator():
    def __init__(self):
        self.static_conf = configparser.ConfigParser()

        # uuid

        try:
            with open(PATH_UUID) as uuid_file:
                self.static_conf.read_file(uuid_file)
            log.info("node uuid: %s" % self.static_conf.get('node', 'uuid'))
        except (IOError, configparser.NoOptionError, configparser.NoSectionError) as e:
            log.warning("No uuid set!")
            new_uuid = str(uuid.uuid1())
            log.warning("Setting new uuid: %s" % new_uuid)
            self.static_conf = configparser.ConfigParser()
            self.static_conf.add_section('node')
            self.static_conf.set('node', 'uuid', new_uuid)
            with open(PATH_UUID, 'w') as uuid_file:
                self.static_conf.write(uuid_file)

        self.static_conf.read(PATH_DEFAULT)
        log.info('reading configuration default.cfg')

        additionals = self.static_conf.read(PATH_LOCAL)
        for f in additionals:
            log.info('reading configuration %s' % f)

        self.dynamic_conf = configparser.ConfigParser()
        self.read_dynamic()

    def read_dynamic(self):
        dyn = self.dynamic_conf.read(PATH_DYNAMIC)
        for f in dyn:
            log.info('reading configuration %s' % f)

    def write_dynamic(self):
        with open(PATH_DYNAMIC, 'w') as f:
            self.dynamic_conf.write(f)

    def clear_dynamic(self):
        try:
            os.remove(PATH_DYNAMIC)
        except OSError:
            pass

        self.dynamic_conf = configparser.ConfigParser()
        self.read_dynamic()

    def get(self, section, option):
        try:
            return self.dynamic_conf.get(section, option)
        except configparser.NoOptionError:
            pass
        except configparser.NoSectionError:
            pass

        return self.static_conf.get(section, option)

    def getint(self, section, option):
        return int(self.get(section, option))

    def getfloat(self, section, option):
        return float(self.get(section, option))

    def getboolean(self, section, option):
        v = self.get(section, option)
        v_low = v.lower()
        if v_low in ["1", "yes", "true", "on"]:
            return True
        elif v_low in ["0", "no", "false", "off"]:
            return False
        else:
            raise ValueError("value '%s' (option '%s' section '%s') could not be parsed as boolean." % (v, option, section))

    def set(self, section, option, value):
        if not self.static_conf.has_section(section):
            raise configparser.NoSectionError(section)
        if not self.static_conf.has_option(section, option):
            raise configparser.NoOptionError(option, section)
        if not self.dynamic_conf.has_section(section):
            self.dynamic_conf.add_section(section)
        self.dynamic_conf.set(section, option, value)


cfg = Configurator()

if __name__ == "__main__":
    logging.basicConfig(level=1)
    cfg = Configurator()
    print(cfg.get('server', 'port'))
    cfg.set('server', 'port', '80')
    print(cfg.get('server', 'port'))
    cfg.write_dynamic()
    cfg.read_dynamic()
    print(cfg.get('server', 'port'))
    # print(cfg.static_conf.get('server','2p'))
