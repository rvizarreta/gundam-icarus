import os
import knoblist

knobNames = knoblist.GENIEMultisigmaKnobNames

for name in knobNames:

  IsEnabled = 'true'
  if 'MFP' in name or 'Fr' in name:
    IsEnabled = 'false'

  output = '''- parameterName: "GENIEReWeight_SBN_v1_multisigma_%s"
  isEnabled: %s
  dialSetDefinitions:
    - dialType: Spline
      minimumSplineResponse: 0
      dialLeafName: "GENIEReWeight_SBN_v1_multisigma_%s"
      applyCondition: "[is_nu]==1"
'''%(name, IsEnabled, name)
  print(output)

knobNames = knoblist.GENIEMorphKnobNames

for name in knobNames:
  output = '''- parameterName: "GENIEReWeight_SBN_v1_multisigma_%s"
  isEnabled: true
  dialSetDefinitions:
    - dialType: Spline
      minimumSplineResponse: 0
      dialLeafName: "GENIEReWeight_SBN_v1_multisigma_%s"
      useMirrorDial: true
      mirrorLowEdge: -1
      mirrorHighEdge: 1
      applyCondition: "[is_nu]==1"
'''%(name, name)
  print(output)
