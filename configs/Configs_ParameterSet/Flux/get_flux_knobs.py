def gen_dial_yaml():
    with open('flux_multisigma_knobs.txt', 'r') as file:
        for line in file:
            s = str(line.strip())
            print(f'- parameterName: \"{s}\"')
            print('  isEnabled: true')
            print('  dialSetDefinitions:')
            print('    - dialType: Spline')
            print('      minDialResponse: 0')
            print('      maxDialResponse: 10')
            print(f'      dialLeafName: \"{s}\"')
            print('      applyCondition: \"[is_nu]==1\"')

def get_syst_list():
    with open('flux_multisigma_knobs.txt', 'r') as file:
        for line in file:
            s = str(line.strip())
            print(f'\"{s}\",')


gen_dial_yaml()
#get_syst_list()
