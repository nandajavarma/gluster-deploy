
import yaml
from generator_modules.conf_parser import ConfigParseHelpers


class YamlWriter(ConfigParseHelpers):

    def __init__(self, bricks, config, filename, filetype):
        self.bricks = bricks
        self.config = config
        self.filename = filename
        self.filetype = filetype
        self.device_count = len(bricks)
        self.write_sections()

    def write_sections(self):
        sections = ['vgs', 'lvs', 'pools', 'mountpoints']
        section_names = ['Volume Group', 'Logical Volume',
                         'Logical Pool', 'Mount Point']
        self.section_dict = {'bricks': self.bricks}
        for section, section_name in zip(sections, section_names):
            self.section_dict[section] = self.section_data_gen(
                section,
                section_name)
        self.section_dict['lvols'] = ['/dev/%s/%s' % (i, j) for i, j in
                                      zip(self.section_dict['vgs'],
                                          self.section_dict['lvs'])]
        gluster_vol_conf_dict = self.gluster_vol_spec()
        performance_data_dict = self.perf_spec_data_write()
        listables_in_yaml = {key: self.section_dict[key]
                for key in ['vgs', 'bricks', 'mountpoints', 'lvols'] }
        self.yaml_list_data_write([listables_in_yaml, performance_data_dict,
                                    gluster_vol_conf_dict])
        self.yaml_dict_data_write()

    def insufficient_param_count(self, section, count):
        print "Error: Please provide %s names for %s devices " \
            "else leave the field empty" % (section, count)
        sys.exit(0)

    def get_options(self, section, required):
        if self.filetype == 'group_vars':
            return self.config_get_options(self.config, section, required)
        else:
            return self.config_section_map(
                self.config, self.filename.split('/')[-1], section,
                required)

    def section_data_gen(self, section, section_name):
        options = self.get_options(section, False)
        if options:
            options = filter(None, options.split(','))
            if len(options) < self.device_count:
                return self.insufficient_param_count(
                    section_name,
                    self.device_count)
        else:
            pattern = {'vgs': 'RHS_vg',
                       'pools': 'RHS_pool',
                       'lvs': 'RHS_lv',
                       'mountpoints': '/rhs/brick'
                       }[section]
            for i in range(1, self.device_count + 1):
                options.append(pattern + str(i))
        return options

    def yaml_list_data_write(self, list_data_dicts):
        for each in list_data_dicts:
            for key, value in each.iteritems():
                data = {}
                data[key] = value
                self.write_yaml(data, False)

    def create_yaml_dict(self, section, data):
        data_dict = {}
        data_dict[section] = data
        self.write_yaml(data_dict, True)

    def yaml_dict_data_write(self):
        vgnames, mntpaths, lvpools, pools = ([] for i in range(4))
        for i, vg in enumerate(self.section_dict['vgs']):
            vgnames.append({'brick': self.section_dict['bricks'][i], 'vg': vg})
            mntpaths.append({'path': self.section_dict['mountpoints'][i],
                'device': self.section_dict['lvols'][i]})
            lvpools.append({'pool': self.section_dict['pools'][i], 'vg': vg,
                'lv': self.section_dict['lvs'][i]})
            pools.append({'pool': self.section_dict['pools'][i], 'vg': vg})
        data_dict = {
            'vgnames': vgnames,
            'lvpools': lvpools,
            'mntpath': mntpaths,
            'pools': pools}
        for key, value in data_dict.iteritems():
            self.create_yaml_dict(key, value)

    def gluster_vol_spec(self):
        gluster = dict(clients=filter(None, self.config_section_map(
                self.config, 'clients', 'hosts',
                True).split(',')))
        gluster['client_mount_points'] = filter(None, self.config_section_map(
                self.config, 'clients', 'mount_points',
                False).split(','))
        if len(gluster['client_mount_points']):
            if len(gluster['client_mount_points']) != len(gluster['clients']):
                print "Error: Provide volume mount points in each client " \
                        "or a common mount point for all the clients. "
                sys.exit(0)
        else:
            gluster['client_mount_points'] = '/mnt/client'
        gluster['volname'] = self.config_get_options(self.config,
                'volname', False) or 'vol1'
        return gluster

    def perf_spec_data_write(self):
        disktype = self.config_get_options(self.config,
                                           'disktype', False)
        if disktype:
            perf = dict(disktype=disktype[0].lower())
        else:
            perf = dict(disktype='jbod')
        if perf['disktype'] not in ['raid10', 'raid6', 'jbod']:
            print "Error: Unsupported disk type!"
            sys.exit(0)
        if perf['disktype'] != 'jbod':
            perf['diskcount'] = int(
                self.config_get_options(self.config, 'diskcount', True)[0])
            stripe_size_necessary = {'raid10': False,
                                     'raid6': True
                                    }[perf['disktype']]
            stripe_size = self.config_get_options(self.config, 'stripesize',
                stripe_size_necessary)
            if stripe_size:
                perf['stripesize'] = int(stripe_size[0])
                if perf['disktype'] == 'raid10' and perf['stripesize'] != 256:
                    print "Warning: We recommend a stripe unit size of 256KB " \
                        "for RAID 10"
            else:
                perf['stripesize'] = 256
            perf['dalign'] = {
                'raid6': perf['stripesize'] * perf['diskcount'],
                'raid10': perf['stripesize'] * perf['diskcount']
                }[perf['disktype']]
        else:
            perf['dalign'] = 256
            perf['diskcount'] = perf['stripesize'] = 0
        perf['profile'] = self.config_get_options(self.config,
                'tune-profile', False) or 'rhs-high-throughput'
        return perf

    def write_yaml(self, data_dict, data_flow):
        with open(self.filename, 'a+') as outfile:
            if not data_flow:
                outfile.write(
                    yaml.dump(
                        data_dict,
                        default_flow_style=data_flow))
            else:
                outfile.write(yaml.dump(data_dict))