# imports
#import toml

def get_syst_list(systs):
    for s in systs:
        #k = 'name'
        print(f'\"{s}\",')

def gen_dial_yaml(systs):
    for s in systs:
        #k = 'name'
        #print(f'- parameterName: \"{s[k]}\"')
        #print('  isEnabled: true')
        #print('  dialSetDefinitions:')
        #print('    - dialType: Spline')
        #print('      minimumSplineResponse: 0')
        #print(f'      dialLeafName: \"{s[k]}\"')
        #print('      applyCondition: \"[IsNu]==1\"')
        print(f'- parameterName: \"{s}\"')
        print('  isEnabled: true')
        print('  dialSetDefinitions:')
        print('    - dialType: Spline')
        print('      minimumSplineResponse: 0')
        print(f'      dialLeafName: \"{s}\"')
        print('      applyCondition: \"[is_nu]==1\"')
        
# load config
#config = toml.load('/exp/icarus/app/users/lkashur/SPINEAna/spine_anaplot_tools/systematics/configurations/pi0ana.toml')
#plot_config = toml.load('/exp/icarus/app/users/lkashur/medulla/medulla/spineplot/configurations/analyses/icarus/ccpi0ana_sel_categorytopology.toml')

# Detector systematics
det_systs = ['var01', 'var02', 'var03', 'var04', 'var05', 'var06', 'var07', 'var08', 'var09']
#get_syst_list(det_systs)
gen_dial_yaml(det_systs)



# OLD
# All systematics
#systematics = config['sys']

# Multisim systematics
#systematics_multisim = [s for s in systematics if s['type'] == 'multisim']

# Multisigma systematics
#systematics_multisigma = [s for s in systematics if s['type'] == 'multisigma']

# Detector systematics
#systematics_detector = [s for s in systematics if s['type'] == 'variation']

#get_syst_list(systematics_detector)
#gen_dial_yaml(systematics_detector)
